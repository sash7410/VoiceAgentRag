"""
Utility script to generate a synthetic Skyline Motors dealer handbook PDF.

The resulting file is intentionally small but reasonably detailed so that
the RAG pipeline has meaningful content to retrieve.
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


def build_handbook(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(path), pagesize=LETTER)
    width, height = LETTER

    def write_paragraph(text: str, x: float, y: float, leading: float = 14) -> float:
        """
        Write a multi-line paragraph and return the new y position.
        """
        for line in text.split("\n"):
            c.drawString(x, y, line)
            y -= leading
        return y - leading

    margin_x = 1 * inch
    y = height - 1 * inch

    c.setFont("Helvetica-Bold", 18)
    c.drawString(margin_x, y, "Skyline Motors Dealer Handbook")
    y -= 0.4 * inch

    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin_x, y, "1. Model Lineup")
    y -= 0.3 * inch

    c.setFont("Helvetica", 11)
    y = write_paragraph(
        (
            "Skyline Aurora (Sedan)\n"
            "- Trims: LX, EX\n"
            "- Price bands: LX typically between $17,000 and $21,000, EX between "
            "$21,000 and $24,000.\n"
            "- Key points: compact sedan, efficient 4-cylinder engine, good for "
            "city commuting.\n"
        ),
        margin_x,
        y,
    )

    y = write_paragraph(
        (
            "Skyline Horizon (Sedan)\n"
            "- Trims: Sport, Limited\n"
            "- Price bands: Sport between $26,000 and $30,000, Limited between "
            "$30,000 and $34,000.\n"
            "- Key points: midsize sedan with more power, comfortable ride, "
            "suitable for families and longer trips.\n"
        ),
        margin_x,
        y,
    )

    y = write_paragraph(
        (
            "Skyline Trailrunner (SUV)\n"
            "- Trims: AWD, Adventure\n"
            "- Price bands: AWD between $33,000 and $37,000, Adventure between "
            "$37,000 and $42,000.\n"
            "- Key points: all-wheel drive, higher ride height, extra cargo "
            "space, light off-road capability.\n"
        ),
        margin_x,
        y,
    )

    if y < 1.5 * inch:
        c.showPage()
        y = height - 1 * inch

    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin_x, y, "2. Warranty Coverage")
    y -= 0.3 * inch
    c.setFont("Helvetica", 11)

    y = write_paragraph(
        (
            "Basic limited warranty:\n"
            "- Coverage period: 3 years or 36,000 miles, whichever comes first.\n"
            "- Covers most components against defects in materials or workmanship.\n"
            "- Includes adjustments and alignment during the first 12 months or "
            "12,000 miles.\n"
        ),
        margin_x,
        y,
    )

    y = write_paragraph(
        (
            "Powertrain warranty:\n"
            "- Coverage period: 5 years or 60,000 miles, whichever comes first.\n"
            "- Covers engine, transmission, and drivetrain components.\n"
        ),
        margin_x,
        y,
    )

    y = write_paragraph(
        (
            "Corrosion and perforation warranty:\n"
            "- Coverage period: 7 years with unlimited mileage against rust "
            "perforation of body panels.\n"
        ),
        margin_x,
        y,
    )

    if y < 1.5 * inch:
        c.showPage()
        y = height - 1 * inch

    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin_x, y, "3. Maintenance Schedule (Example)")
    y -= 0.3 * inch
    c.setFont("Helvetica", 11)

    y = write_paragraph(
        (
            "Oil and filter change:\n"
            "- Recommended every 7,500 miles or 12 months for normal driving.\n"
            "- For severe conditions (frequent short trips, extreme temperatures), "
            "every 5,000 miles or 6 months is recommended.\n"
        ),
        margin_x,
        y,
    )

    y = write_paragraph(
        (
            "Brake inspection:\n"
            "- Inspect pads, rotors, and fluid level at least once every 12 "
            "months or 12,000 miles.\n"
        ),
        margin_x,
        y,
    )

    if y < 1.5 * inch:
        c.showPage()
        y = height - 1 * inch

    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin_x, y, "4. Financing and Leasing Overview")
    y -= 0.3 * inch
    c.setFont("Helvetica", 11)

    y = write_paragraph(
        (
            "Typical finance terms:\n"
            "- Common terms: 36, 48, 60, or 72 months.\n"
            "- Customers are usually encouraged to make a down payment of at "
            "least 10% of the vehicle price.\n"
            "- Example: for a $24,000 sedan with 10% down and a 60‑month term, "
            "a typical monthly payment might fall in the $380–$430 range, "
            "depending on credit and interest rate.\n"
        ),
        margin_x,
        y,
    )

    y = write_paragraph(
        (
            "Leasing guidelines:\n"
            "- Common lease terms: 36 months with annual mileage limits such as "
            "10,000, 12,000, or 15,000 miles.\n"
            "- Excess mileage charges typically range from $0.15 to $0.25 per "
            "mile above the contracted limit.\n"
            "- Wear-and-tear guidelines require that the vehicle be returned "
            "without major damage and with all scheduled maintenance performed.\n"
        ),
        margin_x,
        y,
    )

    if y < 1.5 * inch:
        c.showPage()
        y = height - 1 * inch

    # Add a couple of extra chapters so the PDF is large enough to simulate
    # a real handbook that spans multiple topics and pages.
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin_x, y, "5. Model Comparison Examples")
    y -= 0.3 * inch
    c.setFont("Helvetica", 11)

    y = write_paragraph(
        (
            "Aurora vs Horizon:\n"
            "- The Aurora is better suited for drivers prioritizing low purchase "
            "price and city fuel efficiency.\n"
            "- The Horizon offers more interior space, a quieter cabin, and "
            "stronger highway acceleration, making it a better choice for "
            "families and commuters with longer daily drives.\n"
            "- In many cases, customers cross‑shopping compact and midsize "
            "sedans can test drive both models on the same visit.\n"
        ),
        margin_x,
        y,
    )

    y = write_paragraph(
        (
            "Horizon vs Trailrunner:\n"
            "- The Trailrunner provides higher seating position, available "
            "all‑wheel drive, and more cargo volume for outdoor gear.\n"
            "- The Horizon generally returns slightly better fuel economy and "
            "offers a smoother, more car‑like ride.\n"
        ),
        margin_x,
        y,
    )

    if y < 1.5 * inch:
        c.showPage()
        y = height - 1 * inch

    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin_x, y, "6. Frequently Asked Questions")
    y -= 0.3 * inch
    c.setFont("Helvetica", 11)

    y = write_paragraph(
        (
            "Q: How long does a typical sales visit take?\n"
            "A: For a basic test drive and price discussion, many guests spend "
            "between 60 and 90 minutes at the dealership. More time may be "
            "required when finalizing finance or lease paperwork.\n"
        ),
        margin_x,
        y,
    )

    y = write_paragraph(
        (
            "Q: Can customers combine national promotions with dealer offers?\n"
            "A: In many cases national incentives can be combined with local "
            "dealer discounts, but certain programs may not stack. Customers "
            "should review the latest program rules with a finance manager.\n"
        ),
        margin_x,
        y,
    )

    y = write_paragraph(
        (
            "Q: What happens at the end of a lease?\n"
            "A: Customers typically have the option to return the vehicle, "
            "purchase it for the residual value, or explore a new lease or "
            "purchase. Excess mileage or damage charges may apply according to "
            "the lease agreement.\n"
        ),
        margin_x,
        y,
    )

    c.showPage()
    c.save()


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    out_path = root / "backend" / "resources" / "dealer_handbook.pdf"
    build_handbook(out_path)
    print(f"Wrote handbook to {out_path}")


