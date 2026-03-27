import streamlit as st
import pandas as pd
import os
from utils.DataBase import database
from utils.insightsgenerator import DataInsightsReport

def render_orders():
    st.markdown("## 📋 My Orders")

    if not st.session_state.get('is_logged_in') or st.session_state.get('user_type') != "customer":
        st.warning("Please login to view orders.")
        return

    c_id = st.session_state.customer_id

    # Fetch orders
    query = f"""
    SELECT order_id, order_timestamp, order_status, total_amount_paid 
    FROM orders WHERE customer_id = {c_id} ORDER BY order_timestamp DESC
    """
    orders = database.execute_query(query)

    if not orders:
        st.info("You have no order history.")
        return

    # Display each order as an expander
    for order in orders:
        o_id, o_ts, o_status, o_total = order
        
        # Color code status
        status_color = "red" if o_status == "cancelled" else "green" if o_status == "dispatched" else "orange"
        
        with st.expander(f"Order #{o_id} - {o_ts.strftime('%d %b %Y, %I:%M %p')} | Total: ₹{o_total} | Status: :{status_color}[{o_status.upper()}]"):
            # Fetch items for this order
            item_q = f"SELECT item_id, name, quantity, amount_paid FROM order_items WHERE order_id = {o_id}"
            items = database.execute_query(item_q)
            
            if items:
                df = pd.DataFrame(items, columns=["Item ID", "Name", "Qty", "Total Paid (₹)"])
                st.dataframe(df, hide_index=True, use_container_width=True)

            col1, col2 = st.columns(2)
            
            with col1:
                # Cancel order button (only if pending)
                if o_status == "pending":
                    if st.button(f"Cancel Order #{o_id}", key=f"cancel_{o_id}", type="primary"):
                        try:
                            # Update order status
                            database.execute_query(f"UPDATE orders SET order_status = 'cancelled' WHERE order_id = {o_id}")
                            # Refund inventory logic (if needed, but originally wasn't in UserObject explicitly other than status update)
                            # To be safe, we'll restore inventory
                            for it in items:
                                it_id, _, it_qty, _ = it
                                database.execute_query(f"UPDATE zepto_v2 SET quantity = quantity + {it_qty} WHERE item_id = '{it_id}'")
                            
                            st.success(f"Order #{o_id} cancelled.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error cancelling order: {e}")
                elif o_status == "dispatched":
                    st.info("Order dispatched. Cannot be cancelled.")
                elif o_status == "cancelled":
                    st.error("Order is cancelled.")

            with col2:
                # Generate Bill PDF
                if st.button(f"📄 Generate Bill for #{o_id}", key=f"bill_{o_id}"):
                    with st.spinner("Generating PDF..."):
                        DataInsightsReport().generate_bill(o_id, c_id)
                        
                        # Use absolute path to the generated bill, as per insightsgenerator
                        base_dir = os.path.dirname(os.path.abspath(__file__))
                        bill_path = os.path.join(base_dir, "..", "..", "order_bills", f"Bill_{o_id}.pdf")
                        
                        if os.path.exists(bill_path):
                            with open(bill_path, "rb") as f:
                                pdf_bytes = f.read()
                            st.download_button(
                                label="⬇️ Download Bill PDF",
                                data=pdf_bytes,
                                file_name=f"Bill_Order_{o_id}.pdf",
                                mime="application/pdf"
                            )
                        else:
                            st.error("Failed to generate bill or locate the file.")
