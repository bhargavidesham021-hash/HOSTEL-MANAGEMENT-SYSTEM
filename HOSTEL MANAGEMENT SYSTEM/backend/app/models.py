from datetime import date, datetime
from decimal import Decimal
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class User(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), nullable=False, default="staff")
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class HostelSetting(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    hostel_name = db.Column(db.String(180), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    currency = db.Column(db.String(10), default="INR")
    default_monthly_rent = db.Column(db.Numeric(10, 2), default=Decimal("5000.00"))
    default_deposit = db.Column(db.Numeric(10, 2), default=Decimal("5000.00"))
    monthly_due_day = db.Column(db.Integer, default=5)
    late_fee = db.Column(db.Numeric(10, 2), default=Decimal("0.00"))
    receipt_prefix = db.Column(db.String(30), default="JTBH-REC")


class Floor(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    rooms = db.relationship("Room", backref="floor", lazy=True, cascade="all, delete-orphan")


class Room(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    floor_id = db.Column(db.Integer, db.ForeignKey("floor.id"), nullable=False)
    number = db.Column(db.String(20), unique=True, nullable=False)
    capacity = db.Column(db.Integer, default=7, nullable=False)
    bedroom_capacity = db.Column(db.Integer, default=4, nullable=False)
    hall_capacity = db.Column(db.Integer, default=3, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    slots = db.relationship("RoomSlot", backref="room", lazy=True, cascade="all, delete-orphan")


class RoomSlot(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey("room.id"), nullable=False)
    code = db.Column(db.String(10), nullable=False)
    area = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    __table_args__ = (db.UniqueConstraint("room_id", "code", name="uq_room_slot_code"),)


class Student(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    student_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(160), nullable=False)
    dob = db.Column(db.Date)
    gender = db.Column(db.String(20), default="Male")
    phone = db.Column(db.String(30), nullable=False, index=True)
    alternate_phone = db.Column(db.String(30))
    email = db.Column(db.String(180))
    aadhaar_number = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(80))
    state = db.Column(db.String(80))
    pin_code = db.Column(db.String(12))
    college_name = db.Column(db.String(180))
    course = db.Column(db.String(120))
    branch = db.Column(db.String(120))
    year = db.Column(db.String(30))
    roll_number = db.Column(db.String(80))
    joining_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    monthly_rent = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    deposit = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    advance = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    payment_due_day = db.Column(db.Integer, default=5)
    status = db.Column(db.String(30), default="Active", nullable=False)
    guardian_name = db.Column(db.String(160))
    guardian_relation = db.Column(db.String(80))
    guardian_phone = db.Column(db.String(30))
    guardian_alternate_phone = db.Column(db.String(30))
    guardian_address = db.Column(db.Text)
    removed_at = db.Column(db.DateTime)
    removed_by_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    removal_reason = db.Column(db.Text)
    restored_at = db.Column(db.DateTime)


class Allocation(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey("room_slot.id"), nullable=False)
    start_date = db.Column(db.Date, default=date.today, nullable=False)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(20), default="Active", nullable=False)
    student = db.relationship("Student", backref="allocations")
    slot = db.relationship("RoomSlot", backref="allocations")


class MonthlyInvoice(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    month = db.Column(db.String(7), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    amount_paid = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    previous_due = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    discount = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    fine = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    status = db.Column(db.String(20), default="PENDING", nullable=False)
    student = db.relationship("Student", backref="invoices")
    items = db.relationship("InvoiceItem", backref="invoice", cascade="all, delete-orphan")
    __table_args__ = (db.UniqueConstraint("student_id", "month", name="uq_student_month_invoice"),)


class InvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey("monthly_invoice.id"), nullable=False)
    label = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)


class Payment(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    invoice_id = db.Column(db.Integer, db.ForeignKey("monthly_invoice.id"), nullable=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    method = db.Column(db.String(40), nullable=False)
    transaction_id = db.Column(db.String(120))
    notes = db.Column(db.Text)
    receipt_no = db.Column(db.String(40), unique=True, nullable=False)
    received_by_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    is_cancelled = db.Column(db.Boolean, default=False)
    cancellation_reason = db.Column(db.Text)
    student = db.relationship("Student", backref="payments")
    invoice = db.relationship("MonthlyInvoice", backref="payments")


class Expense(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    expense_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    category = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text)
    payment_method = db.Column(db.String(40), nullable=False)
    entered_by_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    notes = db.Column(db.Text)
    bill_path = db.Column(db.String(255))
    edited_by_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    edited_at = db.Column(db.DateTime)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    deleted_by_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    deleted_at = db.Column(db.DateTime)
    deletion_reason = db.Column(db.Text)


class ExpenseHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column(db.Integer, db.ForeignKey("expense.id"), nullable=False)
    action = db.Column(db.String(40), nullable=False)
    snapshot = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Complaint(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    # ``title`` is the public complaint heading used by the student and admin APIs.
    # The remaining legacy columns are retained so existing hostel.db files continue
    # to work without a destructive SQLite table rebuild.
    title = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255))
    complaint_no = db.Column(db.String(40), unique=True, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    category = db.Column(db.String(80), nullable=False, default="General")
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default="MEDIUM")
    status = db.Column(db.String(20), default="PENDING", nullable=False)
    resolution = db.Column(db.Text)
    resolved_at = db.Column(db.DateTime)
    student = db.relationship("Student", backref="complaints")


class Attendance(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    attendance_date = db.Column(db.Date, default=date.today, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    student = db.relationship("Student", backref="attendance")
    __table_args__ = (db.UniqueConstraint("student_id", "attendance_date", name="uq_student_attendance_date"),)


class LeaveRequest(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    from_date = db.Column(db.Date, nullable=False)
    to_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    destination = db.Column(db.String(180))
    emergency_contact = db.Column(db.String(30))
    status = db.Column(db.String(20), default="Pending")
    student = db.relationship("Student", backref="leave_requests")


class OutingRequest(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    outing_date = db.Column(db.Date, nullable=False)
    leaving_time = db.Column(db.String(10), nullable=False)
    expected_return_time = db.Column(db.String(10), nullable=False)
    destination = db.Column(db.String(180), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    emergency_contact = db.Column(db.String(30))
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default="Pending", nullable=False)
    actual_leaving_time = db.Column(db.DateTime)
    actual_return_time = db.Column(db.DateTime)
    decided_by_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    decided_at = db.Column(db.DateTime)
    student = db.relationship("Student", backref="outing_requests")


class Visitor(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    visitor_name = db.Column(db.String(160), nullable=False)
    relation = db.Column(db.String(80))
    phone = db.Column(db.String(30))
    purpose = db.Column(db.Text)
    entry_time = db.Column(db.DateTime, default=datetime.utcnow)
    exit_time = db.Column(db.DateTime)
    id_type = db.Column(db.String(80))
    notes = db.Column(db.Text)
    student = db.relationship("Student", backref="visitors")


class Announcement(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    message = db.Column(db.Text, nullable=False)
    target_type = db.Column(db.String(30), default="Everyone")
    target_value = db.Column(db.String(80))
    is_active = db.Column(db.Boolean, default=True)


class Notification(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255), nullable=False)
    kind = db.Column(db.String(40), default="info")
    is_read = db.Column(db.Boolean, default=False)


class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    action = db.Column(db.String(255), nullable=False)
    ip_address = db.Column(db.String(80))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
