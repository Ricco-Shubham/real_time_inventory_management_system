import bcrypt
import getpass
from utils.DataBase import database
from utils.insightsgenerator import DataInsightsReport


# Function to hash passwords using bcrypt
# This function generates a salt and hashes the password using bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

class Customer:
    def __init__(self):
        self.username = ""
        self.address = ""
        self.pincode = ""
        self.phone_no = ""
        self.__password = ""
        self.__is_logged_in = False

    def verify_password(self, password: str) -> bool:
        # Fetch the stored password hash from the database for this user
        query = f"SELECT password_hash FROM customers WHERE phone_no = '{self.phone_no}'"
        result = database.execute_query(query)
        if result:
            stored_hash = result[0][0]
            return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
        return False
   
    def authenticate(self):
        if self.verify_password(self.__password):
            self.__is_logged_in = True
            print("Login successful.\n")
        else:
            print("Invalid phone number or password.\n")

    def __enter_info(self):
        self.username = input("Enter your name: ")
        self.address = input("Enter your address: ")
        self.pincode = input("Enter your pincode: ")
        self.phone_no = input("Enter your phone number: ")
        query = f'SELECT "name" FROM customers WHERE phone_no = \'{self.phone_no}\''
        result = database.execute_query(query)
        if len(result) != 0 :
            print("Phone number already registered. Please log in.\n")
            return None
        else:
            self.__password = getpass.getpass("Enter your password: ")
            return 1

    def __print_data(self, result, columns=None, title="Table Data"):
        """
        Generalized function to print any table data in a formatted way.
        :param result: List of tuples from database query
        :param columns: List of column names (optional)
        :param title: Title to display (optional)
        """
        if result:
            print(f"\n{title}:\n")
            # If columns are provided, print header
            if columns:
                print(" | ".join(["{:<20}".format(col) for col in columns]))
                print("-" * (22 * len(columns)))
            for row in result:
                print(" | ".join(["{:<20}".format(str(item)) for item in row]))
        else:
            print("No data found.")

    def __update_info(self):
            query = f"""
            INSERT INTO customers (name, address, pincode, phone_no, password_hash)
            VALUES ('{self.username}', '{self.address}', '{self.pincode}', '{self.phone_no}', '{hash_password(self.__password)}')
            """
            try:
                database.execute_query(query)
            except Exception as e:
                print(f"Error occurred: {e}\n")
    
    def signup(self):
        catch = self.__enter_info() 
        if catch is None:
            print("Signup unsccessful.please sign in again!\n")
        else:
            self.__update_info()
            print("Signup successful!!\n")
            print("Please log in to continue.\n")
            self.login()

    def login(self):
        self.phone_no = input("Enter your phone number: ")
        self.__password = getpass.getpass("Enter your password: ")
        self.verify_password(self.__password)
        self.authenticate()
        try:
            # Fetch customer_id after successful login
            self.customer_id = database.execute_query(f"SELECT customer_id FROM customers WHERE phone_no = '{self.phone_no}'")[0][0]
        except Exception as e:
            print(f"Error fetching customer ID: {e}\n")
            return

    def fetch_login_status(self):
        return self.__is_logged_in

    def change_user_details(self):
        if self.__is_logged_in:
            print("Change User Details\n")
            change = input("what you want to change? (name/address/pincode/phone/password): ").strip().lower()
            if change == "name":
                self.username = input("Enter your new name: ")
                query = f"UPDATE customers SET name = '{self.username}' WHERE phone_no = '{self.phone_no}'"
            elif change == "address":
                self.address = input("Enter your new address: ")
                query = f"UPDATE customers SET address = '{self.address}' WHERE phone_no = '{self.phone_no}'"
            elif change == "pincode":
                self.pincode = input("Enter your new pincode: ")
                query = f"UPDATE customers SET pincode = '{self.pincode}' WHERE phone_no = '{self.phone_no}'"
            elif change == "phone":
                self.phone_no = input("Enter your new phone number: ")
                query = f"UPDATE customers SET phone_no = '{self.phone_no}' WHERE phone_no = '{self.phone_no}'"
            elif change == "password":
                password1 = input("Enter your new password: ")
                password2 = input("Re-enter your new password: ")
                if password1 != password2:
                    print("Passwords do not match. Please try again.\n")
                    return
                self.__password = password1
                query = f"UPDATE customers SET password_hash = '{hash_password(self.__password)}' WHERE phone_no = '{self.phone_no}'"
            # If no valid change is specified
            else:
                print("Invalid option. Please choose from name, address, pincode, phone, or password.\n")
                return
            # Execute the update query
            try:
                database.execute_query(query)
                print("User details updated successfully.\n")
            except Exception as e:
                print(f"Error occurred while updating user details: {e}\n")

    def view_profile(self):
        if self.__is_logged_in:
            query = f"SELECT * FROM customers WHERE phone_no = '{self.phone_no}'"
            result = database.execute_query(query)
            if result:
                customer_data = result[0]
                print(f"Customer ID: {customer_data[0]}")
                print(f"Name: {customer_data[1]}")
                print(f"Address: {customer_data[2]}")
                print(f"Pincode: {customer_data[3]}")
                print(f"Phone No: {customer_data[4]}")
            else:
                print("No profile found. Please log in or sign up.")

    def view_grocery(self):
        # Fetch distinct categories
        if self.__is_logged_in:
            category = database.execute_query('SELECT DISTINCT("Category") FROM zepto_v2')
        
            while True:
                # Print available categories
                count = 1
                print("\nAvailable Categories:\n")
                for i in category:
                    print(f"{count} :  {i[0]}")
                    count += 1
                # Prompt user to choose a category or return to main menu
                choose = input("Choose category, press q to return to main menu: ")
                # If user chooses to return to main menu
                if choose == 'q':
                    break
                # If user chooses to view products in a category  
                choose = int(choose)
                selected_category = category[choose - 1][0]
                # Fetch products in the selected category
                result = database.execute_query(f'SELECT "item_id", "quantity","discountedSellingPrice" , "name" FROM zepto_v2 WHERE "Category" = \'{selected_category}\'')
                self.__print_data(result, columns=["Product ID", "Quantity", "Discounted Selling Price", "Product Name"], title=f"Products in Category: {selected_category}")
                self.__add_to_cart()

    def view_order_history(self):
        if self.__is_logged_in:
            result = database.execute_query(f'SELECT "order_id", "order_timestamp", "order_status", "total_amount_paid" FROM orders WHERE customer_id = {self.customer_id}')
            self.__print_data(result,columns=["Order ID", "Order Timestamp", "Order Status","Total Amount Paid"], title="Order History")
            print("press q to return to main menu or press v to view order details, press g to generate bill")
            choice = input("Enter your choice: ")
            if choice == 'q':
                return
            elif choice == 'v':
                print("View Order details:\n")
                order_id = int(input("Enter Order ID to view order Items"))
                result = database.execute_query(f'SELECT "order_id","item_id","quantity","amount_paid","name" FROM order_items WHERE "order_id" = \'{order_id}\'')
                self.__print_data(result,columns=["order ID","Item ID","quantity","amount paid","name"],title="Order Details")
            elif choice == 'g':
                order_id = int(input("Enter Order ID to generate bill: "))
                print("Generating bill...")
                self.generate_bill(order_id,self.customer_id)

    def cancel_order(self):
        if self.__is_logged_in:
            self.view_order_history()
            order_id = int(input("Enter the Order ID to cancel: "))
            status = database.execute_query(f'SELECT "order_status" FROM orders WHERE "order_id" = {order_id} AND "customer_id" = {self.customer_id}')
            if status[0][0] == 'pending':
                database.execute_query(f"UPDATE orders SET order_status = 'cancelled' WHERE order_id = {order_id} AND customer_id = {self.customer_id}")
                print("Order cancelled successfully.")
            elif status[0][0] == 'dispatched':
                print("Order already dispatched. Cannot cancel.")
            else:
                print("Order already cancelled. Cannot cancel.")

    def view_cart(self):
        if self.__is_logged_in:
            result = database.execute_query(f'SELECT "item_id","quantity","price","name" FROM cart_details WHERE customer_id = {self.customer_id}')
            self.__print_data(result,columns=["Item ID", "quantity","price", "name"], title="Cart Details")
            total_price = sum(item[1] * item[2] for item in result)
            print(f"\nTotal Price: {total_price}\n")
            if result: 
                print("Remove items from cart? or press 'n' to continue shopping")
                remove_choice = input("Enter your choice: ").strip().lower()
                if remove_choice == 'yes':
                    item_id = input("Enter the product item id to remove from cart: ")
                    # Remove item from cart
                    query = f'DELETE FROM cart_details WHERE "customer_id" = {self.customer_id} AND "item_id" = \'{int(item_id)}\''
                    database.execute_query(query)
                    print("Item removed from cart successfully.")
                elif remove_choice == 'n':
                    print("Continuing shopping...\n")

            return result

    def __add_to_cart(self):
        if self.__is_logged_in:
            while True:
                item_id = input("Enter the product item id to add to cart or press 'q' to return to main menu: ")
                # If user chooses to return to main menu
                if item_id == 'q':
                    break
                result = database.execute_query(f'SELECT "name","quantity","discountedSellingPrice" FROM zepto_v2 WHERE "item_id" = \'{int(item_id)}\'')
                # Check if product exists
                if not result:
                    print("Product not found.")
                    return
                
                name = result[0][0]
                available_quantity = result[0][1]
                price = result[0][2]
                # Check if product is in stock
                if available_quantity <= 0:
                    print("Product is out of stock.")
                    return
                print(f"Available quantity: {available_quantity}")
                # Get desired quantity from user
                quantity = int(input("Enter quantity: "))
                # Check if requested quantity is available
                if quantity > available_quantity:
                    print("Requested quantity exceeds available stock.")
                    return
                # Add to cart (assuming a cart table exists)
                query = f'INSERT INTO cart_details ("customer_id", "item_id","name", "quantity", "price") VALUES ({self.customer_id}, \'{int(item_id)}\',\'{name}\', \'{quantity}\',\'{price}\')'
                database.execute_query(query)
                # Update inventory
                query = f'UPDATE zepto_v2 SET "quantity" = "quantity" - \'{quantity}\' WHERE "item_id" = \'{int(item_id)}\''
                database.execute_query(query)
                print("Product added to cart successfully.")

    def purchase_order(self):
        if self.__is_logged_in:
            result = self.view_cart()
            if result:
                cart_items = database.execute_query(f'SELECT "item_id", "quantity" FROM cart_details WHERE "customer_id" = {self.customer_id}')
                total_amount = sum(int(item[1]) * database.execute_query(f'SELECT "discountedSellingPrice" FROM zepto_v2 WHERE "item_id" = \'{item[0]}\'')[0][0] for item in cart_items)
               
                database.execute_query(f'INSERT INTO orders ("customer_id","order_status","total_amount_paid") VALUES ({self.customer_id},\'pending\',{total_amount})')
                order_id = database.execute_query(f'SELECT "order_id" FROM orders WHERE "customer_id" = {self.customer_id} ORDER BY "order_timestamp" DESC LIMIT 1')[0][0]
                for item in cart_items:
                    item_id = item[0]
                    quantity = item[1]
                
                    info = database.execute_query(f'SELECT "name","discountedSellingPrice" FROM zepto_v2 WHERE "item_id" = \'{item_id}\'')
                    # info[0][0] --> name
                    name = info[0][0]
                    # info[0][1] --> discounted price
                    price = info[0][1]
                    query = f'INSERT INTO order_items (order_id, item_id, name, quantity, amount_paid) VALUES ({order_id}, \'{item_id}\',\'{name}\', \'{quantity}\', \'{price* quantity}\')'
                    database.execute_query(query)
                # Clear the cart after purchase
                database.execute_query(f'DELETE FROM cart_details WHERE "customer_id" = {self.customer_id}')
                # Print success message with order ID
                print("Order placed successfully. Your order ID is:", order_id)
                
    def logout(self):
        if self.__is_logged_in:
            self.__is_logged_in = False
            print("You have been logged out successfully.")
        else:
            print("You are already logged out.")

    def generate_bill(self, order_id,customer_id):
        # Generate bill for the last order using DataInsight reporting tool
        if self.__is_logged_in:
            DataInsightsReport().generate_bill(order_id,customer_id)



