import frappe
from frappe.utils import today, add_days, nowtime

def run():
    frappe.set_user("Administrator")
    print("🌱 Seeding demo data for Hospitality Core...")

    create_room_types()
    create_rooms()
    create_rate_plans()
    create_guests()
    create_reservations()

    frappe.db.commit()
    print("✅ Demo data seeded successfully.")


def create_room_types():
    types = [
        {"hotel_room_type": "Standard", "description": "Standard Room"},
        {"hotel_room_type": "Deluxe", "description": "Deluxe Room"},
        {"hotel_room_type": "Suite", "description": "Executive Suite"},
    ]
    for t in types:
        if not frappe.db.exists("Hotel Room Type", t["hotel_room_type"]):
            frappe.get_doc({"doctype": "Hotel Room Type", **t}).insert(ignore_permissions=True)
            print(f"  ✔ Room Type: {t['hotel_room_type']}")


def create_rooms():
    rooms = [
        {"name": "101", "hotel_room_type": "Standard", "status": "Available"},
        {"name": "102", "hotel_room_type": "Standard", "status": "Available"},
        {"name": "103", "hotel_room_type": "Standard", "status": "Available"},
        {"name": "201", "hotel_room_type": "Deluxe",   "status": "Available"},
        {"name": "202", "hotel_room_type": "Deluxe",   "status": "Available"},
        {"name": "301", "hotel_room_type": "Suite",    "status": "Available"},
    ]
    for r in rooms:
        if not frappe.db.exists("Hotel Room", r["name"]):
            frappe.get_doc({"doctype": "Hotel Room", **r}).insert(ignore_permissions=True)
            print(f"  ✔ Room: {r['name']} ({r['hotel_room_type']})")


def create_rate_plans():
    plans = [
        {"hotel_room_type": "Standard", "rate": 80},
        {"hotel_room_type": "Deluxe",   "rate": 150},
        {"hotel_room_type": "Suite",    "rate": 300},
    ]
    for p in plans:
        name = f"{p['hotel_room_type']} Rate"
        if not frappe.db.exists("Room Rate Plan", name):
            frappe.get_doc({
                "doctype": "Room Rate Plan",
                "rate_plan_name": name,
                "hotel_room_type": p["hotel_room_type"],
                "rate": p["rate"]
            }).insert(ignore_permissions=True)
            print(f"  ✔ Rate Plan: {name} @ {p['rate']}")


def create_guests():
    guests = [
        {"first_name": "John",   "last_name": "Doe",     "email_id": "john.doe@example.com",     "mobile_no": "0711000001"},
        {"first_name": "Jane",   "last_name": "Smith",   "email_id": "jane.smith@example.com",   "mobile_no": "0711000002"},
        {"first_name": "Robert", "last_name": "Brown",   "email_id": "robert.brown@example.com", "mobile_no": "0711000003"},
        {"first_name": "Emily",  "last_name": "Clarke",  "email_id": "emily.c@example.com",      "mobile_no": "0711000004"},
        {"first_name": "Michael","last_name": "Scott",   "email_id": "m.scott@example.com",      "mobile_no": "0711000005"},
    ]
    for g in guests:
        existing = frappe.db.exists("Guest", {
            "first_name": g["first_name"],
            "last_name": g["last_name"]
        })
        if not existing:
            frappe.get_doc({"doctype": "Guest", **g}).insert(ignore_permissions=True)
            print(f"  ✔ Guest: {g['first_name']} {g['last_name']}")


def get_guest_name(first, last):
    return frappe.db.get_value("Guest", {"first_name": first, "last_name": last}, "name")


def create_reservations():
    reservations = [
        {
            "guest": get_guest_name("John", "Doe"),
            "hotel_room": "101",
            "arrival_date": today(),
            "departure_date": add_days(today(), 3),
            "status": "Checked In",
        },
        {
            "guest": get_guest_name("Jane", "Smith"),
            "hotel_room": "201",
            "arrival_date": today(),
            "departure_date": add_days(today(), 2),
            "status": "Checked In",
        },
        {
            "guest": get_guest_name("Robert", "Brown"),
            "hotel_room": "301",
            "arrival_date": add_days(today(), 1),
            "departure_date": add_days(today(), 5),
            "status": "Reserved",
        },
        {
            "guest": get_guest_name("Emily", "Clarke"),
            "hotel_room": "102",
            "arrival_date": add_days(today(), -2),
            "departure_date": add_days(today(), 1),
            "status": "Checked In",
        },
        {
            "guest": get_guest_name("Michael", "Scott"),
            "hotel_room": "202",
            "arrival_date": add_days(today(), -5),
            "departure_date": add_days(today(), -1),
            "status": "Checked Out",
        },
    ]
    for r in reservations:
        if not r["guest"]:
            print(f"  ⚠ Skipping reservation — guest not found")
            continue
        frappe.get_doc({"doctype": "Hotel Reservation", **r}).insert(ignore_permissions=True)
        print(f"  ✔ Reservation: {r['guest']} → Room {r['hotel_room']} ({r['status']})")