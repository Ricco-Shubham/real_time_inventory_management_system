import streamlit as st
import bcrypt
from utils.DataBase import database

def render_profile():
    st.markdown("## 👤 User Profile")

    if not st.session_state.get('is_logged_in') or st.session_state.get('user_type') != "customer":
        st.warning("Please login to view profile.")
        return

    phone = st.session_state.phone_no
    query = f"SELECT customer_id, name, address, pincode, phone_no FROM customers WHERE phone_no = '{phone}'"
    result = database.execute_query(query)

    if not result:
        st.error("Failed to load profile.")
        return

    c_id, c_name, c_addr, c_pin, c_phone = result[0]

    st.markdown(f"**Customer ID:** {c_id}")

    with st.expander("📝 Edit Profile Details", expanded=True):
        with st.form("edit_profile_form"):
            new_name = st.text_input("Name", value=c_name)
            new_address = st.text_area("Address", value=c_addr)
            new_pin = st.text_input("Pincode", value=c_pin)
            new_phone = st.text_input("Phone Number", value=c_phone)

            st.markdown("#### Change Password (Optional)")
            new_pwd = st.text_input("New Password", type="password")
            confirm_pwd = st.text_input("Confirm New Password", type="password")

            submit = st.form_submit_button("Save Changes")

            if submit:
                updates = []
                if new_name != c_name: updates.append(f"name = '{new_name}'")
                if new_address != c_addr: updates.append(f"address = '{new_address}'")
                if new_pin != c_pin: updates.append(f"pincode = '{new_pin}'")
                if new_phone != c_phone: updates.append(f"phone_no = '{new_phone}'")

                if new_pwd:
                    if new_pwd != confirm_pwd:
                        st.error("New passwords do not match.")
                        return
                    salt = bcrypt.gensalt()
                    pwd_hash = bcrypt.hashpw(new_pwd.encode('utf-8'), salt).decode('utf-8')
                    updates.append(f"password_hash = '{pwd_hash}'")

                if updates:
                    update_query = f"UPDATE customers SET {', '.join(updates)} WHERE phone_no = '{phone}'"
                    try:
                        database.execute_query(update_query)
                        st.success("Profile updated successfully!")
                        st.session_state.phone_no = new_phone
                        st.session_state.username = new_name
                    except Exception as e:
                        st.error(f"Error updating profile: {e}")
                else:
                    st.info("No changes detected.")