class Admin:
    def __init__(self):
        self.__is_logged_in = False

    def login(self):
        self.username = input("Enter admin username: ")
        self.__password = getpass.getpass("Enter admin password: ")
        if self.username == "admin" and self.__password == "admin@123":
            self.__is_logged_in = True
            print("Admin login successful.")
        else:
            print("Invalid admin credentials.")
            return

    def logout(self):
        if self.__is_logged_in:
            self.__is_logged_in = False
            print("Admin logged out successfully.")
        else:
            print("Admin is not logged in.")
            return

    def fetch_login_status(self):
        return self.__is_logged_in

    def edit_product(self):
        if self.__is_logged_in:
            # Display all products
            result = database.execute_query('SELECT "item_id", "quantity","discountedSellingPrice", "name" FROM zepto_v2')
            self.__print_data(result, columns=["Product ID", "Quantity", "Discounted Selling Price", "Product Name"], title="All Products")
           
            print("What do you want to edit? (name/price/quantity)")
            item_id = input("Enter the product item id to edit: ")
            field_to_edit = input("Enter the field to edit (name/price/quantity): ")
           # If name is to be edited
            if field_to_edit == "name":
                new_name = input("Enter the new product name: ")
                query = f'UPDATE zepto_v2 SET name = \'{new_name}\' WHERE item_id = \'{item_id}\''     
           # If price is to be edited
            elif field_to_edit == "price":
                new_price = float(input("Enter the new product price: "))
                # change discount percentage based on new price and mrp
                mrp = database.execute_query(f'SELECT "mrp" FROM zepto_v2 WHERE "item_id" = \'{item_id}\'')[0][0]
                if new_price < mrp:
                    discount_percentage = ((mrp - new_price) / mrp) * 100
                else:
                    discount_percentage = 0
                query = f'UPDATE zepto_v2 SET "discountedSellingPrice" = {int(new_price)}, "discountPercent" = \'{discount_percentage:1f}\' WHERE item_id = \'{item_id}\''
              # If quantity is to be edited
            elif field_to_edit == "quantity":
                new_quantity = int(input("Enter the new product quantity: "))
                query = f'UPDATE zepto_v2 SET "quantity" = \'{new_quantity}\' WHERE item_id = \'{item_id}\''
            # If no valid field is specified
            else:
                print("Invalid option. Please choose from name or price.")
                return
            # Execute the update query
            database.execute_query(query)
            print("Product updated successfully.")
        else:
            print("Admin is not logged in. Please log in to generate insights.")
        
    def view_order_details(self):
        if self.__is_logged_in:
            result = database.execute_query("SELECT * FROM orders")
            if result:
                print("\nOrder Details:")
                print("{:<10} | {:<12} | {:<20} | {:<15}".format("Order ID", "Customer ID", "Order Timestamp", "Order Status"))
                print("-" * 65)
                for row in result:
                    print("{:<10} | {:<12} | {:<20} | {:<15}".format(row[0], row[1], str(row[2]), row[3]))
            else:
                print("No orders found.")
        else:
            print("Admin is not logged in. Please log in to generate insights.")
     
    def dispatch_order(self):
        if self.__is_logged_in:
            self.view_order_details()
            order_id = int(input("Enter the Order ID to dispatch: "))
            status = database.execute_query(f'SELECT "order_status" FROM orders WHERE "order_id" = {order_id}')
            if status[0][0] == 'pending':
                database.execute_query(f"UPDATE orders SET order_status = 'dispatched' WHERE order_id = {order_id}")
                print("Order dispatched successfully.")
            elif status[0][0] == 'dispatched':
                print("Order already dispatched.")
            elif status[0][0] == 'cancelled':
                print("Order was cancelled. Cannot dispatch.")
            else:
                print("Order ID not found.")
        else:
            print("Admin is not logged in. Please log in to generate insights.")

    def __print_data(self, result, columns=None, title="Table Data"):
        """
        Generalized function to print any table data in a formatted way.
        :param result: List of tuples from database query
        :param columns: List of column names (optional)
        :param title: Title to display (optional)
        """
        if result:
            print(f"\n{title}:")
            # If columns are provided, print header
            if columns:
                print(" | ".join(["{:<20}".format(col) for col in columns]))
                print("-" * (22 * len(columns)))
            for row in result:
                print(" | ".join(["{:<20}".format(str(item)) for item in row]))
        else:
            print("No data found.")

    def get_insights(self):
        if self.__is_logged_in:
            print("Generating insights report...")
            # Create an instance of DataInsightsReport and generate the report
            DataInsightsReport().generate_pdf_report()
            print("Insights report generated successfully.")
        else:
            print("Admin is not logged in. Please log in to generate insights.")
    