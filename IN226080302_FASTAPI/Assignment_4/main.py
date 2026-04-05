from fastapi import FastAPI, HTTPException

app = FastAPI()

# ---------------- PRODUCTS ----------------
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "in_stock": False},  # Out of stock
    {"id": 4, "name": "Pen Set", "price": 49, "in_stock": True}
]

cart = []
orders = []


# ---------------- HELPER ----------------
def calculate_total(product, quantity):
    return product["price"] * quantity


def find_product(product_id):
    for p in products:
        if p["id"] == product_id:
            return p
    return None


# ---------------- ADD TO CART ----------------
@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int = 1):

    product = find_product(product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not product["in_stock"]:
        raise HTTPException(
            status_code=400,
            detail=f"{product['name']} is out of stock"
        )

    # Check if already in cart
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = calculate_total(product, item["quantity"])
            return {
                "message": "Cart updated",
                "cart_item": item
            }

    # New item
    new_item = {
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": calculate_total(product, quantity)
    }

    cart.append(new_item)

    return {
        "message": "Added to cart",
        "cart_item": new_item
    }


# ---------------- VIEW CART ----------------
@app.get("/cart")
def get_cart():
    if not cart:
        return {"message": "Cart is empty"}

    grand_total = sum(item["subtotal"] for item in cart)

    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": grand_total
    }


# ---------------- REMOVE ITEM ----------------
@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):
    for item in cart:
        if item["product_id"] == product_id:
            cart.remove(item)
            return {"message": "Item removed from cart"}

    raise HTTPException(status_code=404, detail="Item not in cart")


# ---------------- CHECKOUT ----------------
@app.post("/cart/checkout")
def checkout(customer_name: str, delivery_address: str):

    if not cart:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty — add items first"
        )

    grand_total = sum(item["subtotal"] for item in cart)

    new_orders = []

    for item in cart:
        order = {
            "order_id": len(orders) + 1,
            "customer_name": customer_name,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "total_price": item["subtotal"],
            "delivery_address": delivery_address
        }
        orders.append(order)
        new_orders.append(order)

    cart.clear()

    return {
        "message": "Order placed successfully",
        "orders_placed": new_orders,
        "grand_total": grand_total
    }


# ---------------- VIEW ORDERS ----------------
@app.get("/orders")
def get_orders():
    return {
        "orders": orders,
        "total_orders": len(orders)
    }