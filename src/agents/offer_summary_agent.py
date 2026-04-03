import anthropic
from datetime import date
import os
from dotenv import load_dotenv
load_dotenv()
def summarize_offer(
    # --- From ApplicationIn (applications table) ---
    full_name: str,
    email: str,
    emirates_id: str,
    phone: str,
    community: str,
    property_type: str,
    size_sqft: float,

    # --- From EstimateOut (estimates table) ---
    estimated_value_aed: float,

    # --- From Offer (offers table — generated after underwriting) ---
    approved_amount: float,
    rental_rate: float,        # decimal, e.g. 0.04 for 4%
    expiry_date: str,          # ISO format: "YYYY-MM-DD"

    # --- Optional config ---
    api_key: str | None = None,
) -> str:
    """
    Generates a plain-language Sharia-compliant offer summary using Claude.

    Parameters
    ----------
    -- ApplicationIn --
    full_name            : Full name of the applicant.
    email                : Applicant's email address.
    emirates_id          : Applicant's Emirates ID number.
    phone                : Applicant's phone number.
    community            : Community/area where the property is located.
    property_type        : Type of property (e.g. "Villa", "Apartment").
    size_sqft            : Property size in square feet.

    -- EstimateOut --
    estimated_value_aed  : Estimated property value in AED from the valuation engine.

    -- Offer fields (generated after underwriting) --
    approved_amount      : Amount the platform approved (AED).
    rental_rate          : Annual rental rate on the platform's share (decimal).
    expiry_date          : Offer expiry date in "YYYY-MM-DD" format.

    -- Config --
    api_key              : Anthropic API key. Falls back to ANTHROPIC_API_KEY env var.

    Returns
    -------
    str : A 3–5 sentence plain-language summary of the offer.

    Example (backend usage)
    -----------------------
    summary = summarize_offer(
        # From ApplicationIn row
        full_name            = application["full_name"],
        email                = application["email"],
        emirates_id          = application["emirates_id"],
        phone                = application["phone"],
        community            = application["community"],
        property_type        = application["property_type"],
        size_sqft            = application["size_sqft"],

        # From EstimateOut row
        estimated_value_aed  = estimate["estimated_value_aed"],

        # From Offer row
        approved_amount      = offer["approved_amount"],
        rental_rate          = offer["rental_rate"],
        expiry_date          = offer["expiry_date"],
    )
    """

    expiry_dt         = date.fromisoformat(expiry_date)
    days_left         = (expiry_dt - date.today()).days
    platform_share    = estimated_value_aed - approved_amount
    monthly_rent      = (approved_amount * rental_rate) / 12

   
    system_prompt = (
        "You are an assistant for a Sharia-compliant home equity platform in the UAE. "
        "Summarize financing offers in plain, friendly language. "
        "Never use jargon or mention interest. "
        "This is an Ijara co-ownership model: the platform owns a property share; "
        "the applicant pays rent on that share only. "
        "Reply in 3-5 sentences only."
    )

    user_message = (
        f"Applicant: {full_name}\n"
        f"Property: {property_type} in {community} ({size_sqft:,.0f} sqft)\n"
        f"Estimated property value: AED {estimated_value_aed:,.0f}\n"
        f"Platform's approved share: AED {approved_amount:,.0f}\n"
        f"Applicant's equity share: AED {platform_share:,.0f}\n"
        f"Rental rate: {rental_rate * 100:.1f}% per year on platform's share "
        f"(≈ AED {monthly_rent:,.0f}/month)\n"
        f"Offer expires: {expiry_date} ({days_left} days left)\n\n"
        "Summarize this offer for the applicant. Cover: the platform's share vs property value, "
        "what the monthly rent figure means practically, expiry urgency, "
        "and zero obligation until draw."
    )


    client = anthropic.Anthropic(
        api_key= api_key or os.environ.get("ANTHROPIC_API_KEY")
    )

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=300,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )

    return message.content[0].text


if __name__ == "__main__":
    summary = summarize_offer(
        full_name            = "Mohammed Al Rashidi",
        email                = "mohammed@example.com",
        emirates_id          = "784-1990-1234567-1",
        phone                = "+971501234567",
        community            = "Arabian Ranches",
        property_type        = "Villa",
        size_sqft            = 3200,
        estimated_value_aed  = 2_500_000,
        approved_amount      = 750_000,
        rental_rate          = 0.04,
        expiry_date          = "2026-04-15",
    )
    print("─" * 60)
    print(summary)
    print("─" * 60)