from flask import Flask, jsonify, request
from flask_cors import CORS

from data import (
    inventory,
    orders,
    get_inventory,
    get_orders,
    get_order,
    get_inventory_summary,
    add_stock,
    get_product_by_sku
)

from decision import analyze_order


app = Flask(__name__)
CORS(app)


# ============================================================
# SMARTWAREHOUSE AI
# BACKEND SERVER
# ============================================================

print("""
======================================
   SMARTWAREHOUSE AI
   Backend Server
======================================
Server: http://127.0.0.1:5000
Status: ONLINE
======================================
""")


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return jsonify({
        "success": True,
        "message": "SmartWarehouse AI Backend is Online"
    })


# ============================================================
# INVENTORY
# ============================================================

@app.route("/api/inventory", methods=["GET"])
def inventory_api():

    return jsonify(get_inventory())


# ============================================================
# INVENTORY SUMMARY
# ============================================================

@app.route("/api/inventory/summary", methods=["GET"])
def inventory_summary_api():

    return jsonify(
        get_inventory_summary()
    )


# ============================================================
# ADD STOCK
# ============================================================

@app.route("/api/inventory/add", methods=["POST"])
def add_stock_api():

    data = request.get_json() or {}

    sku = data.get("sku")
    quantity = data.get("quantity")

    if not sku:
        return jsonify({
            "success": False,
            "message": "Product SKU is required"
        }), 400

    if quantity is None:
        return jsonify({
            "success": False,
            "message": "Quantity is required"
        }), 400

    try:
        quantity = int(quantity)
    except:

        return jsonify({
            "success": False,
            "message": "Enter a valid quantity"
        }), 400

    result = add_stock(
        sku,
        quantity
    )

    return jsonify(result)


# ============================================================
# ORDERS
# ============================================================

@app.route("/api/orders", methods=["GET"])
def orders_api():

    return jsonify(get_orders())


# ============================================================
# SINGLE ORDER
# ============================================================

@app.route("/api/orders/<order_id>", methods=["GET"])
def single_order_api(order_id):

    order = get_order(order_id)

    if order is None:

        return jsonify({
            "success": False,
            "message": "Order not found"
        }), 404

    return jsonify(order)


# ============================================================
# AI ORDER ANALYSIS
# ============================================================

@app.route(
    "/api/orders/<order_id>/analysis",
    methods=["GET"]
)
def order_analysis_api(order_id):

    order = get_order(order_id)

    if order is None:

        return jsonify({
            "success": False,
            "message": "Order not found"
        }), 404

    try:

        result = analyze_order(
            order_id
        )

        return jsonify(result)

    except Exception as e:

        return jsonify({

            "success": False,

            "message":
            "AI analysis failed",

            "error":
            str(e)

        }), 500


# ============================================================
# CREATE NEW ORDER
# ============================================================

