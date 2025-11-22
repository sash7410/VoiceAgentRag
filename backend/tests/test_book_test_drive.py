from backend.tools import TEST_DRIVE_BOOKINGS, book_test_drive


def test_book_test_drive_records_booking() -> None:
  """Ensure the simple in-memory booking helper appends a record."""
  initial_count = len(TEST_DRIVE_BOOKINGS)

  booking = book_test_drive(
      customer_name="Alex",
      contact_phone="111-111-1111",
      contact_email="alex@example.com",
      model="Skyline Aurora EX",
      preferred_time="tomorrow 8 pm",
  )

  assert len(TEST_DRIVE_BOOKINGS) == initial_count + 1
  assert booking in TEST_DRIVE_BOOKINGS
  assert booking["customer_name"] == "Alex"
  assert booking["model"] == "Skyline Aurora EX"


