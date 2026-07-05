# Comparison: Without Repair vs With Repair

## Summary Table

| Metric                  | Without Repair | With Repair |
|-------------------------|----------------|-------------|
| Success Rate            | 85.0%          | 95.0%       |
| Failed Count            | 3              | 1           |
| Total Attempts Used     | 20             | 26          |
| Total Estimated Cost    | $0.0080        | $0.0115     |

## Success Rate Without Repair

On first attempt, [X out of 20] inputs produced a valid ContactCard.
Common reasons for failure: [fill in — e.g. malformed JSON, invalid email format, phone not normalizing]

## Success Rate With Repair

After the repair loop (up to 3 retries), [Y out of 20] inputs produced a valid ContactCard.
The repair loop recovered [Y - X] additional inputs.

## Common Error Types Fixed by Repair

- JSON syntax errors (model returned extra text or markdown fences)
- Invalid email (OCR errors like gmai1.com that the repair prompt corrected)
- Phone normalization failure (too many digits, letters mixed in)
- Invalid pincode (spaces inside digits, wrong digit count)
- Missing fields (model omitted a key; repair prompt re-emphasized the schema)

## Inputs That Still Failed

| Input ID   | Reason for Failure                          |
|------------|---------------------------------------------|
| input_11   | email address should have @ sign            |
| input_19   | Incorrect Digit in Phone number             |

## Cost vs Success Trade-off

Base cost (first attempts only): $0.0080
Total cost with repairs: $0.0115
Cost to recover each additional valid record: $ 0.00175

Analysis: The extra cost was definitely not worth it. 

## Final Conclusion

The improvements were necessary because, in some cases, the email address was incomplete and the phone number wasn't properly formatted. However, one more issue remains: the model still fails to detect when the order of information is incorrect.
