from datetime import date, datetime
from decimal import Decimal
import csv
import io
from flask import Response, stream_with_context, Blueprint, jsonify, make_response, request, send_file
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required
from sqlalchemy import or_
from .auth import roles_required
from .extensions import db
from .models import (
    Allocation,
    Announcement,
    Attendance,
    Complaint,
    Expense,
    ExpenseHistory,
    Floor,
    HostelSetting,
    LeaveRequest,
    MonthlyInvoice,
    Notification,
    OutingRequest,
    Payment,
    Room,
    RoomSlot,
    Student,
    User,
    Visitor,
)
from .services import (
    allocate_student,
    create_monthly_invoice,
    dashboard_summary,
    generate_receipt_no,
    generate_student_code,
    log_action,
    money,
    refresh_invoice,
    format_timestamp,
    serialize_room,
    serialize_student,
    serialize_student_brief,
    student_balance,
)
import json
import time
from uuid import uuid4

api = Blueprint("api", __name__)


def body():
    return request.get_json(silent=True) or {}


def parse_datetime(value, fallback=None):
    if not value:
        return fallback
    for pattern in ("%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, pattern)
        except ValueError:
            continue
    raise ValueError("Invalid datetime; expected YYYY-MM-DD HH:mm:ss")


def parse_date(value, fallback=None):
    parsed = parse_datetime(value, fallback)
    return parsed.date() if isinstance(parsed, datetime) else parsed


def current_user_id():
    identity = get_jwt_identity()
    return int(identity) if identity else None


@api.post("/auth/login")
def login():
    data = body()
    user = User.query.filter_by(email=data.get("email", "").lower().strip()).first()
    if not user or not user.is_active or not user.check_password(data.get("password", "")):
        return jsonify({"error": "Invalid credentials"}), 401
    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role, "name": user.name})
    return {"access_token": token, "user": {"id": user.id, "name": user.name, "email": user.email, "role": user.role, "student_id": user.student_id}}


@api.post("/auth/student-login")
def student_login():
    data = body()
    identifier = data.get("identifier", "").strip()
    student = Student.query.filter((Student.student_code == identifier) | (Student.phone == identifier) | (Student.email == identifier.lower())).first()
    if not student:
        return jsonify({"error": "Invalid credentials"}), 401
    user = User.query.filter_by(student_id=student.id, role="student").first()
    if not user or not user.is_active or not user.check_password(data.get("password", "")):
        return jsonify({"error": "Invalid credentials"}), 401
    token = create_access_token(identity=str(user.id), additional_claims={"role": "student", "name": student.full_name})
    return {"access_token": token, "user": {"id": user.id, "name": student.full_name, "role": "student", "student_id": student.id}}


@api.get("/me")
@jwt_required()
def me():
    user = User.query.get_or_404(current_user_id())
    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role, "student_id": user.student_id}


@api.get("/settings")
@jwt_required()
def settings():
    setting = HostelSetting.query.first()
    return {
        "hostel_name": setting.hostel_name,
        "phone": setting.phone,
        "address": setting.address,
        "currency": setting.currency,
        "default_monthly_rent": float(setting.default_monthly_rent),
        "default_deposit": float(setting.default_deposit),
        "monthly_due_day": setting.monthly_due_day,
        "receipt_prefix": setting.receipt_prefix,
    }


@api.put("/settings")
@roles_required("owner")
def update_settings():
    setting = HostelSetting.query.first()
    data = body()
    for field in ["hostel_name", "phone", "address", "currency", "monthly_due_day", "receipt_prefix"]:
        if field in data:
            setattr(setting, field, data[field])
    for field in ["default_monthly_rent", "default_deposit", "late_fee"]:
        if field in data:
            setattr(setting, field, money(data[field]))
    log_action(current_user_id(), "Updated hostel settings", request.remote_addr)
    db.session.commit()
    return settings()


@api.get("/dashboard")
@jwt_required()
def dashboard():
    month = request.args.get("month") or date.today().strftime("%Y-%m")
    rooms = Room.query.order_by(Room.number).all()
    return {"summary": dashboard_summary(month), "rooms": [serialize_room(room) for room in rooms], "outing_summary": outing_summary()}


@api.get("/rooms")
@jwt_required()
def rooms():
    floors = Floor.query.order_by(Floor.number).all()
    return {"floors": [{"id": f.id, "number": f.number, "name": f.name, "rooms": [serialize_room(r) for r in sorted(f.rooms, key=lambda r: r.number)]} for f in floors]}


