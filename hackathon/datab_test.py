import sqlite3

try:
    with sqlite3.connect("shelters.db") as conn:
        print("Connected to the database")
        
        # Create a cursor object to execute SQL queries
        cursor = conn.cursor()
        
        # Query to fetch all rows from the 'users' table
        cursor.execute("SELECT * FROM resources")
        
        # Fetch all rows from the executed query
        rows = cursor.fetchall()
        
        # Check if there are rows and print them
        if rows:
            print("Users table:")
            for row in rows:
                print(row)
        else:
            print("No data found in the 'users' table.")
except sqlite3.OperationalError as e:
    print("Failed to open database:", e)
except sqlite3.DatabaseError as e:
    print("Database error occurred:", e)
