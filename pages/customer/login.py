import streamlit as st
import bcrypt
from utils.DataBase import database
from utils.UserObject import Customer

def render_login():
    st.markdown("## Customer Portal")
    st.markdown("### 🔑 Login")

    with st.form("cust_login_form"):
        phone = st.text_input("Phone Number")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            if not phone or not password:
                st.error("Please fill all fields.")
            else:
                c1 = Customer()
                c1.phone_no = phone
                if c1.verify_password(password):
                    # Fetch extra details to store in session
                    try:
                        query = f"SELECT customer_id, name FROM customers WHERE phone_no = '{phone}'"
                        result = database.execute_query(query)
                        if result:
                            st.session_state.customer_id = result[0][0]
                            st.session_state.username = result[0][1]
                            st.session_state.phone_no = phone
                            st.session_state.is_logged_in = True
                            st.session_state.current_page = "grocery"
                            st.query_params["user_type"] = "customer"
                            st.query_params["is_logged_in"] = "true"
                            st.query_params["customer_id"] = str(result[0][0])
                            st.query_params["username"] = result[0][1]
                            st.query_params["phone_no"] = phone
                            st.rerun()
                        else:
                            st.error("User not found in DB.")
                    except Exception as e:
                        st.error(f"Database error: {e}")
                else:
                    st.error("Invalid phone number or password.")

    if st.button("Don't have an account? Sign Up"):
        st.session_state.current_page = "customer_signup"
        st.rerun()


def render_signup():
    st.markdown("## Customer Portal")
    st.markdown("### 📝 Sign Up")

    with st.form("cust_signup_form"):
        name = st.text_input("Full Name")
        address = st.text_area("Address")
        pincode = st.text_input("Pincode")
        phone = st.text_input("Phone Number")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        submit = st.form_submit_button("Sign Up")

        if submit:
            if not all([name, address, pincode, phone, password, confirm_password]):
                st.error("Please fill all fields.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            else:
                # Check if phone already registered
                query = f"SELECT name FROM customers WHERE phone_no = '{phone}'"
                result = database.execute_query(query)
                if result:
                    st.error("Phone number already registered. Please log in.")
                else:
                    # Hash password and insert
                    salt = bcrypt.gensalt()
                    pwd_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
                    insert_query = f"""
                    INSERT INTO customers (name, address, pincode, phone_no, password_hash)
                    VALUES ('{name}', '{address}', '{pincode}', '{phone}', '{pwd_hash}')
                    """
                    try:
                        database.execute_query(insert_query)
                        st.success("Sign Up successful! Please login.")
                        st.session_state.current_page = "customer_login"
                    except Exception as e:
                        st.error(f"Error creating account: {e}")

    if st.button("Already have an account? Login"):
        st.session_state.current_page = "customer_login"
        st.rerun()
