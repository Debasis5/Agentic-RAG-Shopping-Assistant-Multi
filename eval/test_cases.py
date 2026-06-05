"""
Golden dataset: 2 test cases per PDF (10 total).
Each case has: input (query), expected_output (ground-truth answer), context (source chunks).

The context strings mirror the format rag_node produces:
    "[Source: <title>]\n<content>"
so that DeepEval ContextualRecall / ContextualPrecision see the same text the RAG pipeline sees.
"""

from deepeval.test_case import LLMTestCase

# ---------------------------------------------------------------------------
# 1. Returns and Refunds Policy
# ---------------------------------------------------------------------------
returns_tc1 = LLMTestCase(
    input="What is the return window for electronics purchased on ShopEasy?",
    expected_output=(
        "Electronics purchased on ShopEasy have a 7-day return window from the date of delivery."
    ),
    actual_output="",   # filled at runtime by run_eval.py
    retrieval_context=[
        "[Source: Returns and Refunds Policy]\n"
        "Electronics: 7-day return window from the date of delivery. "
        "Items must be unused and in original packaging with all accessories included."
    ],
)

returns_tc2 = LLMTestCase(
    input="Which items are non-returnable on ShopEasy?",
    expected_output=(
        "Non-returnable items on ShopEasy include perishable goods, digital products after download, "
        "personalised or customised items, hygiene products once opened (such as innerwear and "
        "swimwear), and hazardous materials."
    ),
    actual_output="",
    retrieval_context=[
        "[Source: Returns and Refunds Policy]\n"
        "Non-returnable items: perishable goods, digital products after download, "
        "personalised/customised items, hygiene products once opened (innerwear, swimwear), "
        "and hazardous materials."
    ],
)

# ---------------------------------------------------------------------------
# 2. Shipping and Delivery Policy
# ---------------------------------------------------------------------------
shipping_tc1 = LLMTestCase(
    input="What is the free shipping threshold on ShopEasy?",
    expected_output=(
        "ShopEasy offers free shipping on orders above Rs. 499. "
        "Orders below Rs. 499 attract a shipping fee of Rs. 40."
    ),
    actual_output="",
    retrieval_context=[
        "[Source: Shipping and Delivery Policy]\n"
        "Shipping fees: Free shipping on orders above Rs. 499. "
        "A flat shipping fee of Rs. 40 applies to orders below Rs. 499."
    ],
)

shipping_tc2 = LLMTestCase(
    input="What happens if a ShopEasy delivery attempt fails?",
    expected_output=(
        "ShopEasy makes up to 3 delivery attempts. If all three attempts fail, "
        "the package is returned to the seller and a refund is initiated."
    ),
    actual_output="",
    retrieval_context=[
        "[Source: Shipping and Delivery Policy]\n"
        "Failed delivery policy: up to 3 delivery attempts are made. "
        "If all attempts fail, the package is returned to the seller and a refund is initiated."
    ],
)

# ---------------------------------------------------------------------------
# 3. Payments and Pricing Policy
# ---------------------------------------------------------------------------
payments_tc1 = LLMTestCase(
    input="What is the minimum purchase amount required to use EMI on ShopEasy?",
    expected_output=(
        "EMI is available on purchases above Rs. 3,000 for eligible credit and debit cards. "
        "EMI tenure options range from 3 to 24 months depending on the bank and card type."
    ),
    actual_output="",
    retrieval_context=[
        "[Source: Payments and Pricing Policy]\n"
        "EMI is available on purchases above Rs. 3,000 for eligible credit and debit cards. "
        "No-cost EMI is available on select products. "
        "EMI tenure options range from 3 to 24 months depending on the bank and card type."
    ],
)