@api.post("/rooms")
@roles_required("owner", "staff")
def create_room():
    data = body()
    floor = Floor.query.filter_by(number=int(data["floor"])).first()
    if not floor:
        floor = Floor(number=int(data["floor"]), name=f"Floor {data['floor']}")
        db.session.add(floor)
        db.session.flush()
    room = Room(
        floor_id=floor.id,
        number=str(data["number"]),
        capacity=int(data.get("capacity", int(data.get("bedroom_capacity", 4)) + int(data.get("hall_capacity", 3)))),
        bedroom_capacity=int(data.get("bedroom_capacity", 4)),
        hall_capacity=int(data.get("hall_capacity", 3)),
    )
    db.session.add(room)
    db.session.flush()
    for index in range(1, room.bedroom_capacity + 1):
        db.session.add(RoomSlot(room_id=room.id, code=f"B{index}", area="Bedroom"))
    for index in range(1, room.hall_capacity + 1):
        db.session.add(RoomSlot(room_id=room.id, code=f"H{index}", area="Hall"))
    log_action(current_user_id(), f"Created room {room.number}", request.remote_addr)
    db.session.commit()
    return serialize_room(room, include_slots=True), 201


@api.get("/rooms/<int:room_id>")
@jwt_required()
def room_detail(room_id):
    return serialize_room(Room.query.get_or_404(room_id), include_slots=True)


@api.put("/rooms/<int:room_id>")
@roles_required("owner", "staff")
def update_room(room_id):
    room = Room.query.get_or_404(room_id)
    data = body()
    if "is_active" in data:
        room.is_active = bool(data["is_active"])
    slots = RoomSlot.query.filter_by(room_id=room.id).all()
    occupied = {a.slot_id for a in Allocation.query.filter_by(status="Active", end_date=None).all()}
    targets = {}
    try:
        for area, key in [("Bedroom", "bedroom_capacity"), ("Hall", "hall_capacity")]:
            value = data.get(key, sum(s.is_active for s in slots if s.area == area))
            if isinstance(value, bool) or str(value) != str(int(value)):
                raise ValueError()
            targets[area] = int(value)
        if "capacity" in data and int(data["capacity"]) != sum(targets.values()):
            return {"error": "Total capacity must equal bedroom and hall beds"}, 400
    except (ValueError, TypeError):
        return {"error": "Capacity must be a whole number"}, 400
    for area, target in targets.items():
        if target < 0 or target < sum(s.id in occupied for s in slots if s.area == area):
            return {"error": f"Cannot reduce {area} capacity below occupied beds or zero"}, 400
    for area, target in targets.items():
        active = [s for s in slots if s.area == area and s.is_active]
        if target < len(active):
            vacant = [s for s in reversed(active) if s.id not in occupied]
            for slot in vacant[:len(active) - target]:
                slot.is_active = False
        else:
            inactive = [s for s in slots if s.area == area and not s.is_active]
            for index in range(target - len(active)):
                if index < len(inactive):
                    inactive[index].is_active = True
                else:
                    prefix = "B" if area == "Bedroom" else "H"
                    number = max([int(s.code[1:]) for s in slots if s.area == area] or [0]) + 1
                    slot = RoomSlot(room_id=room.id, code=f"{prefix}{number}", area=area)
                    slots.append(slot)
                    db.session.add(slot)
    room.bedroom_capacity = targets["Bedroom"]
    room.hall_capacity = targets["Hall"]
    room.capacity = sum(targets.values())
    log_action(current_user_id(), f"Updated room {room.number}", request.remote_addr)
    db.session.commit()
    return serialize_room(room, include_slots=True)


@api.get("/students")
@jwt_required()
def students():
    query = Student.query
    search = request.args.get("search")
    if search:
        like = f"%{search}%"
        query = query.filter(or_(Student.full_name.ilike(like), Student.student_code.ilike(like), Student.phone.ilike(like), Student.college_name.ilike(like), Student.roll_number.ilike(like)))
    status = request.args.get("status")
    if status and status != "All":
        query = query.filter_by(status=status)
    elif not status:
        query = query.filter_by(status="Active")
    return {"students": [serialize_student_brief(s) for s in query.order_by(Student.created_at.desc()).all()]}


