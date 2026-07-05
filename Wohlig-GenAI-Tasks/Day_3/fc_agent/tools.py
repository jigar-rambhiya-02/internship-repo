import json
import os

def load_orders(file_path = 'fake_orders.json'):
    with open(file_path, 'r') as f:
        orders = json.load(f)
    return orders
            
def get_order(order_id):
    orders = load_orders()
    for order in orders:
        if order["order_id"] == order_id:
            return order
    return {"error": f"Order {order_id} not found"}

def get_shipping(order_id):
    order = get_order(order_id)
    
    if order is None or "error" in order:
        return {"error": f"Order {order_id} not found"}
    
    status = order["status"]
    
    status_messages = {
        "delivered": "Your order has been delivered.",
        "in-transit": "Your order is in transit.",
        "returned": "This order was returned.",
        "disputed": "This order is under dispute."
    }
    
    message = status_messages.get(status, f"Status unknown: {status}")
    
    return {"order_id": order_id, "shipping_status": message}


def check_refund_policy(category):
    policies = {
        'Electronics': '90 Days return policy',
        "Clothing": '7 Days return policy',
        "Books": '2 Days return policy',
        "Furniture": '30 Days return policy'
    }
    
    policy = policies.get(category, 'Please check our website for specific policy')
    
    return {'category': category, 'policy': policy}


def escalate_to_human(reason):
    return {
        "status": "escalated",
        "message": "A human agent will follow up within 24 hours.",
        "reason_received": reason
    }
    