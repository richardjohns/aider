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

    # List all tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print('\nTables in the database:')
    for table in tables:
        print(f'- {table[0]}')

    # Find a table with rows and list the data in a row
    for table in tables:
        cursor.execute(f'SELECT * FROM {table[0]} LIMIT 1;')
        data = cursor.fetchone()
        if data is not None:
            print(f'\nFirst row data from table "{table[0]}":')
            print(data)
            break

    # List all tables in the database and their row counts
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print('\nTables in the database:')
    for table in tables:
        table_name = table[0]
        try:
            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()
            row_count = len(rows)
            print(f'- {table_name} (Row count: {row_count})')
            for row in rows:
                row_dict = {desc[0]: value for desc, value in zip(cursor.description, row)}
                print(f"data in row is {json.dumps(row_dict, indent=4)}")
        except Exception as e:
            print(f"Error reading table {table_name}: {e}")

    # Close the connection to the database
    conn.close()

if __name__ == '__main__':
    main()