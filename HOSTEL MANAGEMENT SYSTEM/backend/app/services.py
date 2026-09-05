from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import func
from .extensions import db
from .models import (
    Allocation,
    AuditLog,
    Expense,
    Floor,
    HostelSetting,
    MonthlyInvoice,
    Payment,
    Room,
    RoomSlot,
    Student,
)


def money(value):
    return Decimal(str(value or 0)).quantize(Decimal("0.01"))


def format_timestamp(value):
    return value.strftime("%Y-%m-%d %H:%M:%S") if value else None


def active_allocation_query():
    return Allocation.query.filter_by(status="Active", end_date=None)


def occupied_slot_ids():
    return {row.slot_id for row in active_allocation_query().with_entities(Allocation.slot_id).all()}


def generate_student_code():
    year = date.today().year
    prefix = f"JTBH{year}"
    last = (
        Student.query.filter(Student.student_code.like(f"{prefix}%"))
        .order_by(Student.student_code.desc())
        .first()
    )
    serial = int(last.student_code[-3:]) + 1 if last else 1
    return f"{prefix}{serial:03d}"


def generate_receipt_no():
    year = date.today().year
    prefix = f"JTBH-REC-{year}"
    last = Payment.query.filter(Payment.receipt_no.like(f"{prefix}%")).order_by(Payment.receipt_no.desc()).first()
    serial = int(last.receipt_no.split("-")[-1]) + 1 if last else 1
    return f"{prefix}-{serial:04d}"


def calculate_invoice_status(invoice):
    total = money(invoice.total_amount)
    paid = money(invoice.amount_paid)
    balance = total - paid
    if paid >= total and total > 0:
        return "PAID"
    if paid > 0 and paid < total:
        return "PARTIAL" if date.today() <= invoice.due_date else "OVERDUE"
    if paid > total:
        return "ADVANCE"
    return "PENDING" if date.today() <= invoice.due_date else "OVERDUE"


def refresh_invoice(invoice):
    invoice.amount_paid = money(sum(payment.amount for payment in invoice.payments if not payment.is_cancelled))
    invoice.status = calculate_invoice_status(invoice)
    return invoice


def month_bounds(month):
    year, month_no = [int(part) for part in month.split("-")]
    start = date(year, month_no, 1)
    end = date(year + (month_no == 12), 1 if month_no == 12 else month_no + 1, 1)
    return start, end


def dashboard_summary(month=None):
    slots = RoomSlot.query.filter_by(is_active=True).join(Room).filter(Room.is_active == True).all()
    occupied = occupied_slot_ids()
    active_students = Student.query.filter_by(status="Active").count()
    month = month or date.today().strftime("%Y-%m")
    start, end = month_bounds(month)
    invoices = MonthlyInvoice.query.filter_by(month=month).all()
    payments = Payment.query.filter(Payment.payment_date >= start, Payment.payment_date < end, Payment.is_cancelled == False).all()
    expenses = Expense.query.filter(Expense.expense_date >= start, Expense.expense_date < end, Expense.is_deleted == False).all()
    total_expected = sum(money(i.total_amount) for i in invoices)
    total_collected = sum(money(p.amount) for p in payments)
    total_expenses = sum(money(e.amount) for e in expenses)
    latest_student = Student.query.order_by(Student.created_at.desc()).first()
    latest_payment = Payment.query.order_by(Payment.payment_date.desc()).first()
    latest_expense = Expense.query.filter_by(is_deleted=False).order_by(Expense.expense_date.desc()).first()
    collected_details = [{
        "id": payment.id,
        "payer": payment.student.full_name,
        "room": serialize_student_brief(payment.student)["room"],
        "method": payment.method,
        "timestamp": format_timestamp(payment.payment_date),
        "amount": float(payment.amount),
    } for payment in sorted(payments, key=lambda item: item.payment_date, reverse=True)]
    overdue_details = []
    for invoice in MonthlyInvoice.query.filter(MonthlyInvoice.due_date < date.today()).all():
        refresh_invoice(invoice)
        balance = money(invoice.total_amount) - money(invoice.amount_paid)
        if balance > 0:
            student_data = serialize_student_brief(invoice.student)
            overdue_details.append({
                "id": invoice.id,
                "student": invoice.student.full_name,
                "phone": invoice.student.phone,
                "room": student_data["room"],
                "due_date": invoice.due_date.isoformat(),
                "balance": float(balance),
            })
    bedroom_capacity = len([s for s in slots if s.area == "Bedroom"])
    hall_capacity = len([s for s in slots if s.area == "Hall"])
    bedroom_occupied = len([s for s in slots if s.id in occupied and s.area == "Bedroom"])
    hall_occupied = len([s for s in slots if s.id in occupied and s.area == "Hall"])
    return {
        "total_capacity": len(slots),
        "current_students": active_students,
        "occupied_slots": len(occupied),
        "available_slots": len(slots) - len(occupied),
        "bedroom_vacancy": bedroom_capacity - bedroom_occupied,
        "hall_vacancy": hall_capacity - hall_occupied,
        "month": month,
        "monthly_expected_income": float(total_expected),
        "monthly_collected_amount": float(total_collected),
        "pending_amount": float(max(total_expected - total_collected, Decimal("0.00"))),
        "total_expenses": float(total_expenses),
        "net_income": float(total_collected - total_expenses),
        "collection_percentage": float((total_collected / total_expected * 100) if total_expected else 0),
        "latest_student_created": format_timestamp(latest_student.created_at) if latest_student else None,
        "latest_payment": format_timestamp(latest_payment.payment_date) if latest_payment else None,
        "latest_expense": format_timestamp(latest_expense.expense_date) if latest_expense else None,
        "collected_details": collected_details,
        "overdue_details": overdue_details,
    }


