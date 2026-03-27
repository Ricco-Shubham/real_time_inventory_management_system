import streamlit as st
import pandas as pd
from utils.DataBase import database

def render_grocery():
    st.markdown("## 🛒 Browse Grocery")

    if not st.session_state.get('is_logged_in') or st.session_state.get('user_type') != "customer":
        st.warning("Please login to browse.")
        return

    # Fetch categories
    cat_query = 'SELECT DISTINCT("Category") FROM zepto_v2'
    categories_res = database.execute_query(cat_query)
    
    if not categories_res:
        st.info("No categories available.")
        return

    categories = [cat[0] for cat in categories_res if cat[0]]
    selected_cat = st.selectbox("Select a Category", categories)

    if selected_cat:
        prod_query = f"""
        SELECT item_id, name, quantity, "discountedSellingPrice" 
        FROM zepto_v2 WHERE "Category" = '{selected_cat}'
        ORDER BY name
        """
        products = database.execute_query(prod_query)
        
        if products:
            df = pd.DataFrame(products, columns=["Item ID", "Product Name", "Available Qty", "Price (₹)"])
            st.dataframe(df, hide_index=True, use_container_width=True)

            # Add to cart section
            st.markdown("### ➕ Add to Cart")
            with st.form("add_cart_form"):
                col1, col2 = st.columns(2)
                with col1:
                    item_id = st.text_input("Enter Item ID")
                with col2:
                    qty = st.number_input("Quantity", min_value=1, value=1, step=1)
                
                add_btn = st.form_submit_button("Add to Cart")

                if add_btn and item_id:
                    # Validate product
                    check_query = f'SELECT name, quantity, "discountedSellingPrice" FROM zepto_v2 WHERE item_id = \'{item_id}\''
                    res = database.execute_query(check_query)
                    
                    if not res:
                        st.error("Product not found! Please check the Item ID.")
                    else:
                        p_name, p_qty, p_price = res[0]
                        if p_qty <= 0:
                            st.error(f"'{p_name}' is currently out of stock.")
                        elif qty > p_qty:
                            st.error(f"Requested quantity exceeds available stock ({p_qty}).")
                        else:
                            # Add to cart
                            cart_query = f"""
                            INSERT INTO cart_details (customer_id, item_id, name, quantity, price) 
                            VALUES ({st.session_state.customer_id}, '{item_id}', '{p_name}', {qty}, {p_price})
                            """
                            # Update inventory
                            inv_query = f"""
                            UPDATE zepto_v2 SET quantity = quantity - {qty} 
                            WHERE item_id = '{item_id}'
                            """
                            try:
                                database.execute_query(cart_query)
                                database.execute_query(inv_query)
                                st.success(f"Added {qty}x '{p_name}' to cart!")
                            except Exception as e:
                                st.error(f"Error adding to cart: {e}")
        else:
            st.info("No products found in this category.")
