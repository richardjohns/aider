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

    # Show the first row from each table
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 1;")
        row = cursor.fetchone()
        if row is not None:
            row_dict = {desc[0]: value for desc, value in zip(cursor.description, row)}
            print(f"\nFirst row from {table_name}:")
            print(json.dumps(row_dict, indent=4))
        else:
            print(f"No rows in {table_name}.")

    # Close the connection to the database
    conn.close()

if __name__ == '__main__':
    main()