@app.route(
    "/api/orders/create",
    methods=["POST"]
)
def create_order():

    data = request.get_json() or {}


    # --------------------------------------------------------
    # GET DATA
    # --------------------------------------------------------

    product_sku = data.get(
        "product_sku"
    )

    quantity = data.get(
        "quantity"
    )

    customer = data.get(
        "customer",
        "Unknown Customer"
    )

    priority = data.get(
        "priority",
        "SILVER"
    )

    sla = data.get(
        "sla",
        "NORMAL"
    )

    price = data.get(
        "price",
        0
    )


    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if not product_sku:

        return jsonify({

            "success": False,

            "message":
            "Please select a product"

        }), 400


    try:

        quantity = int(
            quantity
        )

        price = float(
            price
        )

    except:

        return jsonify({

            "success": False,

            "message":
            "Enter valid quantity and price"

        }), 400


    if quantity <= 0:

        return jsonify({

            "success": False,

            "message":
            "Quantity must be greater than 0"

        }), 400


    if price < 0:

        return jsonify({

            "success": False,

            "message":
            "Price cannot be negative"

        }), 400


    # --------------------------------------------------------
    # FIND PRODUCT
    # --------------------------------------------------------

    product = get_product_by_sku(
        product_sku
    )


    if product is None:

        return jsonify({

            "success": False,

            "message":
            "Product not found"

        }), 404


    # --------------------------------------------------------
    # GENERATE ORDER ID
    # --------------------------------------------------------

    highest_id = 4032


    for order in orders:

        try:

            number = int(
                order["order_id"]
                .replace("WP-", "")
            )

            highest_id = max(
                highest_id,
                number
            )

        except:

            pass


    new_order_id = (
        f"WP-{highest_id + 1}"
    )


    # --------------------------------------------------------
    # BUSINESS IMPACT
    # --------------------------------------------------------

    if priority == "PLATINUM":

        business_impact = 95

    elif priority == "GOLD":

        business_impact = 75

    else:

        business_impact = 50


    # --------------------------------------------------------
    # SLA URGENCY
    # --------------------------------------------------------

    if sla == "CRITICAL":

        sla_urgency = 95

    elif sla == "URGENT":

        sla_urgency = 75

    else:

        sla_urgency = 40


    # --------------------------------------------------------
    # STOCK CHECK
    # --------------------------------------------------------

    available_stock = int(
        product.get(
            "available_stock",
            product.get("stock", 0)
        )
    )


    if quantity > available_stock:

        status = "AT_RISK"

    elif quantity >= available_stock * 0.7:

        status = "WARNING"

    else:

        status = "NORMAL"


    # --------------------------------------------------------
    # CREATE ORDER
    # --------------------------------------------------------

    new_order = {

        "order_id":
        new_order_id,

        "product":
        product["name"],

        "sku":
        product["sku"],

        "required_quantity":
        quantity,

        "customer":
        customer,

        "customer_priority":
        priority,

        "business_impact":
        business_impact,

        "sla_urgency":
        sla_urgency,

        "distance_impact":
        30,

        "price":
        price,

        "total":
        price * quantity,

        "sla":
        sla,

        "status":
        status

    }


    orders.append(
        new_order
    )


    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return jsonify({

        "success":
        True,

        "message":
        f"Order {new_order_id} created successfully",

        "order":
        new_order,

        "stock_available":
        available_stock,

        "stock_required":
        quantity,

        "risk":
        status

    })


# ============================================================
# DECISION
# ============================================================

@app.route(
    "/api/decision",
    methods=["POST"]
)
def decision_api():

    data = request.get_json() or {}


    order_id = data.get(
        "order_id"
    )

    action = data.get(
        "action"
    )

    allocation = data.get(
        "allocation"
    )


    if not order_id:

        return jsonify({

            "success": False,

            "message":
            "Order ID is required"

        }), 400


    order = get_order(
        order_id
    )


    if order is None:

        return jsonify({

            "success": False,

            "message":
            "Order not found"

        }), 404


    # --------------------------------------------------------
    # REJECT
    # --------------------------------------------------------

    if action == "reject":

        order["status"] = "REJECTED"


        return jsonify({

            "success":
            True,

            "message":
            "Decision recorded successfully",

            "action":
            "REJECTED"

        })


    # --------------------------------------------------------
    # ALLOCATION
    # --------------------------------------------------------

    if action == "modify":

        try:

            allocation = int(
                allocation
            )

        except:

            return jsonify({

                "success": False,

                "message":
                "Invalid allocation"

            }), 400

    else:

        allocation = int(
            order.get(
                "required_quantity",
                0
            )
        )


    if allocation <= 0:

        return jsonify({

            "success": False,

            "message":
            "Allocation must be greater than 0"

        }), 400


    # --------------------------------------------------------
    # FIND PRODUCT
    # --------------------------------------------------------

    product = get_product_by_sku(
        order["sku"]
    )


    if product is None:

        return jsonify({

            "success": False,

            "message":
            "Product not found"

        }), 404


    available = int(
        product.get(
            "available_stock",
            0
        )
    )


    # --------------------------------------------------------
    # CHECK STOCK
    # --------------------------------------------------------

    if allocation > available:

        return jsonify({

            "success":
            False,

            "message":
            f"Only {available} units are available"

        }), 400


    # --------------------------------------------------------
    # APPROVE / MODIFY
    # --------------------------------------------------------

    product["available_stock"] -= allocation

    product["reserved"] += allocation


    if product["available_stock"] <= 3:

        product["status"] = "CRITICAL"

    elif product["available_stock"] <= product["reorder_level"]:

        product["status"] = "WARNING"

    else:

        product["status"] = "HEALTHY"


    order["status"] = "ALLOCATED"

    order["allocated_quantity"] = allocation


    return jsonify({

        "success":
        True,

        "message":
        "Decision recorded successfully",

        "order":
        order,

        "inventory":
        product

    })


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )