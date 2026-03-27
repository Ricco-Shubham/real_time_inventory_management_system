import streamlit as st
import pandas as pd
from utils.DataBase import database

def render_orders():
    st.markdown("## 🚚 Manage Orders")

    if not st.session_state.get('is_logged_in') or st.session_state.get('user_type') != "admin":
        st.warning("Unauthorized.")
        return

    # Fetch all orders
    query = """
    SELECT o.order_id, c.name, o.order_timestamp, o.total_amount_paid, o.order_status 
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    ORDER BY o.order_timestamp DESC
    """
    orders = database.execute_query(query)

    if orders:
        df = pd.DataFrame(orders, columns=["Order ID", "Customer Name", "Order Date", "Amount (₹)", "Status"])
        
        # Color status
        def style_status(val):
            if val == 'pending': color = '#f59e0b'
            elif val == 'dispatched': color = '#10b981'
            else: color = '#ef4444' # cancelled
            return f'color: {color}; font-weight: bold'
            
        st.dataframe(df.style.map(style_status, subset=['Status']), use_container_width=True, hide_index=True)

        st.markdown("### 📦 Dispatch Order")
        with st.form("dispatch_form"):
            d_id = st.text_input("Enter Order ID to dispatch")
            d_btn = st.form_submit_button("Dispatch")
            
            if d_btn and d_id:
                # Check status
                status_q = f"SELECT order_status FROM orders WHERE order_id = {d_id}"
                res = database.execute_query(status_q)
                
                if not res:
                    st.error("Order ID not found.")
                else:
                    status = res[0][0]
                    if status == "pending":
                        up_q = f"UPDATE orders SET order_status = 'dispatched' WHERE order_id = {d_id}"
                        try:
                            database.execute_query(up_q)
                            st.success(f"Order #{d_id} dispatched successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                    elif status == "dispatched":
                        st.info("Order is already dispatched.")
                    elif status == "cancelled":
                        st.error("Cannot dispatch a cancelled order.")
    else:
        st.info("No orders found in DB.")
