# schema.py
# Pydantic models for contact card extraction.
# Strict validation: phone must normalize to 10 digits, pincode must be exactly 6 digits.

from pydantic import BaseModel, EmailStr, field_validator
import re


class Address(BaseModel):
    city: str
    pincode: str

    @field_validator("pincode")
    @classmethod
    def pincode_must_be_six_digits(cls, v: str) -> str:
        cleaned = re.sub(r"\s+", "", v)  # strip whitespace only
        if not re.fullmatch(r"\d{6}", cleaned):
            raise ValueError(
                f"pincode must be exactly 6 digits, got: '{v}'"
            )
        return cleaned


class ContactCard(BaseModel):
    name: str
    email: EmailStr
    phone: str
    address: Address

    @field_validator("phone")
    @classmethod
    def phone_must_normalize_to_ten_digits(cls, v: str) -> str:
        # Strip spaces, dashes, dots, parentheses, plus sign
        digits_only = re.sub(r"[\s\-\.\(\)\+]", "", v)

        # Remove leading country code +91 or 0
        if digits_only.startswith("91") and len(digits_only) == 12:
            digits_only = digits_only[2:]
        elif digits_only.startswith("0") and len(digits_only) == 11:
            digits_only = digits_only[1:]

        if not re.fullmatch(r"\d{10}", digits_only):
            raise ValueError(
                f"phone must normalize to exactly 10 digits, got: '{v}' → '{digits_only}'"
            )
        return digits_only
