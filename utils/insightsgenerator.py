import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from utils.DataBase import database
from datetime import datetime


class DataInsightsReport:

    def fetch_sales_data(self):
        query = """
        SELECT oi.item_id, zv.name, SUM(oi.quantity) AS total_sold, SUM(oi.amount_paid) AS revenue
        FROM order_items oi
        JOIN zepto_v2 zv ON oi.item_id = zv.item_id
        GROUP BY oi.item_id, zv.name
        ORDER BY total_sold DESC
        LIMIT 10
        """
        return pd.DataFrame(database.execute_query(query), columns=["Item ID", "Product Name", "Total Sold", "Revenue"])

    def fetch_inventory_status(self):
        query = """
        SELECT item_id, name, quantity
        FROM zepto_v2
        WHERE quantity < 10
        ORDER BY quantity ASC
        LIMIT 10
        """
        return pd.DataFrame(database.execute_query(query), columns=["Item ID", "Product Name", "Quantity"])

    def fetch_customer_behavior(self):
        query = """
        SELECT c.name, COUNT(o.order_id) AS orders, SUM(oi.quantity) AS items_bought
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN order_items oi ON o.order_id = oi.order_id
        GROUP BY c.name
        ORDER BY orders DESC
        LIMIT 10
        """
        return pd.DataFrame(database.execute_query(query), columns=["Customer Name", "Orders", "Items Bought"])

    def plot_top_products(self, sales_df):
        # Ensure 'Total Sold' is numeric for nlargest
        sales_df["Total Sold"] = pd.to_numeric(sales_df["Total Sold"], errors="coerce").fillna(0)
        top10 = sales_df.nlargest(10, "Total Sold").sort_values("Total Sold", ascending=False)
        plt.figure(figsize=(16, 10))
        color_count = len(top10)
        colors_list = [plt.cm.Greens(0.3 + 0.7 * (1-i / (color_count - 1))) for i in range(color_count)]
        bars = plt.bar(top10["Product Name"], top10["Total Sold"], color=colors_list)
        plt.xticks(rotation=30, ha='right', fontsize=12)
        plt.title("Top 10 Selling Products", fontsize=18, fontweight='bold')
        plt.ylabel("Units Sold", fontsize=15)
        plt.xlabel("Product Name", fontsize=15)
        plt.tight_layout()
        for bar in bars:
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(), int(bar.get_height()), ha='center', va='bottom', fontsize=12)
        plt.savefig("./insights_img/top10_products.png", dpi=200, bbox_inches='tight')
        plt.close()

    def plot_revenue_profit(self, sales_df):
        plt.figure(figsize=(16, 10))  
        color_count = len(sales_df["Product Name"])
        colors_list = [plt.cm.Blues(0.3 + 0.7 * (1-i / (color_count - 1))) for i in range(color_count)]
        sales_df = sales_df.sort_values("Revenue", ascending=False)
        bars = plt.bar(sales_df["Product Name"], sales_df["Revenue"], color=colors_list)
        plt.xticks(rotation=30, ha='right', fontsize=12)
        plt.title("Revenue by Product", fontsize=18, fontweight='bold')
        plt.ylabel("Revenue", fontsize=15)
        plt.xlabel("Product Name", fontsize=15)
        plt.tight_layout()
        for bar in bars:
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f"{bar.get_height():.2f}", ha='center', va='bottom', fontsize=12)
        plt.savefig("./insights_img/revenue_by_product.png", dpi=200, bbox_inches='tight')  # Use bbox_inches to avoid cropping
        plt.close()

    def draw_table(self, c, data, col_names, x, y, col_widths, row_height=18, title=None):
        if title:
            c.setFont("Helvetica-Bold", 12)
            c.setFillColor(colors.darkblue)
            c.drawString(x, y, title)
            y -= row_height
        # Table header
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.HexColor("#F7DC6F"))
        c.rect(x-5, y-4, sum(col_widths)+10, row_height, fill=1, stroke=0)
        c.setFillColor(colors.black)
        for i, col in enumerate(col_names):
            c.drawString(x + sum(col_widths[:i]), y, str(col))
        y -= row_height
        # Table rows
        c.setFont("Helvetica", 10)
        for idx, row in enumerate(data):
            # Alternate row color using index
            c.setFillColor(colors.white if idx % 2 == 0 else colors.HexColor("#EBF5FB"))
            c.rect(x-5, y-4, sum(col_widths)+10, row_height, fill=1, stroke=0)
            c.setFillColor(colors.black)
            for i, item in enumerate(row):
                c.drawString(x + sum(col_widths[:i]), y, str(item))
            y -= row_height
            if y < 60:
                c.showPage()
                y = letter[1] - 60
        return y

    def plot_category_distribution(self):
        # Pie chart for product categories
        query = 'SELECT "Category", COUNT(*) FROM zepto_v2 GROUP BY "Category"'
        result = database.execute_query(query)
        if result:
            categories, counts = zip(*result)
            plt.figure(figsize=(8, 8))
            plt.pie(counts, labels=categories, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
            plt.title("Product Category Distribution", fontsize=16)
            plt.tight_layout()
            plt.savefig("./insights_img/category_distribution.png", dpi=150)
            plt.close()
    
    def plot_monthly_sales(self):
        # Bar chart for monthly sales
        query = """
        SELECT DATE_TRUNC('month', o.order_timestamp) AS month, SUM(oi.quantity) AS total_sold
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        GROUP BY month
        ORDER BY month
        """
        result = database.execute_query(query)
        if result:
            months, totals = zip(*result)
            months_fmt = [str(m)[:7] for m in months]
            plt.figure(figsize=(12, 6))
            plt.bar(months_fmt, totals, color=plt.cm.Blues(np.linspace(0.3, 0.8, len(months_fmt))))
            plt.title("Monthly Sales Trend", fontsize=16)
            plt.xlabel("Month", fontsize=13)
            plt.ylabel("Units Sold", fontsize=13)
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig("./insights_img/monthly_sales.png", dpi=150)
            plt.close()
    
    def plot_top_customers(self):
        # Horizontal bar chart for top customers by orders
        query = """
        SELECT c.name, COUNT(o.order_id) AS orders
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.name
        ORDER BY orders DESC
        LIMIT 5
        """
        result = database.execute_query(query)
        if result:
            names, orders = zip(*result)
            plt.figure(figsize=(10, 5))
            barh = plt.barh(names, orders, color=plt.cm.Greens(np.linspace(0.5, 0.9, len(names))))
            plt.title("Top 5 Customers by Orders", fontsize=16)
            plt.xlabel("Number of Orders", fontsize=13)
            plt.tight_layout()
            for bar in barh:
                plt.text(bar.get_width(), bar.get_y() + bar.get_height()/2, f"{bar.get_width()}", va='center', fontsize=12)
            plt.savefig("./insights_img/top_customers.png", dpi=150)
            plt.close()

    def generate_pdf_report(self):
        sales_df = self.fetch_sales_data()
        inventory_df = self.fetch_inventory_status()
        customer_df = self.fetch_customer_behavior()

        self.plot_top_products(sales_df)
        self.plot_revenue_profit(sales_df)
        self.plot_category_distribution()
        self.plot_monthly_sales()
        self.plot_top_customers()
        
        # Get the base directory
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Build the target directory path
        output_dir = os.path.join(base_dir, "..", "Inventory_Insights")

        # Create the directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Full file path
        file_path = os.path.join(output_dir, f"Inventory_Insights_Report.pdf")

        c = canvas.Canvas(file_path, pagesize=letter)
        width, height = letter

        # Header
        c.setFillColor(colors.HexColor("#2E86C1"))
        c.rect(0, height-60, width, 60, fill=1)
        c.setFont("Helvetica-Bold", 22)
        c.setFillColor(colors.white)
        c.drawString(40, height-40, "Inventory Insights Report")

        # Section: Sales & Revenue
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, height-90, "Total Sales & Revenue Overview")
        c.drawImage("./insights_img/revenue_by_product.png", 20, height-400, width=570, height=250)

        # Section: Top 10 Selling Products
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, height-420, "Top 10 Selling Products")
        c.drawImage("./insights_img/top10_products.png", 20, height-700, width=570, height=250)

        # --- PAGE BREAK for next visuals ---
        c.showPage()
        width, height = letter

        # Section: Product Category Distribution (Pie Chart)
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.darkblue)
        c.drawString(40, height-60, "Product Category Distribution")
        c.setFillColor(colors.black)
        c.drawImage("./insights_img/category_distribution.png", 40, height-320, width=250, height=250)

        # Section: Monthly Sales Trend
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.darkmagenta)
        c.drawString(320, height-60, "Monthly Sales Trend")
        c.setFillColor(colors.black)
        c.drawImage("./insights_img/monthly_sales.png", 320, height-320, width=250, height=180)

        # Section: Top Customers
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.darkgreen)
        c.drawString(40, height-340, "Top 5 Customers by Orders")
        c.setFillColor(colors.black)
        c.drawImage("./insights_img/top_customers.png", 40, height-470, width=250, height=120)

        # --- PAGE BREAK for tables ---
        c.showPage()
        width, height = letter

        # Section: Items to Reorder (Table format)
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.red)
        c.drawString(40, height-60, "Items to Reorder (Low Stock):")
        c.setFillColor(colors.black)
        y = height-80
        if not inventory_df.empty:
            y = self.draw_table(
                c,
                inventory_df.values,
                ["Item ID", "Product Name", "Quantity"],
                40, y,
                [60, 250, 80],
                row_height=18,
                title=None
            )
        else:
            c.setFont("Helvetica", 12)
            c.drawString(60, y, "All items sufficiently stocked.")
            y -= 20

        # Section: Customer Buying Behavior
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.darkgreen)
        c.drawString(40, y-20, "Customer Buying Behavior:")
        c.setFillColor(colors.black)
        y -= 40
        if not customer_df.empty:
            self.draw_table(
                c,
                customer_df.values,
                ["Customer Name", "Orders", "Items Bought"],
                40, y,
                [200, 80, 80],
                row_height=16,
                title=None
            )
        else:
            c.setFont("Helvetica", 12)
            c.drawString(60, y, "No customer data available.")

        # Footer
        c.setFont("Helvetica-Oblique", 10)
        c.setFillColor(colors.grey)
        c.drawString(40, 30, "Generated by Real-Time Inventory Tracking System | © 2025")

        c.save()
        print("PDF report generated: Inventory_Insights_Report.pdf")

    def generate_bill(self, order_id, customer_id):
        # Fetch order details (including order_timestamp)
        order_details = database.execute_query(
            f'SELECT order_status, order_timestamp FROM orders WHERE order_id = {order_id} AND customer_id = {customer_id}'
        )
        if not order_details:
            print("Order not found.")
            return

        order_status = order_details[0][0].lower()
        order_timestamp = order_details[0][1]

        # Format timestamp (example: 10-Sep-2025 07:01 AM)
        try:
            order_datetime = datetime.strptime(str(order_timestamp), "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            order_datetime = datetime.strptime(str(order_timestamp), "%Y-%m-%d %H:%M:%S")
        formatted_date = order_datetime.strftime("%d-%b-%Y %I:%M %p")

        # Fetch order items
        order_items = database.execute_query(
            f'SELECT item_id, name, quantity, amount_paid FROM order_items WHERE order_id = {order_id}'
        )
        if not order_items:
            print("No items found for this order.")
            return

        # Fetch customer info
        customer_info = database.execute_query(
            f"SELECT name, address, pincode, phone_no FROM customers WHERE customer_id = {customer_id}"
        )
        customer_name, address, pincode, phone_no = customer_info[0]

        # Get the base directory (utils/ in your case)
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Build the target directory path
        output_dir = os.path.join(base_dir, "..", "order_bills")

        # Create the directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Full file path
        file_path = os.path.join(output_dir, f"Bill_{order_id}.pdf")
        c = canvas.Canvas(file_path, pagesize=letter)
        width, height = letter

        # Bill Header
        c.setFont("Helvetica-Bold", 18)
        c.setFillColor(colors.HexColor("#2E86C1"))
        c.drawString(30, height - 50, "Thank you for shopping with us!")
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(30, height - 80, f"Bill for Order ID: {order_id}")

        # Order Status with color
        status_y = height - 105
        if order_status == "cancelled":
            c.setFillColor(colors.red)
            status_text = "Order Status: Cancelled"
        elif order_status == "dispatched":
            c.setFillColor(colors.green)
            status_text = "Order Status: Dispatched"
        else:
            c.setFillColor(colors.HexColor("#F7DC6F"))  # dark yellow
            status_text = "Order Status: In Process"
        c.setFont("Helvetica-Bold", 13)
        c.drawString(30, status_y, status_text)
        c.setFillColor(colors.black)

        # Order Date/Time
        c.setFont("Helvetica", 12)
        c.drawString(30, status_y - 20, f"Order Date & Time: {formatted_date}")

        # Customer details
        c.drawString(30, height - 165, f"Customer Name: {customer_name}")
        c.drawString(30, height - 185, f"Delivery Address: {address}, {pincode}")
        c.drawString(30, height - 205, f"Phone: {phone_no}")

        # Table Heading
        y_position = height - 240
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.HexColor("#F7DC6F"))
        c.rect(25, y_position - 5, 500, 22, fill=1, stroke=0)
        c.setFillColor(colors.black)
        c.drawString(35, y_position, "Item ID")
        c.drawString(120, y_position, "Item Name")
        c.drawString(320, y_position, "Quantity")
        c.drawString(400, y_position, "Amount Paid")

        # Table Rows
        y_position -= 25
        total_amount = 0
        for idx, item in enumerate(order_items):
            item_id, name, quantity, amount_paid = item

            # Column positions
            col_item_id_x = 35
            col_name_x = 120
            col_qty_x = 320
            col_amt_x = 400
            max_name_width = col_qty_x - col_name_x - 10  # prevent overlap

            # Split name into wrapped lines
            words = str(name).split(" ")
            line = ""
            wrapped_lines = []
            for word in words:
                test_line = line + (" " if line else "") + word
                if stringWidth(test_line, "Helvetica", 12) <= max_name_width:
                    line = test_line
                else:
                    wrapped_lines.append(line)
                    line = word
            if line:
                wrapped_lines.append(line)

            # Row height depends on number of wrapped lines
            row_height = 15 * len(wrapped_lines)

            # Background color for entire row
            c.setFillColor(colors.white if idx % 2 == 0 else colors.HexColor("#EBF5FB"))
            c.rect(25, y_position - (row_height - 10), 500, row_height, fill=1, stroke=0)
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 12)
            # Draw item_id
            c.drawString(col_item_id_x, y_position, str(item_id))

            # Draw wrapped name lines
            line_y = y_position
            for line_text in wrapped_lines:
                c.drawString(col_name_x, line_y, line_text)
                line_y -= 15

            # Draw quantity & amount (only on first line to align properly)
            c.drawString(col_qty_x, y_position, str(quantity))
            c.drawString(col_amt_x, y_position, f"Rs. {amount_paid:.2f}")

            # Update y_position for next row
            y_position -= row_height + 5
            total_amount += float(amount_paid)

            # Page break check
            if y_position < 80:
                c.showPage()
                y_position = height - 80

        # Total Amount
        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(colors.HexColor("#F7DC6F"))
        c.rect(320, y_position - 8, 205, 22, fill=1, stroke=0)
        c.setFillColor(colors.black)
        c.drawString(325, y_position, "Total Amount:")
        c.drawString(420, y_position, f"Rs. {total_amount:.2f}")

        # Footer
        c.setFont("Helvetica-Oblique", 11)
        c.setFillColor(colors.grey)
        c.drawString(30, 40, "We hope to see you again! | Real-Time Inventory Tracking System | © 2025")

        c.save()
        print(f"PDF bill generated: Bill_{order_id}.pdf")


