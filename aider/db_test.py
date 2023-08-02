import sqlite3

def main():
    # Connect to the SQLite database
    conn = sqlite3.connect('db/chroma.sqlite3')

    # Create a cursor
    cursor = conn.cursor()

    # Check if the database is responding
    try:
        cursor.execute('SELECT 1')
        print('The database is responding.')
    except sqlite3.Error as e:
        print(f'The database is not responding. Error: {e}')

    # List all tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print('Tables in the database:', tables)

    # Find a table with rows and list the data in a row
    for table in tables:
        cursor.execute(f'SELECT * FROM {table[0]} LIMIT 1;')
        data = cursor.fetchone()
        if data is not None:
            print(f'Table {table[0]} has data:', data)
            break

    # Close the connection to the database
    conn.close()

if __name__ == '__main__':
    main()