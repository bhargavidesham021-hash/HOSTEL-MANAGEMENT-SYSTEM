from decimal import Decimal
import os
from .extensions import db
from .models import Floor, HostelSetting, Room, RoomSlot, User


def seed_database():
    if not HostelSetting.query.first():
        db.session.add(HostelSetting(
            hostel_name="Jai Tulja Bhavani Deluxe Boys Hostel",
            phone="9822222064",
            address="Near Aurora College, Aushapur",
            currency="INR",
            default_monthly_rent=Decimal("5000.00"),
            default_deposit=Decimal("5000.00"),
            monthly_due_day=5,
            receipt_prefix="JTBH-REC",
        ))

    admin_username = os.getenv("ADMIN_USERNAME", "").strip()
    admin_email = (os.getenv("ADMIN_EMAIL", "").strip() or admin_username).lower()
    admin_password = os.getenv("ADMIN_PASSWORD", "")
    if admin_email and admin_password:
        owner = User.query.filter_by(email=admin_email).first()
        if not owner and admin_username:
            owner = User.query.filter_by(email=admin_username.lower()).first()
        if not owner:
            owner = User(name=os.getenv("ADMIN_NAME", "Hostel Owner"), email=admin_email, role="owner")
            owner.set_password(admin_password)
            db.session.add(owner)
        # Existing owner credentials are deliberately left unchanged.

    if not Floor.query.first():
        structure = {1: ["101", "102", "103", "104"], 2: ["201", "202", "203", "204"], 3: ["301", "302"]}
        for floor_no, rooms in structure.items():
            floor = Floor(number=floor_no, name=f"Floor {floor_no}")
            db.session.add(floor)
            db.session.flush()
            for number in rooms:
                room = Room(floor_id=floor.id, number=number, capacity=7, bedroom_capacity=4, hall_capacity=3)
                db.session.add(room)
                db.session.flush()
                for index in range(1, 5):
                    db.session.add(RoomSlot(room_id=room.id, code=f"B{index}", area="Bedroom"))
                for index in range(1, 4):
                    db.session.add(RoomSlot(room_id=room.id, code=f"H{index}", area="Hall"))

    db.session.commit()
