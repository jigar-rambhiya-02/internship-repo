# Test Queries for Customer Service Agent

## Single-Tool Queries (3)

1. **get_order only**  
   `"What are the details of order #1005?"`

2. **get_shipping only**  
   `"Can you tell me the shipping status for order 1013?"`

3. **check_refund_policy only**  
   `"What's your refund policy for Electronics?"`

---

## Multi-Tool Queries (needs 2+ tools) (3)

4. **get_order + check_refund_policy**  
   `"I want to return the item from order 1002. What's the refund policy for that product?"`

5. **get_shipping + escalate_to_human** (if shipping delayed)  
   `"My order 1019 is late. Check the shipping status and if it's not delivered by tomorrow, connect me to a human."`

6. **get_order + get_shipping**  
   `"Show me order 1007 details and also tell me where it is right now."`

---

## Multi-Turn Conversations (2)

7. **Turn 1:** `"I need help with an order."`  
   **Turn 2:** `"Order number 1004"`

8. **Turn 1:** `"What's the status of order 1011?"`  
   **Turn 2:** `"And what about the refund policy for that category?"`

---

## Escalation Queries (should trigger escalate_to_human) (2)

9. **Explicit request for human**  
   `"This is ridiculous. I've been waiting for weeks. Connect me to a real person right now."`

10. **Angry/frustrated customer**  
    `"I am extremely frustrated. Your service is terrible. I demand to speak with a manager immediately."`