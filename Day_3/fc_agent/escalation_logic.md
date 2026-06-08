# Escalation Logic for Customer Service Agent

## What Triggers Escalation

The agent calls `escalate_to_human` when the user's message indicates:

1. **Explicit request for human agent** – Keywords like "human", "manager", "real person", "talk to someone", "connect me", "escalate".

2. **Strong frustration or anger** – Phrases indicating high dissatisfaction:
   - "This is ridiculous"
   - "I'm extremely frustrated"
   - "Your service is terrible"
   - "I've been waiting for weeks"
   - Threatening language or yelling (e.g., all caps, exclamation marks)

3. **Repeat complaints after agent already provided information** – If the user rejects the agent's answer twice and demands human intervention.

## What Context the Agent Passes

When calling `escalate_to_human(reason)`, the agent provides a `reason` string that includes:

- **The user's original complaint** (quoted if possible)
- **What tools were attempted** (if any) and their results
- **Why the agent decided to escalate** (e.g., "user explicitly asked for a manager")

### Example reason strings:

- `"User said: 'Connect me to a real person right now' – explicit human request"`
- `"User expressed extreme frustration after being told order 1019 is delayed. Said: 'This is ridiculous, I want a manager.'"`
- `"User rejected refund policy information twice and demanded human agent for Electronics return."`

## Note

The agent does not automatically escalate on any negative sentiment. Low-level complaints (e.g., "I'm unhappy with delivery time") first trigger refund policy checks or order status lookup. Escalation is reserved for high-frustration or explicit human requests.