import psycopg2
import os


class database:
    # Fetch database configuration from environment variables
    @classmethod
    def get_db_config(cls):
        cls.user = os.getenv('user')
        cls.__password = os.getenv('password')
        cls.host = os.getenv('host')
        cls.dbname = os.getenv('dbname')
        cls.port = os.getenv('port')
        # Return config as a dictionary
        return {
            'user': cls.user,
            'password': cls.__password,
            'host': cls.host,
            'dbname': cls.dbname,
            'port': cls.port
        }
    
    # Establish a connection to the PostgreSQL database
    @classmethod
    def conn_postgres(cls):
        try:
            config = cls.get_db_config()
            conn = psycopg2.connect(**config)
            return conn
        except Exception as e:
            print(f"Error connecting to PostgreSQL database: {e}")
            return None

    # Execute a SQL query (SELECT or non-SELECT)
    @classmethod
    def execute_query(cls, query, params=None):
        conn = cls.conn_postgres()
        if conn is None:
            print("Connection failed.\n")
            return None
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            # If the query is a SELECT, fetch and return results
            if query.strip().lower().startswith("select"):
                result = cursor.fetchall()
            else:
                # For non-SELECT queries, commit changes
                result = None
                conn.commit()
            cursor.close()
            return result
        except Exception as e:
            print(f"Error executing query: {e}\n")
            return None
        finally:
            # Ensure the connection is closed
            if conn:
                conn.close()

