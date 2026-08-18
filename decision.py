from data import (
    inventory,
    orders,
    get_product_by_sku,
    get_order_by_id
)


def get_customer_score(priority):

    scores = {
        "PLATINUM": 100,
        "GOLD": 80,
        "SILVER": 60,
        "BRONZE": 40
    }

    return scores.get(priority, 50)


def inventory_summary():

    total_stock = sum(
        item["stock"]
        for item in inventory
    )

    total_available = sum(
        item["available_stock"]
        for item in inventory
    )

    total_reserved = sum(
        item["reserved"]
        for item in inventory
    )

    low_stock = sum(
        1
        for item in inventory
        if item["available_stock"] <= item["reorder_level"]
    )

    return {
        "total_products": len(inventory),
        "total_stock": total_stock,
        "total_available": total_available,
        "total_reserved": total_reserved,
        "low_stock_products": low_stock
    }


def analyze_order(order_id):

    order = get_order_by_id(order_id)

    if order is None:
        return {
            "error": "Order not found",
            "order_id": order_id
        }

    product = get_product_by_sku(
        order["sku"]
    )

    if product is None:
        return {
            "error": "Product not found",
            "order_id": order_id
        }

    required = order["required_quantity"]
    available = product["available_stock"]

    shortage = max(
        0,
        required - available
    )

    customer_priority = get_customer_score(
        order["customer_priority"]
    )

    business_impact = order.get(
        "business_impact", 50
    )

    sla_urgency = order.get(
        "sla_urgency", 50
    )

    distance_impact = order.get(
        "distance_impact", 50
    )

    if available <= 5:
        stock_security = 95
    elif available <= 10:
        stock_security = 85
    elif available <= 20:
        stock_security = 72
    else:
        stock_security = 50

    gap_score = min(
        100,
        shortage * 10
    )

    risk_score = round(
        customer_priority * 0.20
        + business_impact * 0.20
        + sla_urgency * 0.20
        + stock_security * 0.20
        + gap_score * 0.20
    )

    if risk_score >= 75:
        risk_level = "HIGH"
    elif risk_score >= 50:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    if shortage > 0:

        recommendation = (
            f"Prioritize {order_id} "
            "for available inventory"
        )

        reason = (
            "Insufficient stock + "
            f"{order['customer_priority']} "
            "customer priority + SLA urgency."
        )

    else:

        recommendation = (
            f"Fulfill {order_id} completely"
        )

        reason = (
            "Sufficient inventory is available "
            "to fulfill the order."
        )

    return {
        "order_id": order_id,
        "product": product["name"],
        "sku": product["sku"],
        "required_quantity": required,
        "available_stock": available,
        "inventory_gap": shortage,
        "risk_score": risk_score,
        "risk_level": risk_level,

        "factor_scores": {
            "customer_priority": customer_priority,
            "business_impact": business_impact,
            "sla_urgency": sla_urgency,
            "stock_security": stock_security,
            "distance_impact": distance_impact
        },

        "recommendation": recommendation,
        "reason": reason
    }


def analyze_all_orders():

    results = []

    for order in orders:

        results.append(
            analyze_order(
                order["order_id"]
            )
        )

    return results
