import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Inventory Management System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Shared CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Hide default streamlit chrome on landing */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Card-style containers */
.landing-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border: 1px solid #0f3460;
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    transition: transform 0.2s, box-shadow 0.2s;
    cursor: pointer;
}
.landing-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 32px rgba(0, 212, 255, 0.2);
}

/* Status badge helpers (used across pages) */
.badge-pending   { background:#f59e0b; color:#000; padding:2px 10px; border-radius:99px; font-size:12px; font-weight:600; }
.badge-dispatched{ background:#10b981; color:#fff; padding:2px 10px; border-radius:99px; font-size:12px; font-weight:600; }
.badge-cancelled { background:#ef4444; color:#fff; padding:2px 10px; border-radius:99px; font-size:12px; font-weight:600; }

/* Sidebar nav styling */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #161b22 100%);
}
</style>
""", unsafe_allow_html=True)

# ── Session state bootstrap ───────────────────────────────────────────────────
defaults = {
    "user_type": None,        # "customer" | "admin"
    "is_logged_in": False,
    "customer_id": None,
    "phone_no": None,
    "username": None,
    "current_page": "home",   # internal page router
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Sidebar navigation ────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("## 📦 Inventory System")
        st.divider()

        if st.session_state.user_type == "customer" and st.session_state.is_logged_in:
            st.markdown(f"👤 **{st.session_state.username or 'Customer'}**")
            pages = {
                "🛒 Browse Grocery": "grocery",
                "🛍️ My Cart": "cart",
                "📋 My Orders": "orders",
                "👤 Profile": "profile",
            }
            for label, page in pages.items():
                if st.button(label, key=f"nav_{page}", use_container_width=True):
                    st.session_state.current_page = page
                    st.rerun()
            st.divider()
            if st.button("🚪 Logout", use_container_width=True):
                for k in ["user_type", "is_logged_in", "customer_id", "phone_no", "username"]:
                    st.session_state[k] = None if k != "is_logged_in" else False
                st.session_state.current_page = "home"
                st.rerun()

        elif st.session_state.user_type == "admin" and st.session_state.is_logged_in:
            st.markdown("🔑 **Admin**")
            pages = {
                "📊 Dashboard": "admin_dashboard",
                "📦 Manage Products": "admin_products",
                "🚚 Manage Orders": "admin_orders",
                "💡 Insights Report": "admin_insights",
            }
            for label, page in pages.items():
                if st.button(label, key=f"nav_{page}", use_container_width=True):
                    st.session_state.current_page = page
                    st.rerun()
            st.divider()
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.user_type = None
                st.session_state.is_logged_in = False
                st.session_state.current_page = "home"
                st.rerun()


# ── Landing page ──────────────────────────────────────────────────────────────
def render_landing():
    st.markdown("""
    <div style="text-align:center; padding: 3rem 0 2rem;">
        <h1 style="font-size:3rem; background: linear-gradient(90deg,#00d4ff,#0f3460);
                   -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            📦 Inventory Management System
        </h1>
        <p style="color:#8b949e; font-size:1.15rem; margin-top:0.5rem;">
            Real-Time Tracking · Smart Insights · Seamless Orders
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, spacer, col2 = st.columns([1, 0.15, 1])

    with col1:
        st.markdown("""
        <div class="landing-card">
            <div style="font-size:4rem;">🛒</div>
            <h2 style="color:#00d4ff; margin:0.5rem 0;">Customer Portal</h2>
            <p style="color:#8b949e;">Browse products, manage your cart, track orders and download bills.</p>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔑 Login", key="cust_login", use_container_width=True):
                st.session_state.user_type = "customer"
                st.session_state.current_page = "customer_login"
                st.rerun()
        with c2:
            if st.button("📝 Sign Up", key="cust_signup", use_container_width=True):
                st.session_state.user_type = "customer"
                st.session_state.current_page = "customer_signup"
                st.rerun()

    with col2:
        st.markdown("""
        <div class="landing-card">
            <div style="font-size:4rem;">🔑</div>
            <h2 style="color:#7c3aed; margin:0.5rem 0;">Admin Portal</h2>
            <p style="color:#8b949e;">Monitor KPIs, manage inventory, dispatch orders and generate insights.</p>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        _, mid, _ = st.columns([0.5, 1, 0.5])
        with mid:
            if st.button("🔑 Admin Login", key="admin_login_btn", use_container_width=True):
                st.session_state.user_type = "admin"
                st.session_state.current_page = "admin_login"
                st.rerun()


# ── Page router ───────────────────────────────────────────────────────────────
def main():
    render_sidebar()
    page = st.session_state.current_page

    if page == "home":
        render_landing()

    # ── Customer auth ──
    elif page == "customer_login":
        from pages.customer.login import render_login
        render_login()
    elif page == "customer_signup":
        from pages.customer.login import render_signup
        render_signup()

    # ── Customer pages ──
    elif page == "profile":
        from pages.customer.profile import render_profile
        render_profile()
    elif page == "grocery":
        from pages.customer.grocery import render_grocery
        render_grocery()
    elif page == "cart":
        from pages.customer.cart import render_cart
        render_cart()
    elif page == "orders":
        from pages.customer.orders import render_orders
        render_orders()

    # ── Admin auth ──
    elif page == "admin_login":
        from pages.admin.login import render_admin_login
        render_admin_login()

    # ── Admin pages ──
    elif page == "admin_dashboard":
        from pages.admin.dashboard import render_dashboard
        render_dashboard()
    elif page == "admin_products":
        from pages.admin.products import render_products
        render_products()
    elif page == "admin_orders":
        from pages.admin.orders import render_orders as render_admin_orders
        render_admin_orders()
    elif page == "admin_insights":
        from pages.admin.insights import render_insights
        render_insights()
    else:
        render_landing()


if __name__ == "__main__":
    main()