payments_tc2 = LLMTestCase(
    input="How long does it take for a failed payment reversal to appear on ShopEasy?",
    expected_output=(
        "If a payment fails but the amount is debited, it will be automatically reversed within "
        "5–7 business days by your bank. If the reversal does not appear within 7 business days, "
        "you should contact your bank."
    ),
    actual_output="",
    retrieval_context=[
        "[Source: Payments and Pricing Policy]\n"
        "Failed payments: if a payment fails but the amount is debited from your account, "
        "it will be automatically reversed within 5–7 business days by your bank. "
        "ShopEasy does not hold failed payment amounts. "
        "Contact your bank if the reversal does not appear within 7 business days."
    ],
)

# ---------------------------------------------------------------------------
# 4. Account Management Policy
# ---------------------------------------------------------------------------
account_tc1 = LLMTestCase(
    input="How do I recover my ShopEasy account password?",
    expected_output=(
        "To recover your ShopEasy password, click 'Forgot your password?' on the sign-in page. "
        "An OTP will be sent to your registered email or mobile number. "
        "Passwords must be at least 8 characters and include a mix of letters and numbers. "
        "Reset links expire within 15 minutes of issuance."
    ),
    actual_output="",
    retrieval_context=[
        "[Source: Account Management Policy]\n"
        "Password recovery: click 'Forgot your password?' on the sign-in page. "
        "An OTP will be sent to your registered email or mobile number. "
        "Passwords must be at least 8 characters and include a mix of letters and numbers. "
        "Reset links expire within 15 minutes of issuance."
    ],
)

account_tc2 = LLMTestCase(
    input="What happens to my data when I delete my ShopEasy account?",
    expected_output=(
        "Account deletion on ShopEasy is permanent and cannot be undone. "
        "All order history, wish lists, reviews, and saved data will be permanently removed. "
        "Active orders must be completed or cancelled before deletion is processed."
    ),
    actual_output="",
    retrieval_context=[
        "[Source: Account Management Policy]\n"
        "Account deletion: permanent and cannot be undone. "
        "All order history, wish lists, reviews, and saved data will be permanently removed. "
        "Active orders must be completed or cancelled before deletion is processed."
    ],
)

# ---------------------------------------------------------------------------
# 5. Product Condition and Listing Guidelines
# ---------------------------------------------------------------------------
product_tc1 = LLMTestCase(
    input="What warranty does a ShopEasy Renewed product come with?",
    expected_output=(
        "ShopEasy Renewed products come with a minimum 90-day supplier-backed warranty or the "
        "ShopEasy Renewed Guarantee. If the product does not work as expected, ShopEasy offers "
        "a replacement or refund within 90 days."
    ),
    actual_output="",
    retrieval_context=[
        "[Source: Product Condition and Listing Guidelines]\n"
        "ShopEasy Renewed Program: professionally refurbished products inspected and tested to "
        "work and look like new. Minimum 90-day supplier-backed warranty or ShopEasy Renewed "
        "Guarantee. If the product does not work as expected, ShopEasy offers a replacement or "
        "refund within 90 days."
    ],
)

product_tc2 = LLMTestCase(
    input="What are my rights if I receive a ShopEasy item that doesn't match its listed condition?",
    expected_output=(
        "If you receive an item that does not match its listed condition, you are entitled to a "
        "full refund including return shipping costs, a free replacement of the same item, an "
        "A-to-Z Guarantee claim if the seller is unresponsive, or escalation to ShopEasy's "
        "specialist team for complex cases."
    ),
    actual_output="",
    retrieval_context=[
        "[Source: Product Condition and Listing Guidelines]\n"
        "Customer rights: customers who receive an item that does not match its listed condition "
        "are entitled to: a full refund including return shipping costs; a free replacement of "
        "the same item; an A-to-Z Guarantee claim if the seller is unresponsive; escalation to "
        "ShopEasy's specialist team for complex cases."
    ],
)

# ---------------------------------------------------------------------------
# Exported list — used by run_eval.py
# ---------------------------------------------------------------------------
ALL_TEST_CASES = [
    returns_tc1,
    returns_tc2,
    shipping_tc1,
    shipping_tc2,
    payments_tc1,
    payments_tc2,
    account_tc1,
    account_tc2,
    product_tc1,
    product_tc2,
]
