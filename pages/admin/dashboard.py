import streamlit as st
import pandas as pd
import plotly.express as px
from utils.DataBase import database

def render_dashboard():
    st.markdown("## 📊 Admin Dashboard")

    if not st.session_state.get('is_logged_in') or st.session_state.get('user_type') != "admin":
        st.warning("Unauthorized.")
        return

    # ── KPIs ──
    # 1. Total Products
    p_q = "SELECT COUNT(*) FROM zepto_v2"
    tot_prod = database.execute_query(p_q)[0][0]

    # 2. Total Orders
    o_q = "SELECT COUNT(*) FROM orders"
    tot_orders = database.execute_query(o_q)[0][0]

    # 3. Total Customers
    c_q = "SELECT COUNT(*) FROM customers"
    tot_cust = database.execute_query(c_q)[0][0]

    # 4. Total Revenue
    r_q = "SELECT SUM(total_amount_paid) FROM orders"
    tot_rev = database.execute_query(r_q)[0][0] or 0

    # 5. Low Stock
    ls_q = "SELECT COUNT(*) FROM zepto_v2 WHERE quantity < 10"
    low_stock = database.execute_query(ls_q)[0][0]

    # 6. Pending Orders
    po_q = "SELECT COUNT(*) FROM orders WHERE order_status = 'pending'"
    pend_orders = database.execute_query(po_q)[0][0]

    st.markdown("### Key Metrics")
    c1, c2, c3 = st.columns(3)
    c1.metric("📦 Total Products", f"{tot_prod:,}")
    c2.metric("🛒 Total Orders", f"{tot_orders:,}")
    c3.metric("👥 Total Customers", f"{tot_cust:,}")

    c4, c5, c6 = st.columns(3)
    c4.metric("💰 Total Revenue", f"₹{tot_rev:,.2f}")
    c5.metric("⚠️ Low Stock Items", low_stock, delta="-Critical" if low_stock > 0 else "Normal", delta_color="inverse")
    c6.metric("🔄 Pending Orders", pend_orders, delta="-Action Req" if pend_orders > 0 else "All Clear", delta_color="inverse")

    st.divider()

    # ── Plotly Charts ──
    st.markdown("### 📈 Visual Insights")

    # 1. Top 10 Selling Products (Bar)
    st.markdown("#### Top 10 Selling Products")
    top_q = """
        SELECT zv.name, SUM(oi.quantity) AS total_sold 
        FROM order_items oi 
        JOIN zepto_v2 zv ON oi.item_id = zv.item_id 
        GROUP BY zv.name 
        ORDER BY total_sold DESC LIMIT 10
    """
    top_data = database.execute_query(top_q)
    if top_data:
        df_top = pd.DataFrame(top_data, columns=["Product", "Sold"])
        fig_top = px.bar(df_top, x="Sold", y="Product", orientation='h', template="plotly_dark", color="Sold", color_continuous_scale="greens")
        fig_top.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_top, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        # 2. Revenue by Product (Top 10)
        st.markdown("#### Revenue Drivers")
        rev_q = """
            SELECT zv.name, SUM(oi.amount_paid) AS revenue 
            FROM order_items oi 
            JOIN zepto_v2 zv ON oi.item_id = zv.item_id 
            GROUP BY zv.name 
            ORDER BY revenue DESC LIMIT 10
        """
        rev_data = database.execute_query(rev_q)
        if rev_data:
            df_rev = pd.DataFrame(rev_data, columns=["Product", "Revenue"])
            fig_rev = px.bar(df_rev, x="Product", y="Revenue", template="plotly_dark", color="Revenue", color_continuous_scale="blues")
            st.plotly_chart(fig_rev, use_container_width=True)

        # 3. Monthly Sales Trend (Line)
        st.markdown("#### Monthly Sales Velocity")
        trend_q = """
            SELECT TO_CHAR(DATE_TRUNC('month', o.order_timestamp), 'YYYY-MM') AS month, SUM(oi.quantity) AS total_sold
            FROM orders o JOIN order_items oi ON o.order_id = oi.order_id
            GROUP BY month ORDER BY month
        """
        trend_data = database.execute_query(trend_q)
        if trend_data:
            df_trend = pd.DataFrame(trend_data, columns=["Month", "Units Sold"])
            fig_trend = px.line(df_trend, x="Month", y="Units Sold", markers=True, template="plotly_dark")
            fig_trend.update_traces(line_color="#10b981", line_width=4, marker_size=10)
            st.plotly_chart(fig_trend, use_container_width=True)

    with col2:
        # 4. Order Status Breakdown (Pie)
        st.markdown("#### Order Status Breakdown")
        status_q = "SELECT order_status, COUNT(*) FROM orders GROUP BY order_status"
        status_data = database.execute_query(status_q)
        if status_data:
            df_status = pd.DataFrame(status_data, columns=["Status", "Count"])
            fig_pie = px.pie(df_status, names="Status", values="Count", hole=0.4, template="plotly_dark", 
                             color="Status", color_discrete_map={'pending':'#f59e0b', 'dispatched':'#10b981', 'cancelled':'#ef4444'})
            st.plotly_chart(fig_pie, use_container_width=True)

        # 5. Category Distribution (Treemap)
        st.markdown("#### Stock Distribution by Category")
        cat_q = 'SELECT "Category", COUNT(*) as count FROM zepto_v2 GROUP BY "Category"'
        cat_data = database.execute_query(cat_q)
        if cat_data:
            df_cat = pd.DataFrame(cat_data, columns=["Category", "Count"])
            fig_tree = px.treemap(df_cat, path=["Category"], values="Count", template="plotly_dark", color="Count", color_continuous_scale="purples")
            st.plotly_chart(fig_tree, use_container_width=True)

    # 6. Low Stock Alert Table
    st.markdown("### 🚨 Low Stock Alerts")
    low_stock_q = """
        SELECT item_id, name, "Category", quantity 
        FROM zepto_v2 WHERE quantity < 10 ORDER BY quantity ASC
    """
    low_stock_data = database.execute_query(low_stock_q)
    if low_stock_data:
        df_ls = pd.DataFrame(low_stock_data, columns=["Item ID", "Name", "Category", "Quantity"])
        # Apply color styling
        def color_danger(val):
            color = 'red' if val < 5 else 'orange'
            return f'color: {color}; font-weight: bold'
        
        st.dataframe(df_ls.style.map(color_danger, subset=['Quantity']), use_container_width=True, hide_index=True)
    else:
        st.success("All items are sufficiently stocked! (Qty >= 10)")

