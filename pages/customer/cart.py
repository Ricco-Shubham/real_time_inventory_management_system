import streamlit as st
import pandas as pd
from utils.DataBase import database

def render_cart():
    st.markdown("## 🛍️ My Cart")

    if not st.session_state.get('is_logged_in') or st.session_state.get('user_type') != "customer":
        st.warning("Please login to view cart.")
        return

    c_id = st.session_state.customer_id

    # Fetch cart items
    query = f"""
    SELECT item_id, name, quantity, price 
    FROM cart_details WHERE customer_id = {c_id}
    """
    cart_items = database.execute_query(query)

    if not cart_items:
        st.info("Your cart is empty. Go to Browse Grocery to add items.")
        return

    # Display cart
    df = pd.DataFrame(cart_items, columns=["Item ID", "Product Name", "Quantity", "Price (₹)"])
    df["Subtotal (₹)"] = df["Quantity"] * df["Price (₹)"]
    st.table(df)

    total_price = df["Subtotal (₹)"].sum()
    st.markdown(f"### Total Price: **₹{total_price:,.2f}**")

    # Actions col
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Remove Item")
        with st.form("remove_item_form"):
            rem_id = st.text_input("Enter Item ID to remove")
            rem_btn = st.form_submit_button("Remove from Cart")

            if rem_btn and rem_id:
                # Need to return quantity to zepto_v2 inventory
                rem_chk = f"SELECT quantity FROM cart_details WHERE customer_id = {c_id} AND item_id = '{rem_id}' LIMIT 1"
                chk_res = database.execute_query(rem_chk)
                
                if chk_res:
                    qty_to_return = chk_res[0][0]
                    # Restore inventory
                    restore_q = f"UPDATE zepto_v2 SET quantity = quantity + {qty_to_return} WHERE item_id = '{rem_id}'"
                    # Delete from cart
                    del_q = f"DELETE FROM cart_details WHERE customer_id = {c_id} AND item_id = '{rem_id}'"
                    try:
                        database.execute_query(restore_q)
                        database.execute_query(del_q)
                        st.success(f"Item {rem_id} removed.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error removing item: {e}")
                else:
                    st.error("Item ID not found in your cart.")

    with col2:
        st.markdown("#### Checkout")
        if st.button("🛍️ Purchase Order", type="primary", use_container_width=True):
            try:
                # 1. Create order
                order_q = f"""
                INSERT INTO orders (customer_id, order_status, total_amount_paid) 
                VALUES ({c_id}, 'pending', {total_price})
                """
                database.execute_query(order_q)

                # Fetch order_id
                oid_q = f'SELECT order_id FROM orders WHERE customer_id = {c_id} ORDER BY order_timestamp DESC LIMIT 1'
                new_oid = database.execute_query(oid_q)[0][0]

                # 2. Create order_items
                for item in cart_items:
                    item_id, name, qty, price = item
                    subtotal = qty * price
                    oi_q = f"""
                    INSERT INTO order_items (order_id, item_id, name, quantity, amount_paid) 
                    VALUES ({new_oid}, '{item_id}', '{name}', {qty}, {subtotal})
                    """
                    database.execute_query(oi_q)

                # 3. Clear cart
                database.execute_query(f"DELETE FROM cart_details WHERE customer_id = {c_id}")
                
                st.success(f"Order placed successfully! Order ID: {new_oid}")
                st.balloons()
                st.rerun()
            except Exception as e:
                st.error(f"Error during checkout: {e}")