@api.post("/students")
@roles_required("owner", "staff")
def create_student():
    data = body()
    setting = HostelSetting.query.first()
    student = Student(
        student_code=generate_student_code(),
        full_name=data["full_name"],
        phone=data["phone"],
        email=data.get("email"),
        college_name=data.get("college_name"),
        course=data.get("course"),
        branch=data.get("branch"),
        year=data.get("year"),
        roll_number=data.get("roll_number"),
        joining_date=parse_datetime(data.get("joining_date"), datetime.utcnow()),
        monthly_rent=money(data.get("monthly_rent", setting.default_monthly_rent)),
        deposit=money(data.get("deposit", setting.default_deposit)),
        advance=money(data.get("advance", 0)),
        payment_due_day=int(data.get("payment_due_day", setting.monthly_due_day)),
        guardian_name=data.get("guardian_name"),
        guardian_relation=data.get("guardian_relation"),
        guardian_phone=data.get("guardian_phone"),
        address=data.get("address"),
    )
    db.session.add(student)
    db.session.flush()
    if data.get("password"):
        student_user = User(name=student.full_name, email=f"{student.student_code.lower()}@student.jtbh.local", role="student", student_id=student.id)
        student_user.set_password(data["password"])
        db.session.add(student_user)
    if data.get("slot_id"):
        try:
            allocate_student(student, int(data["slot_id"]))
        except ValueError as error:
            db.session.rollback()
            return {"error": str(error)}, 400
    create_monthly_invoice(student)
    log_action(current_user_id(), f"Added student {student.student_code}", request.remote_addr)
    db.session.commit()
    return serialize_student(student), 201


@api.post("/students/<int:student_id>/remove")
@roles_required("owner", "staff")
def remove_student(student_id):
    student = Student.query.get_or_404(student_id)
    data = body()
    allocation = Allocation.query.filter_by(student_id=student.id, status="Active", end_date=None).first()
    if allocation:
        allocation.status = "Removed"
        allocation.end_date = date.today()
    student.status = "Removed"
    student.removed_at = datetime.utcnow()
    student.removed_by_id = current_user_id()
    student.removal_reason = data.get("reason")
    user = User.query.filter_by(student_id=student.id, role="student").first()
    if user:
        user.is_active = False
    log_action(current_user_id(), f"Removed student {student.student_code}", request.remote_addr)
    db.session.commit()
    return serialize_student(student)


@api.post("/students/<int:student_id>/restore")
@roles_required("owner")
def restore_student(student_id):
    student = Student.query.get_or_404(student_id)
    student.status = "Active"
    student.restored_at = datetime.utcnow()
    user = User.query.filter_by(student_id=student.id, role="student").first()
    if user:
        user.is_active = True
    log_action(current_user_id(), f"Restored student {student.student_code}", request.remote_addr)
    db.session.commit()
    return serialize_student(student)


@api.delete("/students/<int:student_id>/unallocated")
@roles_required("owner", "staff")
def delete_unallocated_student(student_id):
    student = Student.query.get_or_404(student_id)
    active_allocation = Allocation.query.filter_by(student_id=student.id, status="Active", end_date=None).first()
    if active_allocation:
        return {"error": "Students with an allocated room cannot be deleted"}, 400
    for user in User.query.filter_by(student_id=student.id).all():
        db.session.delete(user)
    for payment in Payment.query.filter_by(student_id=student.id).all():
        db.session.delete(payment)
    for invoice in MonthlyInvoice.query.filter_by(student_id=student.id).all():
        for item in invoice.items:
            db.session.delete(item)
        db.session.delete(invoice)
    for model in [Complaint, Attendance, LeaveRequest, OutingRequest, Visitor, Allocation]:
        for record in model.query.filter_by(student_id=student.id).all():
            db.session.delete(record)
    log_action(current_user_id(), f"Deleted unallocated student {student.student_code}", request.remote_addr)
    db.session.delete(student)
    db.session.commit()
    return {"deleted": True, "student_id": student_id}


@api.get("/students/<int:student_id>")
@jwt_required()
def student_detail(student_id):
    student = Student.query.get_or_404(student_id)
    user = User.query.get_or_404(current_user_id())
    if user.role == "student" and user.student_id != student_id:
        return {"error": "Forbidden"}, 403
    return {
        "student": serialize_student(student),
        "invoices": [serialize_invoice(i) for i in student.invoices],
        "payments": [serialize_payment(p) for p in student.payments],
        "allocations": [serialize_allocation(a) for a in student.allocations],
    }


