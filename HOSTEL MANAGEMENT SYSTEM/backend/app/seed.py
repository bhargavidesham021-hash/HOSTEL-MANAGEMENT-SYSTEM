from decimal import Decimal
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

    owner = User.query.filter_by(email="bhargavi021@gmail.com").first()
    if not owner:
        owner = User.query.filter_by(email="owner@jtbh.local").first()
    if not owner:
        owner = User(name="Hostel Owner", email="bhargavi021@gmail.com", role="owner")
        db.session.add(owner)
    owner.email = "bhargavi021@gmail.com"
    # Only establish the initial development credential.  Do not overwrite a
    # password hash (or any registered account) every time the app starts.
    if not owner.password_hash:
        owner.set_password("MRECW")

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
