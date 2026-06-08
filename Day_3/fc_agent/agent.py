# pip install openai python-dotenv

import os
from dotenv import load_dotenv
# from openai import OpenAI
from groq import Groq 
import json

# Your tools are imported here, ready to be passed to the API later
from tools import get_order, get_shipping, check_refund_policy, escalate_to_human

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_order",
            "description": "Retrieve details of a specific order by its ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "The order ID, e.g., '1001'"}
                },
                "required": ["order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_shipping",
            "description": "Get shipping status of an order",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "The order ID"}
                },
                "required": ["order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_refund_policy",
            "description": "Check refund policy for a product category",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "Product category like Electronics, Clothing, Furniture, Books"}
                },
                "required": ["category"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "escalate_to_human",
            "description": "Escalate an angry or frustrated customer to a human agent",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {"type": "string", "description": "Reason for escalation, e.g., 'customer yelled and demanded manager'"}
                },
                "required": ["reason"]
            }
        }
    }
]

def run_agent(user_input):
    messages = [
        {"role": "system", "content": "You are a helpful customer service agent. Use tools to answer orders, shipping, refunds, and escalate when needed."},
        {"role": "user", "content": user_input}
    ]
    
    while True:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # <--- Make sure this is a Groq model!
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        message = response.choices[0].message
        
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            
            if tool_name == "get_order":
                result = get_order(order_id=tool_args["order_id"])
            elif tool_name == "get_shipping":
                result = get_shipping(order_id=tool_args["order_id"])
            elif tool_name == "check_refund_policy":
                result = check_refund_policy(category=tool_args["category"])
            elif tool_name == "escalate_to_human":
                result = escalate_to_human(reason=tool_args["reason"])
            else:
                result = {"error": f"Unknown tool: {tool_name}"}
            
            messages.append(message)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })
        else:
            print(message.content)
            break

if __name__ == "__main__":
    # Test the agent with a sample query
    while True:
        user_input = input("Customer: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting agent.")
            break
        run_agent(user_input)
        print("\n---\n")
        # print("\n---\n")
        # run_agent("What's the status of order 1001?")