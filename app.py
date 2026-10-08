from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin9876",  # Confirm karo ki aapka MySQL Password yahi hai
        database="restaurant_pos"
    )

# 1. API: Fetch Menu Items
@app.route('/api/menu', methods=['GET'])
def get_menu():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT m.item_id, m.name, m.price, c.name as category FROM menu_items m JOIN categories c ON m.category_id = c.category_id"
        cursor.execute(query)
        menu = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(menu), 200
    except Exception as e:
        print("Detailed Menu Error:", str(e))
        return jsonify({"error": str(e)}), 500

# 2. API: Create Order
@app.route('/api/orders', methods=['POST'])
def create_order():
    try:
        data = request.json
        items = data.get('items', [])
        payment_mode = data.get('payment_mode', 'UPI')
        order_type = data.get('order_type', 'Dine-In')
        table_no = data.get('table_no', 'Table 1')

        if not items:
            return jsonify({"error": "Cart is empty"}), 400

        subtotal = sum(float(item['price']) * int(item['qty']) for item in items)
        gst_amount = round(subtotal * 0.05, 2)
        grand_total = round(subtotal + gst_amount, 2)

        conn = get_db_connection()
        cursor = conn.cursor()

        order_query = """
            INSERT INTO orders (order_type, payment_mode, subtotal, gst_amount, grand_total, status, table_no, kitchen_status)
            VALUES (%s, %s, %s, %s, %s, 'Paid', %s, 'Preparing')
        """
        cursor.execute(order_query, (order_type, payment_mode, subtotal, gst_amount, grand_total, table_no))
        order_id = cursor.lastrowid

        item_query = "INSERT INTO order_items (order_id, item_id, quantity, price) VALUES (%s, %s, %s, %s)"
        for item in items:
            cursor.execute(item_query, (order_id, item['item_id'], item['qty'], item['price']))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Order placed successfully!", "invoice": {"order_id": order_id, "grand_total": grand_total}}), 201
    except Exception as e:
        print("Detailed Order Error:", str(e))
        return jsonify({"error": str(e)}), 500

# 3. API: Kitchen Orders
@app.route('/api/kitchen/orders', methods=['GET'])
def get_kitchen_orders():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT o.order_id, o.table_no, o.order_type, o.created_at, 
                   oi.quantity, m.name as item_name
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN menu_items m ON oi.item_id = m.item_id
            WHERE o.kitchen_status = 'Preparing'
            ORDER BY o.order_id ASC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        orders_dict = {}
        for row in rows:
            oid = row['order_id']
            if oid not in orders_dict:
                orders_dict[oid] = {
                    "order_id": oid,
                    "table_no": row['table_no'],
                    "order_type": row['order_type'],
                    "time": str(row['created_at']),
                    "items": []
                }
            orders_dict[oid]["items"].append(f"{row['quantity']}x {row['item_name']}")

        cursor.close()
        conn.close()
        return jsonify(list(orders_dict.values())), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 4. API: Mark Order Ready
@app.route('/api/kitchen/complete/<int:order_id>', methods=['POST'])
def complete_kitchen_order(order_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE orders SET kitchen_status = 'Ready' WHERE order_id = %s", (order_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Order marked as Ready!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 5. API: Reports
@app.route('/api/reports', methods=['GET'])
def get_reports():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        summary_query = """
            SELECT 
                COUNT(order_id) as total_orders,
                COALESCE(SUM(subtotal), 0) as total_sales,
                COALESCE(SUM(gst_amount), 0) as total_gst,
                COALESCE(SUM(grand_total), 0) as total_revenue
            FROM orders
        """
        cursor.execute(summary_query)
        summary = cursor.fetchone()

        items_query = """
            SELECT 
                m.name, 
                SUM(oi.quantity) as total_qty, 
                SUM(oi.quantity * oi.price) as item_revenue
            FROM order_items oi
            JOIN menu_items m ON oi.item_id = m.item_id
            GROUP BY m.name
            ORDER BY total_qty DESC
        """
        cursor.execute(items_query)
        top_items = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            "summary": summary,
            "items": top_items
        }), 200
    except Exception as e:
        print("Detailed Reports Error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)