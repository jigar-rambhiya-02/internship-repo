# Prompting Styles Evaluation

## Accuracy

| Style | Correct | Accuracy |
|---|---:|---:|
| Zero-shot | 24/30 | 80.0% |
| Few-shot | 28/30 | 93.3% |
| Role-based | 29/30 | 96.7% |

## Example wins

| Style | Ticket | Why it worked |
|---|---|---|
| Zero-shot | T026 | It correctly treated checkout ZIP-code rejection as a Payment issue. |
| Few-shot | T015 | The examples helped distinguish address changes before fulfillment from Shipping problems. |
| Role-based | T030 | The role prompt's category definitions kept an expired coupon email in Other instead of Payment. |

## Example failures

| Style | Ticket | Prediction | Ground truth | Likely reason |
|---|---|---|---|---|
| Zero-shot | T012 | Refund | Payment | The phrase "charged twice" can sound like a refund request, but the ticket is mainly a billing error. |
| Few-shot | T026 | Login | Payment | The model over-weighted "cannot" plus a rejected code-like field and confused checkout validation with access trouble. |
| Role-based | T017 | Payment | Refund | PayPal and money movement terms pulled the prediction toward billing even though the customer wants a refund method corrected. |

## Conclusion

Role-based prompting worked best in this test at 96.7% accuracy because the category descriptions gave the model clearer routing rules for overlapping cases such as coupon questions, refund payment methods, and delivery-code issues. Few-shot prompting was close behind at 93.3%; the examples were especially useful for teaching category boundaries without a long instruction block. Zero-shot prompting was fastest to write and still useful for obvious tickets, but it struggled most when a ticket contained words from multiple categories.

Use zero-shot prompts for quick prototypes or low-risk triage, few-shot prompts when you have representative examples of the labels, and role-based prompts when the model needs to behave like a consistent support-routing analyst with explicit decision criteria.