@api.put("/students/<int:student_id>")
@roles_required("owner", "staff")
def update_student(student_id):
    student = Student.query.get_or_404(student_id)
    data = body()
    allowed = ["full_name", "phone", "email", "college_name", "course", "branch", "year", "roll_number", "status", "guardian_name", "guardian_phone", "address"]
    for field in allowed:
        if field in data:
            setattr(student, field, data[field])
    for field in ["monthly_rent", "deposit", "advance"]:
        if field in data:
            setattr(student, field, money(data[field]))
    if "joining_date" in data:
        student.joining_date = parse_datetime(data["joining_date"], student.joining_date)
    log_action(current_user_id(), f"Updated student {student.student_code}", request.remote_addr)
    db.session.commit()
    return serialize_student(student)


@api.post("/students/<int:student_id>/transfer")
@roles_required("owner", "staff")
def transfer_student(student_id):
    student = Student.query.get_or_404(student_id)
    data = body()
    old = Allocation.query.filter_by(student_id=student.id, status="Active", end_date=None).first()
    if old:
        old.status = "Transferred"
        old.end_date = date.today()
    try:
        allocate_student(student, int(data["slot_id"]))
    except ValueError as error:
        db.session.rollback()
        return {"error": str(error)}, 400
    log_action(current_user_id(), f"Transferred student {student.student_code}", request.remote_addr)
    db.session.commit()
    return serialize_student(student)


@api.post("/students/<int:student_id>/checkout")
@roles_required("owner", "staff")
def checkout_student(student_id):
    student = Student.query.get_or_404(student_id)
    data = body()
    allocation = Allocation.query.filter_by(student_id=student.id, status="Active", end_date=None).first()
    if allocation:
        allocation.status = "Checked Out"
        allocation.end_date = parse_date(data.get("checkout_date"), date.today())
    student.status = "Checked Out"
    log_action(current_user_id(), f"Checked out student {student.student_code}", request.remote_addr)
    db.session.commit()
    return serialize_student(student)


@api.get("/available-slots")
@jwt_required()
def available_slots():
    occupied = {a.slot_id for a in Allocation.query.filter_by(status="Active", end_date=None).all()}
    slots = RoomSlot.query.join(Room).join(Floor).filter(RoomSlot.is_active == True, Room.is_active == True).order_by(Floor.number, Room.number, RoomSlot.code).all()
    return {"slots": [{"id": s.id, "floor": s.room.floor.number, "room": s.room.number, "code": s.code, "area": s.area} for s in slots if s.id not in occupied]}


def serialize_invoice(invoice):
    refresh_invoice(invoice)
    return {
        "id": invoice.id,
        "student_id": invoice.student_id,
        "student": invoice.student.full_name,
        "student_code": invoice.student.student_code,
        "phone": invoice.student.phone,
        "room": serialize_student_brief(invoice.student)["room"],
        "month": invoice.month,
        "due_date": invoice.due_date.isoformat(),
        "total_amount": float(invoice.total_amount),
        "amount_paid": float(invoice.amount_paid),
        "balance": float(money(invoice.total_amount) - money(invoice.amount_paid)),
        "status": invoice.status,
    }


@api.get("/invoices")
@jwt_required()
def invoices():
    month = request.args.get("month")
    query = MonthlyInvoice.query
    if month:
        query = query.filter_by(month=month)
    invoices_list = query.order_by(MonthlyInvoice.due_date.desc()).all()
    db.session.commit()
    return {"invoices": [serialize_invoice(i) for i in invoices_list]}


@api.post("/invoices/generate")
@roles_required("owner", "staff")
def generate_invoices():
    month = body().get("month") or date.today().strftime("%Y-%m")
    count = 0
    for student in Student.query.filter_by(status="Active").all():
        create_monthly_invoice(student, month)
        count += 1
    log_action(current_user_id(), f"Generated invoices for {month}", request.remote_addr)
    db.session.commit()
    return {"created_or_refreshed": count, "month": month}