def serialize_slot(slot, occupied=None):
    occupied = occupied if occupied is not None else occupied_slot_ids()
    allocation = next((a for a in slot.allocations if a.status == "Active" and a.end_date is None), None)
    student = allocation.student if allocation else None
    return {
        "id": slot.id,
        "code": slot.code,
        "area": slot.area,
        "is_active": slot.is_active,
        "is_occupied": slot.id in occupied,
        "student": serialize_student_brief(student) if student else None,
    }


def serialize_room(room, include_slots=False):
    occupied = occupied_slot_ids()
    active_slots = [slot for slot in room.slots if slot.is_active]
    data = {
        "id": room.id,
        "number": room.number,
        "floor": room.floor.number,
        "capacity": len(active_slots),
        "bedroom_capacity": len([s for s in active_slots if s.area == "Bedroom"]),
        "hall_capacity": len([s for s in active_slots if s.area == "Hall"]),
        "occupied": len([s for s in active_slots if s.id in occupied]),
        "bedroom_occupied": len([s for s in active_slots if s.id in occupied and s.area == "Bedroom"]),
        "hall_occupied": len([s for s in active_slots if s.id in occupied and s.area == "Hall"]),
        "is_active": room.is_active,
    }
    data["available"] = data["capacity"] - data["occupied"]
    if include_slots:
        data["slots"] = [serialize_slot(slot, occupied) for slot in sorted(active_slots, key=lambda s: s.code)]
    return data


def serialize_student_brief(student):
    allocation = current_allocation(student.id) if student else None
    room = allocation.slot.room if allocation else None
    return {
        "id": student.id,
        "student_code": student.student_code,
        "full_name": student.full_name,
        "phone": student.phone,
        "college_name": student.college_name,
        "course": student.course,
        "status": student.status,
        "created_at": format_timestamp(student.created_at),
        "joining_date": format_timestamp(student.joining_date),
        "payment_status": latest_payment_status(student.id),
        "monthly_rent": float(student.monthly_rent or 0),
        "room": room.number if room else None,
        "floor": room.floor.number if room else None,
        "slot": allocation.slot.code if allocation else None,
        "area": allocation.slot.area if allocation else None,
        "balance": student_balance(student.id),
    }


def serialize_student(student):
    data = serialize_student_brief(student)
    data.update({
        "email": student.email,
        "joining_date": format_timestamp(student.joining_date),
        "deposit": float(student.deposit or 0),
        "advance": float(student.advance or 0),
        "guardian_name": student.guardian_name,
        "guardian_phone": student.guardian_phone,
        "address": student.address,
        "roll_number": student.roll_number,
        "year": student.year,
    })
    return data


def current_allocation(student_id):
    return Allocation.query.filter_by(student_id=student_id, status="Active", end_date=None).first()


def student_balance(student_id):
    invoices = MonthlyInvoice.query.filter_by(student_id=student_id).all()
    return float(sum(money(i.total_amount) - money(i.amount_paid) for i in invoices))


def latest_payment_status(student_id):
    invoice = MonthlyInvoice.query.filter_by(student_id=student_id).order_by(MonthlyInvoice.month.desc()).first()
    return invoice.status if invoice else "PENDING"


def allocate_student(student, slot_id):
    slot = RoomSlot.query.get_or_404(slot_id)
    if not slot.is_active or not slot.room.is_active:
        raise ValueError("Selected slot is inactive")
    if active_allocation_query().filter_by(slot_id=slot.id).first():
        raise ValueError("Selected slot is already occupied")
    if current_allocation(student.id):
        raise ValueError("Student already has an active allocation")
    allocation = Allocation(student_id=student.id, slot_id=slot.id)
    db.session.add(allocation)
    return allocation


def create_monthly_invoice(student, month=None):
    settings = HostelSetting.query.first()
    month = month or date.today().strftime("%Y-%m")
    year, month_no = [int(part) for part in month.split("-")]
    due_day = min(student.payment_due_day or settings.monthly_due_day or 5, 28)
    due = date(year, month_no, due_day)
    existing = MonthlyInvoice.query.filter_by(student_id=student.id, month=month).first()
    if existing:
        return refresh_invoice(existing)
    rent = money(student.monthly_rent or settings.default_monthly_rent)
    invoice = MonthlyInvoice(student_id=student.id, month=month, due_date=due, total_amount=rent)
    invoice.items.append(__import__("app.models", fromlist=["InvoiceItem"]).InvoiceItem(label="Monthly Rent", amount=rent))
    invoice.status = calculate_invoice_status(invoice)
    db.session.add(invoice)
    return invoice


def log_action(user_id, action, ip_address=None):
    db.session.add(AuditLog(user_id=user_id, action=action, ip_address=ip_address))
