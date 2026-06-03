"""
Generate customer support policy PDF documents for the Agentic RAG knowledge base.
Run once: python scripts/generate_docs.py
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "docs")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def build_doc(filename: str, title: str, version: str, date: str, sections: list):
    path = os.path.join(OUTPUT_DIR, filename)
    doc = SimpleDocTemplate(
        path,
        pagesize=A4,
        leftMargin=2.5 * cm,
        rightMargin=2.5 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm,
    )

    styles = getSampleStyleSheet()

    style_title = ParagraphStyle(
        "DocTitle", fontSize=18, leading=24, alignment=TA_CENTER,
        textColor=colors.HexColor("#1a1a2e"), spaceAfter=6, fontName="Helvetica-Bold"
    )
    style_meta = ParagraphStyle(
        "Meta", fontSize=9, leading=13, alignment=TA_CENTER,
        textColor=colors.HexColor("#555555"), spaceAfter=4
    )
    style_h1 = ParagraphStyle(
        "H1", fontSize=13, leading=18, spaceBefore=16, spaceAfter=6,
        textColor=colors.HexColor("#1a1a2e"), fontName="Helvetica-Bold"
    )
    style_h2 = ParagraphStyle(
        "H2", fontSize=11, leading=15, spaceBefore=10, spaceAfter=4,
        textColor=colors.HexColor("#333333"), fontName="Helvetica-Bold"
    )
    style_body = ParagraphStyle(
        "Body", fontSize=10, leading=15, spaceAfter=6,
        textColor=colors.HexColor("#222222"), alignment=TA_LEFT
    )
    style_bullet = ParagraphStyle(
        "Bullet", fontSize=10, leading=15, spaceAfter=4,
        leftIndent=16, bulletIndent=0,
        textColor=colors.HexColor("#222222")
    )

    story = []

    # Header
    story.append(Paragraph(title, style_title))
    story.append(Paragraph(f"Version {version}  |  Effective Date: {date}", style_meta))
    story.append(Paragraph("ShopEasy Customer Support", style_meta))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1a1a2e"), spaceAfter=12))

    for section in sections:
        if section["type"] == "h1":
            story.append(Paragraph(section["text"], style_h1))
        elif section["type"] == "h2":
            story.append(Paragraph(section["text"], style_h2))
        elif section["type"] == "body":
            story.append(Paragraph(section["text"], style_body))
        elif section["type"] == "bullet":
            for item in section["items"]:
                story.append(Paragraph(f"• {item}", style_bullet))
            story.append(Spacer(1, 4))
        elif section["type"] == "spacer":
            story.append(Spacer(1, section.get("height", 8)))
        elif section["type"] == "table":
            t = Table(section["data"], colWidths=section.get("colWidths"))
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f5f5f5"), colors.white]),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]))
            story.append(t)
            story.append(Spacer(1, 8))

    doc.build(story)
    print(f"  Created: {filename}")


# ---------------------------------------------------------------------------
# Document 1 — Returns & Refunds Policy
# ---------------------------------------------------------------------------

def create_returns_policy():
    build_doc(
        filename="returns_and_refunds_policy_v1.0.pdf",
        title="Returns and Refunds Policy",
        version="1.0",
        date="June 3, 2026",
        sections=[
            {"type": "h1", "text": "1. Overview"},
            {"type": "body", "text": "ShopEasy offers a hassle-free returns and refunds program designed to ensure complete customer satisfaction. This policy applies to all items purchased directly from ShopEasy.in or from third-party sellers fulfilled by ShopEasy (SFE). Items sold and fulfilled by third-party sellers may have separate return policies."},

            {"type": "h1", "text": "2. Return Window"},
            {"type": "body", "text": "The return window begins from the date of delivery as recorded in the order tracking system. Different product categories have different return windows:"},
            {"type": "table", "colWidths": [8*cm, 4*cm, 5*cm], "data": [
                ["Product Category", "Return Window", "Condition"],
                ["Electronics & Mobiles", "10 days", "Unused, original packaging"],
                ["Clothing, Shoes & Accessories", "30 days", "Unworn, tags intact"],
                ["Books & Stationery", "10 days", "Undamaged"],
                ["Large Appliances", "10 days", "Defective/damaged only"],
                ["Grocery & Perishables", "2 days", "Damaged/wrong item only"],
                ["Jewellery & Watches", "10 days", "Unused, original packaging"],
                ["Furniture & Home Decor", "10 days", "Damaged/defective only"],
                ["Toys & Baby Products", "10 days", "Unused, original packaging"],
            ]},

            {"type": "h1", "text": "3. Eligible Return Conditions"},
            {"type": "body", "text": "A return request will be accepted under the following conditions:"},
            {"type": "bullet", "items": [
                "Item received is damaged or defective.",
                "Item received does not match the product description or image on the website.",
                "Item received is incomplete (missing parts or accessories).",
                "Wrong item was delivered.",
                "Item is no longer needed (subject to category-specific policy).",
            ]},

            {"type": "h1", "text": "4. Non-Returnable Items"},
            {"type": "body", "text": "The following items are not eligible for return:"},
            {"type": "bullet", "items": [
                "Digital products, software licenses, and downloadable content.",
                "Hazardous materials and items with safety seals broken.",
                "Perishable goods beyond the 2-day window.",
                "Customised or personalised products.",
                "Items explicitly marked as non-returnable on the product listing.",
                "Underwear, lingerie, and swimwear for hygiene reasons.",
            ]},

            {"type": "h1", "text": "5. How to Initiate a Return"},
            {"type": "body", "text": "To initiate a return, follow these steps:"},
            {"type": "bullet", "items": [
                "Log in to your ShopEasy.in account.",
                "Navigate to 'Returns & Orders' from the top navigation bar.",
                "Select the order containing the item you wish to return.",
                "Click 'Return or Replace Items' and select the reason for return.",
                "Choose your preferred return method: Pickup or Drop-off.",
                "Print the return label if required and pack the item securely.",
                "Await confirmation and tracking updates via email and SMS.",
            ]},

            {"type": "h1", "text": "6. Refund Process"},
            {"type": "body", "text": "Once the returned item is received and inspected, the refund will be processed as follows:"},
            {"type": "table", "colWidths": [6*cm, 5*cm, 6*cm], "data": [
                ["Refund Method", "Timeframe", "Notes"],
                ["ShopEasy Pay Balance", "2–3 business days", "Fastest option"],
                ["Original Credit/Debit Card", "5–7 business days", "Bank processing times apply"],
                ["Net Banking / UPI", "5–7 business days", "Subject to bank timelines"],
                ["EMI / BNPL", "7–10 business days", "EMI cancellation applies"],
                ["Gift Card / Voucher", "2–3 business days", "Credited to account balance"],
            ]},

            {"type": "h1", "text": "7. Partial Refunds"},
            {"type": "body", "text": "Partial refunds may be issued in the following situations:"},
            {"type": "bullet", "items": [
                "Item is returned in a condition that differs from when it was delivered.",
                "Original packaging or accessories are missing.",
                "Item shows signs of use beyond what is acceptable for the stated return reason.",
            ]},

            {"type": "h1", "text": "8. Replacement Policy"},
            {"type": "body", "text": "For eligible items, customers may request a replacement instead of a refund. Replacements are subject to stock availability. If the item is out of stock, a full refund will be processed automatically."},

            {"type": "h1", "text": "9. Contact & Escalation"},
            {"type": "body", "text": "For return-related queries, contact ShopEasy Customer Support at 1800-3000-9009 (toll-free) or via the 'Help' section on ShopEasy.in. Escalation to a senior resolution specialist is available if the issue is not resolved within 48 hours."},
        ]
    )


# ---------------------------------------------------------------------------
# Document 2 — Shipping & Delivery Policy
# ---------------------------------------------------------------------------

def create_shipping_policy():
    build_doc(
        filename="shipping_and_delivery_policy_v1.0.pdf",
        title="Shipping and Delivery Policy",
        version="1.0",
        date="June 3, 2026",
        sections=[
            {"type": "h1", "text": "1. Overview"},
            {"type": "body", "text": "ShopEasy provides reliable shipping and delivery services across India through its logistics network ShopEasy Logistics and third-party courier partners. This policy outlines delivery timelines, shipping fees, and related terms."},

            {"type": "h1", "text": "2. Delivery Timelines"},
            {"type": "table", "colWidths": [6*cm, 4*cm, 7*cm], "data": [
                ["Delivery Type", "Estimated Time", "Eligibility"],
                ["Same-Day Delivery", "Same day", "Select pin codes, order before 9 AM"],
                ["Next-Day Delivery", "Next business day", "Select items and locations"],
                ["Standard Delivery", "3–5 business days", "All customers"],
                ["Economy Delivery", "6–8 business days", "Remote areas"],
                ["Scheduled Delivery", "Customer chosen date", "Large appliances & furniture"],
            ]},

            {"type": "h1", "text": "3. Shipping Fees"},
            {"type": "body", "text": "Shipping fee structures are as follows:"},
            {"type": "bullet", "items": [
                "Orders above ₹499: FREE standard delivery.",
                "Orders below ₹499: ₹40 shipping fee applies.",
                "Expedited delivery: Additional charges apply based on item weight and destination.",
                "Large items (appliances, furniture): Fixed delivery fee of ₹99–₹499 depending on item.",
            ]},

            {"type": "h1", "text": "4. Delivery Coverage"},
            {"type": "body", "text": "ShopEasy delivers to over 100% of serviceable pin codes across India. Delivery availability depends on the seller's shipping settings and the delivery partner's coverage in that area. You can check delivery availability on the product page by entering your pin code."},

            {"type": "h1", "text": "5. Order Tracking"},
            {"type": "body", "text": "All orders can be tracked in real time through the following channels:"},
            {"type": "bullet", "items": [
                "ShopEasy.in website: 'Returns & Orders' section.",
                "ShopEasy mobile app: Push notifications and order tracking.",
                "Email and SMS updates at every milestone (dispatched, out for delivery, delivered).",
                "Third-party courier tracking via the courier's website using the AWB number provided.",
            ]},

            {"type": "h1", "text": "6. Failed Delivery Attempts"},
            {"type": "body", "text": "If a delivery attempt fails, ShopEasy will make up to 3 delivery attempts on consecutive business days. After 3 failed attempts, the package will be returned to the seller and a refund will be initiated. To reschedule delivery, contact customer support or update your delivery instructions in the app."},

            {"type": "h1", "text": "7. Delivery to Alternate Address"},
            {"type": "body", "text": "Customers can add multiple delivery addresses to their ShopEasy account. You may also update the delivery address after placing an order, provided the order has not yet been dispatched. Address changes are not possible once the item is out for delivery."},

            {"type": "h1", "text": "8. Undeliverable Items"},
            {"type": "body", "text": "Certain items cannot be shipped to specific locations due to legal restrictions, carrier limitations, or hazardous material regulations. These include:"},
            {"type": "bullet", "items": [
                "Flammable or explosive materials.",
                "Certain batteries and electronic devices to remote areas.",
                "Items restricted by state or local regulations.",
            ]},

            {"type": "h1", "text": "9. International Shipping"},
            {"type": "body", "text": "ShopEasy currently does not support outbound international shipping for domestic orders. For international deliveries, customers are directed to ShopEasy Global Store. Import duties and taxes for items from ShopEasy Global Store are the responsibility of the buyer."},
        ]
    )


# ---------------------------------------------------------------------------
# Document 3 — Payments & Pricing Policy
# ---------------------------------------------------------------------------

def create_payments_policy():
    build_doc(
        filename="payments_and_pricing_policy_v1.0.pdf",
        title="Payments and Pricing Policy",
        version="1.0",
        date="June 3, 2026",
        sections=[
            {"type": "h1", "text": "1. Accepted Payment Methods"},
            {"type": "body", "text": "ShopEasy supports a wide range of payment methods to ensure convenience for all customers:"},
            {"type": "table", "colWidths": [5*cm, 12*cm], "data": [
                ["Payment Type", "Details"],
                ["Credit Cards", "Visa, MasterCard, American Express, Diners Club, RuPay"],
                ["Debit Cards", "All major Indian bank debit cards supported"],
                ["Net Banking", "50+ major Indian banks supported"],
                ["UPI", "All UPI-enabled apps: GPay, PhonePe, Paytm, BHIM, etc."],
                ["ShopEasy Pay", "ShopEasy Pay balance, ShopEasy Pay ICICI credit card"],
                ["EMI", "No-cost EMI and standard EMI via credit/debit cards and Bajaj Finserv"],
                ["Buy Now Pay Later", "ShopEasy Pay Later — instant credit up to ₹60,000"],
                ["Cash on Delivery", "Available for eligible orders and pin codes"],
                ["Gift Cards", "ShopEasy.in gift cards and e-gift vouchers"],
            ]},

            {"type": "h1", "text": "2. Payment Security"},
            {"type": "body", "text": "All payment transactions on ShopEasy are secured using industry-standard protocols:"},
            {"type": "bullet", "items": [
                "256-bit SSL encryption for all payment data transmission.",
                "PCI-DSS compliant payment processing.",
                "Two-factor authentication (2FA) via OTP for card and net banking payments.",
                "ShopEasy never stores full card numbers on its servers.",
                "Tokenisation is used for saved payment methods as per RBI guidelines.",
            ]},

            {"type": "h1", "text": "3. EMI Options"},
            {"type": "body", "text": "EMI is available on purchases above ₹3,000 for eligible credit and debit cards. No-cost EMI is available on select products where the interest amount is discounted upfront by the seller or ShopEasy. EMI tenure options range from 3 to 24 months depending on the bank and card type."},

            {"type": "h1", "text": "4. ShopEasy Pay Later"},
            {"type": "body", "text": "ShopEasy Pay Later allows eligible customers to purchase now and pay later with flexible repayment options:"},
            {"type": "bullet", "items": [
                "Instant credit limit up to ₹60,000 based on creditworthiness.",
                "Pay next month or in 3/6/9/12 monthly instalments.",
                "Zero interest for next-month repayment.",
                "Managed through the ShopEasy app under 'ShopEasy Pay Later' section.",
                "Late payment fees apply if repayment is not made by the due date.",
            ]},

            {"type": "h1", "text": "5. Pricing Policy"},
            {"type": "body", "text": "Prices on ShopEasy are set by sellers and may change at any time. The price charged is the price displayed at the time of order placement. ShopEasy participates in price matching on select products. All prices are inclusive of applicable GST unless stated otherwise."},

            {"type": "h1", "text": "6. Price Errors"},
            {"type": "body", "text": "In the event of a pricing error, ShopEasy reserves the right to cancel the order and issue a full refund. Customers will be notified via email within 24 hours of order cancellation due to a pricing error."},

            {"type": "h1", "text": "7. Coupons, Vouchers & Offers"},
            {"type": "body", "text": "Promotional codes and coupons can be applied at checkout. Key rules include:"},
            {"type": "bullet", "items": [
                "Only one coupon code can be applied per order unless stated otherwise.",
                "Coupons cannot be combined with Lightning Deals or other exclusive offers.",
                "Vouchers are non-transferable and non-refundable.",
                "Bank offer discounts apply only to eligible cards and may have maximum discount caps.",
                "Cashback offers are credited to ShopEasy Pay balance within 3–7 business days.",
            ]},

            {"type": "h1", "text": "8. Failed Payments"},
            {"type": "body", "text": "If a payment fails but the amount is debited from your account, it will be automatically reversed within 5–7 business days by your bank. ShopEasy does not hold failed payment amounts. Contact your bank if the reversal does not appear within 7 business days."},

            {"type": "h1", "text": "9. GST & Tax Invoices"},
            {"type": "body", "text": "GST invoices are available for all orders. Business customers can provide their GSTIN at checkout to receive a business invoice. Tax invoices can be downloaded from the 'Returns & Orders' section under 'Invoice'."},
        ]
    )


# ---------------------------------------------------------------------------
# Document 4 — Account Management Policy
# ---------------------------------------------------------------------------

def create_account_policy():
    build_doc(
        filename="account_management_policy_v1.0.pdf",
        title="Account Management Policy",
        version="1.0",
        date="June 3, 2026",
        sections=[
            {"type": "h1", "text": "1. Account Creation"},
            {"type": "body", "text": "To create an ShopEasy account, you must provide a valid email address or mobile number and set a password. You must be at least 18 years of age or have parental/guardian consent to create an account. One person may not maintain multiple accounts; duplicate accounts may be merged or suspended."},

            {"type": "h1", "text": "2. Account Security"},
            {"type": "body", "text": "Customers are responsible for maintaining the security of their account credentials. Best practices include:"},
            {"type": "bullet", "items": [
                "Use a strong, unique password not used on other websites.",
                "Enable Two-Step Verification (2SV) from Account & Security settings.",
                "Never share your OTP, password, or account details with anyone.",
                "Log out of shared or public devices after every session.",
                "Regularly review active sessions under 'Manage Login Sessions'.",
            ]},

            {"type": "h1", "text": "3. Password Recovery"},
            {"type": "body", "text": "If you forget your password, click 'Forgot your password?' on the sign-in page. A one-time password (OTP) will be sent to your registered email or mobile number. Passwords must be at least 8 characters and include a mix of letters and numbers. Reset links expire within 15 minutes of issuance."},

            {"type": "h1", "text": "4. Updating Account Information"},
            {"type": "body", "text": "You can update the following from 'Account & Lists' > 'Account':"},
            {"type": "bullet", "items": [
                "Name, email address, and mobile number.",
                "Delivery addresses (add, edit, delete, set as default).",
                "Payment methods and saved cards.",
                "Communication preferences and notification settings.",
                "Language and regional preferences.",
            ]},

            {"type": "h1", "text": "5. Account Suspension & Termination"},
            {"type": "body", "text": "ShopEasy reserves the right to suspend or terminate accounts that violate its terms of service. Common reasons include:"},
            {"type": "bullet", "items": [
                "Fraudulent activity or misuse of return/refund policies.",
                "Providing false information during account creation.",
                "Multiple accounts created to abuse promotional offers.",
                "Chargebacks filed without valid basis.",
                "Violation of ShopEasy's Community Guidelines.",
            ]},

            {"type": "h1", "text": "6. Account Deletion"},
            {"type": "body", "text": "To request account deletion, navigate to 'Account & Lists' > 'Account' > 'Close Your ShopEasy Account'. Account deletion is permanent and cannot be undone. All order history, wish lists, reviews, and saved data will be permanently removed. Active orders must be completed or cancelled before deletion is processed."},

            {"type": "h1", "text": "7. Data Privacy"},
            {"type": "body", "text": "ShopEasy is committed to protecting your personal data in accordance with the Information Technology Act, 2000 and applicable data protection regulations. Customer data is used solely to provide and improve ShopEasy services. Data is never sold to third parties. For full details, refer to ShopEasy's Privacy Notice available on the website."},

            {"type": "h1", "text": "8. Customer Support"},
            {"type": "body", "text": "For account-related assistance, contact ShopEasy Customer Support via:"},
            {"type": "bullet", "items": [
                "Phone: 1800-3000-9009 (toll-free, 24/7).",
                "Chat: Available on the ShopEasy.in Help page.",
                "Email: Via the 'Contact Us' form in the Help section.",
                "ShopEasy App: 'Help & Customer Service' in the main menu.",
            ]},
        ]
    )


# ---------------------------------------------------------------------------
# Document 5 — Product Condition & Listing Guidelines
# ---------------------------------------------------------------------------

def create_product_condition_guidelines():
    build_doc(
        filename="product_condition_guidelines_v1.0.pdf",
        title="Product Condition and Listing Guidelines",
        version="1.0",
        date="June 3, 2026",
        sections=[
            {"type": "h1", "text": "1. Overview"},
            {"type": "body", "text": "ShopEasy maintains strict guidelines for product condition descriptions to ensure customers receive exactly what they expect. This document defines condition categories, listing standards, and customer rights related to product condition."},

            {"type": "h1", "text": "2. Product Condition Categories"},
            {"type": "table", "colWidths": [4*cm, 13*cm], "data": [
                ["Condition", "Description"],
                ["New", "Brand new, unused, unopened, undamaged item in original manufacturer packaging."],
                ["Renewed", "Professionally inspected, tested and cleaned. Backed by the ShopEasy Renewed Guarantee."],
                ["Used - Like New", "Item in perfect condition. Original protective packaging may be missing."],
                ["Used - Very Good", "Item is well-cared for. May show limited signs of wear. Accessories included."],
                ["Used - Good", "Item shows signs of use. Fully functional. May have cosmetic imperfections."],
                ["Used - Acceptable", "Item is fairly worn but fully functional. Significant cosmetic damage possible."],
                ["Collectible", "Items with special characteristics; condition sub-noted by seller."],
            ]},

            {"type": "h1", "text": "3. ShopEasy Renewed Program"},
            {"type": "body", "text": "ShopEasy Renewed products are professionally refurbished, pre-owned products that have been inspected and tested to work and look like new. Key features of the program include:"},
            {"type": "bullet", "items": [
                "Minimum 90-day supplier-backed warranty or ShopEasy Renewed Guarantee.",
                "Products tested by qualified suppliers with a minimum 90-day warranty.",
                "Products include all relevant accessories.",
                "If the product does not work as expected, ShopEasy offers a replacement or refund within 90 days.",
            ]},

            {"type": "h1", "text": "4. Listing Accuracy Requirements"},
            {"type": "body", "text": "All sellers on ShopEasy must accurately represent the condition of their products. Requirements include:"},
            {"type": "bullet", "items": [
                "Product images must accurately represent the actual item being sold.",
                "Condition notes must disclose all known defects or cosmetic damage.",
                "Product descriptions must not be misleading or omit material information.",
                "Sellers must update listings promptly if product condition changes.",
                "Counterfeit or inauthentic products are strictly prohibited.",
            ]},

            {"type": "h1", "text": "5. A-to-Z Guarantee"},
            {"type": "body", "text": "The ShopEasy A-to-Z Guarantee protects customers when purchasing from third-party sellers on ShopEasy.in. Coverage includes:"},
            {"type": "bullet", "items": [
                "Item not received within the estimated delivery date.",
                "Item received is materially different from what was described.",
                "Item received is damaged or defective.",
                "Seller refuses to provide a refund or replacement for a valid return.",
            ]},
            {"type": "body", "text": "To file an A-to-Z Guarantee claim, go to 'Returns & Orders', select the order, and click 'File/View Claim'. Claims must be filed within 90 days of the maximum estimated delivery date."},

            {"type": "h1", "text": "6. Counterfeit & Intellectual Property"},
            {"type": "body", "text": "ShopEasy has a zero-tolerance policy for counterfeit products. Sellers found listing counterfeit items face immediate account suspension and legal action. Customers who receive suspected counterfeit items should report them via the product listing page using the 'Report a violation' link or contact customer support."},

            {"type": "h1", "text": "7. Customer Rights"},
            {"type": "body", "text": "Customers who receive an item that does not match its listed condition are entitled to:"},
            {"type": "bullet", "items": [
                "A full refund including return shipping costs.",
                "A free replacement of the same item.",
                "An A-to-Z Guarantee claim if the seller is unresponsive.",
                "Escalation to ShopEasy's specialist team for complex cases.",
            ]},
        ]
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Generating PDFs into: {os.path.abspath(OUTPUT_DIR)}\n")
    create_returns_policy()
    create_shipping_policy()
    create_payments_policy()
    create_account_policy()
    create_product_condition_guidelines()
    print("\nDone. All 5 documents generated.")