@api.post("/payments")
@roles_required("owner", "staff")
def record_payment():
    data = body()
    student = Student.query.get_or_404(int(data["student_id"]))
    invoice = MonthlyInvoice.query.get(int(data["invoice_id"])) if data.get("invoice_id") else None
    if not invoice:
        invoice = create_monthly_invoice(student, data.get("month"))
        db.session.flush()
    payment = Payment(
        student_id=student.id,
        invoice_id=invoice.id,
        amount=money(data["amount"]),
        payment_date=parse_datetime(data.get("payment_date"), datetime.utcnow()),
        method=data.get("method", "Cash"),
        transaction_id=data.get("transaction_id"),
        notes=data.get("notes"),
        receipt_no=generate_receipt_no(),
        received_by_id=current_user_id(),
    )
    db.session.add(payment)
    db.session.flush()
    refresh_invoice(invoice)
    log_action(current_user_id(), f"Recorded payment {payment.receipt_no}", request.remote_addr)
    db.session.commit()
    return serialize_payment(payment), 201


def serialize_payment(payment):
    return {
        "id": payment.id,
        "receipt_no": payment.receipt_no,
        "student": payment.student.full_name,
        "student_id": payment.student_id,
        "invoice_id": payment.invoice_id,
        "purpose": f"Monthly Rent - {payment.invoice.month}" if payment.invoice else "Hostel Fee",
        "amount": float(payment.amount),
        "created_at": format_timestamp(payment.created_at),
        "payment_date": format_timestamp(payment.payment_date),
        "method": payment.method,
        "transaction_id": payment.transaction_id,
        "is_cancelled": payment.is_cancelled,
    }


@api.get("/payments")
@jwt_required()
def payments():
    user = User.query.get_or_404(current_user_id())
    query = Payment.query.filter_by(student_id=user.student_id) if user.role == "student" else Payment.query
    return {"payments": [serialize_payment(p) for p in query.order_by(Payment.payment_date.desc()).all()]}


