import streamlit as st
import pandas as pd
from utils.DataBase import database

def render_products():
    st.markdown("## 📦 Manage Products")

    if not st.session_state.get('is_logged_in') or st.session_state.get('user_type') != "admin":
        st.warning("Unauthorized.")
        return

    # Fetch all products
    query = 'SELECT item_id, name, "Category", quantity, mrp, "discountedSellingPrice", "discountPercent" FROM zepto_v2 ORDER BY "Category", name'
    prods = database.execute_query(query)

    if prods:
        df = pd.DataFrame(prods, columns=["Item ID", "Name", "Category", "Qty", "MRP (₹)", "Selling Price (₹)", "Discount %"])
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown("### ✏️ Edit Product")
        with st.form("edit_product_form"):
            e_id = st.text_input("Enter Item ID to edit")
            e_field = st.selectbox("Field to Edit", ["name", "price", "quantity"])
            e_val = st.text_input("New Value")
            
            submit = st.form_submit_button("Update Product")

            if submit and e_id and e_val:
                try:
                    if e_field == "name":
                        up_q = f"UPDATE zepto_v2 SET name = '{e_val}' WHERE item_id = '{e_id}'"
                        database.execute_query(up_q)
                    
                    elif e_field == "quantity":
                        up_q = f"UPDATE zepto_v2 SET quantity = {int(e_val)} WHERE item_id = '{e_id}'"
                        database.execute_query(up_q)
                    
                    elif e_field == "price":
                        new_price = float(e_val)
                        # Calc new discount percent
                        mrp_q = f"SELECT mrp FROM zepto_v2 WHERE item_id = '{e_id}'"
                        mrp = database.execute_query(mrp_q)[0][0]
                        
                        disc_pct = ((mrp - new_price) / mrp) * 100 if new_price < mrp else 0
                        up_q = f'UPDATE zepto_v2 SET "discountedSellingPrice" = {int(new_price)}, "discountPercent" = {disc_pct} WHERE item_id = \'{e_id}\''
                        database.execute_query(up_q)

                    st.success(f"Product {e_id} updated successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error updating product: {e}")
    else:
        st.info("No products found in DB.")

