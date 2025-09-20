from utils.DataBase import database
from utils.UserObject import Customer, Admin
from dotenv import load_dotenv
import sys

load_dotenv()  # Load environment variables from .env file
database.get_db_config()
database.conn_postgres()
# database.execute_query("SELECT * FROM zepto_v2")
print("Welcome to Inventory Management System")
while True:
    user_type = input("Are you a customer or admin? (c/a) or q to quit: ").strip().lower()
    if user_type == 'c':
        c1 = Customer()
        action = input("Do you want to login or signup? (l/s): ").strip().lower()
        if action == 'l':
            c1.login()
        elif action == 's':
            c1.signup()
        else:
            print("Invalid action. Please enter 'l' to login or 's' to signup.")
            continue
        if c1.fetch_login_status():
            while True:
                print("\nCustomer Menu:")
                print("1. View Profile")
                print("2. Change User Details")
                print("3. View Grocery")
                print("4. View Order History")
                print("5. Cancel Order")
                print("6. View Cart")
                print("7. Purchase Order")
                print("8. Logout")
                
                # Get user choice
                choice = input("Enter your choice (1-8): ").strip()
                if choice == '1':
                    c1.view_profile()
                elif choice == '2':
                    c1.change_user_details()
                elif choice == '3':
                    c1.view_grocery()
                elif choice == '4':
                    c1.view_order_history()
                elif choice == '5':
                    c1.cancel_order()
                elif choice == '6':
                    c1.view_cart()
                elif choice == '7':
                    c1.purchase_order()
                elif choice == '8':
                    c1.logout()
                    break
                else:
                    print("Invalid choice. Please enter a number between 1 and 9.")
                    
    if user_type == 'a':
        admin = Admin()
        admin.login()
        if admin.fetch_login_status():
            while True:
                print("\nAdmin Menu:")
                print("1. Edit Product")
                print("2. View Order Details")
                print("3. Dispatch Order")
                print("4. Get Insights")
                print("5. Logout")
                
                # Get user choice
                choice = input("Enter your choice (1-5): ").strip()
                if choice == '1':
                    admin.edit_product()
                elif choice == '2':
                    admin.view_order_details()
                elif choice == '3':
                    admin.dispatch_order()
                elif choice == '4':
                    admin.get_insights()
                elif choice == '5':
                    admin.logout()
                    break
                else:
                    print("Invalid choice. Please enter a number between 1 and 5.")
    if user_type == 'q':
        print("Exiting the Inventory Management System. Goodbye!")
        sys.exit(0)
    else:
        print("Invalid user type. Please enter 'c' for customer or 'a' for admin.")
        continue