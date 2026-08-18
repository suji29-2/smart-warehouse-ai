# ============================================
# SMARTWAREHOUSE AI
# DATA
# ============================================

# ============================================
# INVENTORY
# ============================================

inventory = [
    {
        "id": 1,
        "name": "Laptop Pro 15",
        "sku": "LAP-15",
        "category": "Electronics",
        "stock": 25,
        "reserved": 8,
        "available_stock": 17,
        "reorder_level": 10,
        "warehouse": "Main Warehouse",
        "status": "HEALTHY"
    },
    {
        "id": 2,
        "name": "Wireless Mouse",
        "sku": "MOU-01",
        "category": "Accessories",
        "stock": 50,
        "reserved": 12,
        "available_stock": 38,
        "reorder_level": 15,
        "warehouse": "Main Warehouse",
        "status": "HEALTHY"
    },
    {
        "id": 3,
        "name": "Keyboard Pro",
        "sku": "KEY-02",
        "category": "Accessories",
        "stock": 30,
        "reserved": 5,
        "available_stock": 25,
        "reorder_level": 10,
        "warehouse": "Main Warehouse",
        "status": "HEALTHY"
    },
    {
        "id": 4,
        "name": "Monitor 24",
        "sku": "MON-24",
        "category": "Electronics",
        "stock": 15,
        "reserved": 4,
        "available_stock": 11,
        "reorder_level": 8,
        "warehouse": "Main Warehouse",
        "status": "HEALTHY"
    }
]


# ============================================
# ORDERS
# ============================================

orders = [
    {
        "order_id": "WP-4029",
        "product": "Laptop Pro 15",
        "sku": "LAP-15",
        "required_quantity": 10,
        "customer": "TechNova Pvt Ltd",
        "customer_priority": "PLATINUM",
        "business_impact": 95,
        "sla_urgency": 75,
        "distance_impact": 40,
        "status": "AT_RISK"
    },
    {
        "order_id": "WP-4030",
        "product": "Laptop Pro 15",
        "sku": "LAP-15",
        "required_quantity": 5,
        "customer": "Digital Solutions",
        "customer_priority": "GOLD",
        "business_impact": 70,
        "sla_urgency": 45,
        "distance_impact": 30,
        "status": "NORMAL"
    },
    {
        "order_id": "WP-4031",
        "product": "Wireless Mouse",
        "sku": "MOU-01",
        "required_quantity": 15,
        "customer": "Retail Hub",
        "customer_priority": "SILVER",
        "business_impact": 50,
        "sla_urgency": 35,
        "distance_impact": 25,
        "status": "NORMAL"
    },
    {
        "order_id": "WP-4032",
        "product": "Monitor 24",
        "sku": "MON-24",
        "required_quantity": 8,
        "customer": "Enterprise Systems",
        "customer_priority": "GOLD",
        "business_impact": 80,
        "sla_urgency": 60,
        "distance_impact": 35,
        "status": "NORMAL"
    }
]


# ============================================
# PRODUCT FUNCTIONS
# ============================================

def get_product_by_sku(sku):

    for product in inventory:

        if product["sku"] == sku:
            return product

    return None


# ============================================
# ORDER FUNCTIONS
# ============================================

def get_order_by_id(order_id):

    for order in orders:

        if order["order_id"] == order_id:
            return order

    return None


def get_order(order_id):

    return get_order_by_id(order_id)


# ============================================
# API HELPERS
# ============================================

def get_inventory():

    return inventory


def get_orders():

    return orders


# ============================================
# INVENTORY SUMMARY
# ============================================

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


def get_inventory_summary():

    return inventory_summary()


# ============================================
# ADD STOCK
# ============================================

def add_stock(sku, quantity):

    product = get_product_by_sku(sku)

    if product is None:

        return {
            "success": False,
            "message": "Product not found"
        }

    quantity = int(quantity)

    if quantity <= 0:

        return {
            "success": False,
            "message": "Quantity must be greater than 0"
        }

    product["stock"] += quantity

    product["available_stock"] += quantity

    if product["available_stock"] <= 3:

        product["status"] = "CRITICAL"

    elif product["available_stock"] <= product["reorder_level"]:

        product["status"] = "WARNING"

    else:

        product["status"] = "HEALTHY"

    return {
        "success": True,
        "message": f"{quantity} units added successfully",
        "product": product
    }