@api.get("/payments/<int:payment_id>/receipt.pdf")
@jwt_required()
def payment_receipt(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    user = User.query.get_or_404(current_user_id())
    if user.role == "student" and payment.student_id != user.student_id:
        return {"error": "Forbidden"}, 403
    if payment.is_cancelled:
        return {"error": "Cancelled payments have no valid receipt"}, 400
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    output = io.BytesIO()
    document = canvas.Canvas(output, pagesize=A4)
    document.setTitle(f"Payment Receipt {payment.receipt_no}")
    document.drawString(72, 780, "Jai Tulja Bhavani Deluxe Boys Hostel")
    document.drawString(72, 750, f"Receipt: {payment.receipt_no}")
    document.drawString(72, 730, f"Student: {payment.student.full_name}")
    document.drawString(72, 710, f"Amount: INR {payment.amount}")
    document.drawString(72, 690, f"Payment timestamp: {format_timestamp(payment.payment_date)}")
    document.drawString(72, 670, f"Created timestamp: {format_timestamp(payment.created_at)}")
    document.drawString(72, 650, f"Method: {payment.method}")
    document.save()
    output.seek(0)
    return send_file(output, mimetype="application/pdf", as_attachment=True, download_name=f"{payment.receipt_no}.pdf")


@api.get("/reports/export.csv")
@jwt_required()
def export_report_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Record Type", "Record ID", "Created At", "Business Timestamp", "Name", "Category/Method", "Amount"])
    for student in Student.query.order_by(Student.created_at.desc()).all():
        writer.writerow(["Student", student.id, format_timestamp(student.created_at), format_timestamp(student.joining_date), student.full_name, "", ""])
    for payment in Payment.query.order_by(Payment.payment_date.desc()).all():
        writer.writerow(["Payment", payment.id, format_timestamp(payment.created_at), format_timestamp(payment.payment_date), payment.student.full_name, payment.method, payment.amount])
    for expense in Expense.query.order_by(Expense.expense_date.desc()).all():
        writer.writerow(["Expense", expense.id, format_timestamp(expense.created_at), format_timestamp(expense.expense_date), "", expense.category, expense.amount])
    response = make_response(output.getvalue())
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = "attachment; filename=jtbh-financial-report.csv"
    return response


@api.get("/dues")
@jwt_required()
def dues():
    invoices_list = MonthlyInvoice.query.order_by(MonthlyInvoice.due_date.asc()).all()
    db.session.commit()
    return {"dues": [serialize_invoice(i) for i in invoices_list if Decimal(str(i.total_amount)) > Decimal(str(i.amount_paid))]}


@api.post("/expenses")
@roles_required("owner", "staff")
def create_expense():
    data = body()
    expense = Expense(
        expense_date=parse_datetime(data.get("expense_date"), datetime.utcnow()),
        category=data["category"],
        amount=money(data["amount"]),
        description=data.get("description"),
        payment_method=data.get("payment_method", "Cash"),
        entered_by_id=current_user_id(),
    )
    db.session.add(expense)
    log_action(current_user_id(), f"Added expense {expense.category}", request.remote_addr)
    db.session.commit()
    return serialize_expense(expense), 201


def serialize_expense(expense):
    return {"id": expense.id, "created_at": format_timestamp(expense.created_at), "expense_date": format_timestamp(expense.expense_date), "category": expense.category, "amount": float(expense.amount), "description": expense.description, "payment_method": expense.payment_method, "notes": expense.notes, "bill_path": expense.bill_path, "is_deleted": expense.is_deleted, "deleted_at": format_timestamp(expense.deleted_at)}


@api.get("/expenses")
@jwt_required()
def expenses():
    include_deleted = request.args.get("include_deleted") == "1"
    query = Expense.query if include_deleted else Expense.query.filter_by(is_deleted=False)
    return {"expenses": [serialize_expense(e) for e in query.order_by(Expense.expense_date.desc()).all()]}


def expense_snapshot(expense):
    return json.dumps(serialize_expense(expense), sort_keys=True)


@api.put("/expenses/<int:expense_id>")
@roles_required("owner", "staff")
def update_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    if expense.is_deleted:
        return {"error": "Deleted expenses cannot be edited"}, 400
    db.session.add(ExpenseHistory(expense_id=expense.id, action="edit", snapshot=expense_snapshot(expense), user_id=current_user_id()))
    data = body()
    for field in ["category", "description", "payment_method", "notes", "bill_path"]:
        if field in data:
            setattr(expense, field, data[field])
    if "expense_date" in data:
        expense.expense_date = parse_datetime(data["expense_date"], expense.expense_date)
    if "amount" in data:
        expense.amount = money(data["amount"])
    expense.edited_by_id = current_user_id()
    expense.edited_at = datetime.utcnow()
    log_action(current_user_id(), f"Edited expense {expense.id}", request.remote_addr)
    db.session.commit()
    return serialize_expense(expense)


@api.delete("/expenses/<int:expense_id>")
@roles_required("owner", "staff")
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    db.session.add(ExpenseHistory(expense_id=expense.id, action="delete", snapshot=expense_snapshot(expense), user_id=current_user_id()))
    expense.is_deleted = True
    expense.deleted_by_id = current_user_id()
    expense.deleted_at = datetime.utcnow()
    expense.deletion_reason = body().get("reason")
    log_action(current_user_id(), f"Deleted expense {expense.id}", request.remote_addr)
    db.session.commit()
    return serialize_expense(expense)


def complaint_items(user):
    query = Complaint.query
    if user.role == "student":
        query = query.filter_by(student_id=user.student_id)
    return [serialize_complaint(c) for c in query.order_by(Complaint.created_at.desc(), Complaint.id.desc()).all()]


@api.post("/complaints")
@roles_required("student")
def create_complaint():
    data = body()
    user = User.query.get_or_404(current_user_id())
    # Accept ``title`` as well as the UI's more familiar ``subject`` field.
    subject = data.get("subject") or data.get("title")
    if any(not isinstance(value, str) or not value.strip() for value in [subject, data.get("description")]):
        return {"error": "Subject and description are required"}, 400
    complaint = Complaint(
        complaint_no=f"JTBH-CMP-{uuid4().hex[:20]}",
        student_id=user.student_id,
        title=subject.strip(), subject=subject.strip(),
        category=str(data.get("category") or "General").strip(),
        description=data["description"].strip(), status="PENDING",
    )
    db.session.add(complaint)
    db.session.add(Notification(message=f"New complaint: {complaint.title[:180]}", kind="complaint"))
    db.session.commit()
    return serialize_complaint(complaint), 201


def serialize_complaint(complaint):
    return {"id": complaint.id, "complaint_no": complaint.complaint_no,
            "student": complaint.student.full_name if complaint.student else None,
            "room": serialize_student_brief(complaint.student)["room"] if complaint.student else None,
            "title": complaint.title or complaint.subject or complaint.category,
            "subject": complaint.title or complaint.subject or complaint.category,
            "category": complaint.category, "description": complaint.description,
            "created_at": format_timestamp(complaint.created_at),
            "status": {"OPEN": "PENDING", "Pending": "PENDING", "In Progress": "IN_PROGRESS", "Resolved": "RESOLVED"}.get(complaint.status, complaint.status)}


@api.get("/complaints")
@roles_required("student")
def complaints():
    return {"complaints": complaint_items(User.query.get_or_404(current_user_id()))}


@api.get("/admin/complaints")
@roles_required("owner", "staff")
def admin_complaints():
    return {"complaints": complaint_items(User.query.get_or_404(current_user_id()))}


@api.route("/admin/complaints/<int:complaint_id>", methods=["PUT", "PATCH"])
@roles_required("owner", "staff")
def update_admin_complaint(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    status = str(body().get("status", "")).upper()
    if status not in ["PENDING", "IN_PROGRESS", "RESOLVED"]:
        return {"error": "Invalid complaint status"}, 400
    complaint.status = status
    complaint.resolved_at = datetime.utcnow() if status == "RESOLVED" else None
    db.session.commit()
    return serialize_complaint(complaint)


@api.get("/complaints/stream")
@jwt_required()
def complaint_stream():
    user_id = current_user_id()
    expires = get_jwt()["exp"]
    @stream_with_context
    def events():
        previous = None
        while time.time() < expires:
            user = db.session.get(User, user_id)
            if not user or not user.is_active:
                break
            payload = json.dumps({"complaints": complaint_items(user)})
            db.session.remove()
            if payload != previous:
                yield f"data: {payload}\n\n"
                previous = payload
            else:
                yield ": heartbeat\n\n"
            time.sleep(0.5)
    return Response(events(), mimetype="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@api.get("/student/dashboard")
@roles_required("student")
def student_dashboard():
    user = User.query.get_or_404(current_user_id())
    student = Student.query.get_or_404(user.student_id)
    invoices_list = [serialize_invoice(i) for i in student.invoices]
    latest = invoices_list[-1] if invoices_list else None
    return {"student": serialize_student(student), "latest_invoice": latest, "invoices": invoices_list, "payments": [serialize_payment(p) for p in student.payments], "complaints": [serialize_complaint(c) for c in student.complaints], "outings": [serialize_outing(o) for o in student.outing_requests], "leaves": [serialize_leave(l) for l in student.leave_requests], "announcements": [serialize_announcement(a) for a in Announcement.query.filter_by(is_active=True).order_by(Announcement.created_at.desc()).all()]}


@api.put("/student/profile")
@roles_required("student")
def update_student_profile():
    user = User.query.get_or_404(current_user_id())
    student = Student.query.get_or_404(user.student_id)
    data = body()
    for field in ["phone", "email"]:
        if field in data:
            setattr(student, field, data[field])
    log_action(user.id, f"Student updated profile {student.student_code}", request.remote_addr)
    db.session.commit()
    return serialize_student(student)


@api.post("/outings")
@jwt_required()
def create_outing():
    data = body()
    user = User.query.get_or_404(current_user_id())
    student_id = user.student_id if user.role == "student" else data.get("student_id")
    if not student_id:
        return {"error": "student_id is required"}, 400
    student = Student.query.get_or_404(student_id)
    outing = OutingRequest(
        student_id=student_id,
        outing_date=parse_date(data.get("outing_date"), date.today()),
        leaving_time=data["leaving_time"],
        expected_return_time=data["expected_return_time"],
        destination=data["destination"],
        reason=data["reason"],
        emergency_contact=data.get("emergency_contact"),
        notes=data.get("notes"),
    )
    db.session.add(outing)
    db.session.add(Notification(message=f"New outing request from {student.full_name}", kind="outing"))
    log_action(current_user_id(), "Created outing request", request.remote_addr)
    db.session.commit()
    return serialize_outing(outing), 201


@api.get("/outings")
@jwt_required()
def outings():
    items = OutingRequest.query.order_by(OutingRequest.outing_date.desc(), OutingRequest.created_at.desc()).all()
    return {"outings": [serialize_outing(o) for o in items], "summary": outing_summary()}


@api.post("/outings/<int:outing_id>/<action>")
@roles_required("owner", "staff")
def outing_action(outing_id, action):
    outing = OutingRequest.query.get_or_404(outing_id)
    transitions = {"approve": "Approved", "reject": "Rejected", "out": "Currently Out", "returned": "Returned"}
    if action not in transitions:
        return {"error": "Invalid action"}, 400
    allowed = {"approve": ["Pending"], "reject": ["Pending"], "out": ["Approved"], "returned": ["Out", "Currently Out", "Late"]}
    if outing.status not in allowed[action]:
        return {"error": "Invalid movement transition"}, 409
    outing.status = transitions[action]
    outing.decided_by_id = current_user_id()
    outing.decided_at = datetime.utcnow()
    if action == "out":
        outing.actual_leaving_time = datetime.utcnow()
    if action == "returned":
        outing.actual_return_time = datetime.utcnow()
    db.session.add(Notification(message=f"Your outing request is {outing.status}", kind="outing"))
    log_action(current_user_id(), f"Marked outing {outing.id} {outing.status}", request.remote_addr)
    db.session.commit()
    return serialize_outing(outing)


@api.post("/leaves")
@jwt_required()
def create_leave():
    data = body()
    user = User.query.get_or_404(current_user_id())
    student_id = user.student_id if user.role == "student" else data.get("student_id")
    leave = LeaveRequest(student_id=student_id, from_date=parse_date(data["from_date"]), to_date=parse_date(data["to_date"]), reason=data["reason"], destination=data.get("destination"), emergency_contact=data.get("emergency_contact"))
    db.session.add(leave)
    log_action(current_user_id(), "Created leave request", request.remote_addr)
    db.session.commit()
    return serialize_leave(leave), 201


@api.get("/leaves")
@jwt_required()
def leaves():
    return {"leaves": [serialize_leave(l) for l in LeaveRequest.query.order_by(LeaveRequest.created_at.desc()).all()]}


@api.post("/announcements")
@roles_required("owner", "staff")
def create_announcement():
    data = body()
    announcement = Announcement(title=data["title"], message=data["message"], target_type=data.get("target_type", "Everyone"), target_value=data.get("target_value"))
    db.session.add(announcement)
    db.session.add(Notification(message="New hostel announcement", kind="announcement"))
    db.session.commit()
    return serialize_announcement(announcement), 201


@api.get("/announcements")
@jwt_required()
def announcements():
    return {"announcements": [serialize_announcement(a) for a in Announcement.query.filter_by(is_active=True).order_by(Announcement.created_at.desc()).all()]}


def serialize_allocation(allocation):
    return {"id": allocation.id, "room": allocation.slot.room.number, "floor": allocation.slot.room.floor.number, "slot": allocation.slot.code, "area": allocation.slot.area, "start_date": allocation.start_date.isoformat(), "end_date": allocation.end_date.isoformat() if allocation.end_date else None, "status": allocation.status}


@api.get("/reports/summary")
@jwt_required()
def reports_summary():
    month = request.args.get("month") or date.today().strftime("%Y-%m")
    return {"summary": dashboard_summary(month), "students": [serialize_student_brief(s) for s in Student.query.all()], "rooms": [serialize_room(r) for r in Room.query.all()]}


def outing_summary():
    today = date.today()
    outings_today = OutingRequest.query.filter_by(outing_date=today).all()
    return {
        "total": len(outings_today),
        "approved": len([o for o in outings_today if o.status == "Approved"]),
        "currently_out": len([o for o in outings_today if o.status in ["Out", "Currently Out"]]),
        "returned": len([o for o in outings_today if o.status == "Returned"]),
        "late": len([o for o in outings_today if o.status == "Late"]),
    }


def serialize_outing(outing):
    brief = serialize_student_brief(outing.student)
    return {"id": outing.id, "student": outing.student.full_name, "student_id": outing.student_id, "room": brief["room"], "phone": outing.student.phone, "outing_date": outing.outing_date.isoformat(), "leaving_time": outing.leaving_time, "expected_return_time": outing.expected_return_time, "destination": outing.destination, "reason": outing.reason, "emergency_contact": outing.emergency_contact, "notes": outing.notes, "status": "Currently Out" if outing.status == "Out" else outing.status, "actual_leaving_time": outing.actual_leaving_time.isoformat() if outing.actual_leaving_time else None, "actual_return_time": outing.actual_return_time.isoformat() if outing.actual_return_time else None}


def serialize_leave(leave):
    return {"id": leave.id, "student": leave.student.full_name, "student_id": leave.student_id, "from_date": leave.from_date.isoformat(), "to_date": leave.to_date.isoformat(), "reason": leave.reason, "destination": leave.destination, "emergency_contact": leave.emergency_contact, "status": leave.status}


def serialize_announcement(announcement):
    return {"id": announcement.id, "title": announcement.title, "message": announcement.message, "target_type": announcement.target_type, "target_value": announcement.target_value, "created_at": announcement.created_at.isoformat()}
