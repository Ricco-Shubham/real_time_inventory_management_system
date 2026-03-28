import streamlit as st
from utils.UserObject import Admin

def render_admin_login():
    st.markdown("## Admin Portal")
    st.markdown("### 🔑 Secure Login")

    with st.form("admin_login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            if username == "admin" and password == "admin@123":
                st.session_state.user_type = "admin"
                st.session_state.is_logged_in = True
                st.session_state.current_page = "admin_dashboard"
                st.query_params["user_type"] = "admin"
                st.query_params["is_logged_in"] = "true"
                st.rerun()
            else:
                st.error("Invalid admin credentials.")
