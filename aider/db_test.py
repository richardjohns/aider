import sqlite3

def main():
    # Connect to the SQLite database
    conn = sqlite3.connect('db/chroma.sqlite3')

    # Create a cursor
    cursor = conn.cursor()

    # Check if the database is responding
    try:
        cursor.execute('SELECT 1')
        print('Database Status: RESPONDING')
    except sqlite3.Error as e:
        print(f'Database Status: NOT RESPONDING\nError: {e}')

    # List all tables in the database and their row counts
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print('\nTables in the database:')
    for table in tables:
        table_name = table
        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()
        row_count = len(rows)
        print(f'- {table_name} (Row count: {row_count})')
        if rows:
            first_row = rows[0]
            row_dict = {desc[0]: value for desc, value in zip(cursor.description, first_row)}
            print(f"data in first row is {json.dumps(row_dict, indent=4)}")
        else:
            print("No rows in this table.")

    # Close the connection to the database
    conn.close()

if __name__ == '__main__':
    main()