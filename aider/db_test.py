import sqlite3
import json

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

    # Find a table with rows and list the data in the first row
    for table in tables:
        cursor.execute(f'SELECT * FROM {table[0]} LIMIT 1;')
        data = cursor.fetchone()
        if data is not None:
            print(f'\nFirst row data from table "{table[0]}":')
            print(data)
            break

    # List all tables in the database and the first row for each table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print('\nTables in the database:')
    for table in tables:
        table_name = table[0]
        try:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 1;")
            row = cursor.fetchone()
            if row is not None:
                row_dict = {desc[0]: value for desc, value in zip(cursor.description, row)}
                print(f'- {table_name} (First row data: {json.dumps(row_dict, indent=4)})')
            else:
                print(f'- {table_name} (No data)')
        except Exception as e:
            print(f"Error reading table {table_name}: {e}")

    # Check the collections table
    cursor.execute("SELECT * FROM collections;")
    collections = cursor.fetchall()
    print(f'Number of collections: {len(collections)}')
    for collection in collections:
        print(collection)

    # Check the segments table
    cursor.execute("SELECT * FROM segments;")
    segments = cursor.fetchall()
    print(f'Number of segments: {len(segments)}')
    for segment in segments:
        print(segment)

    # Check the embeddings_queue table
    cursor.execute("SELECT COUNT(*) FROM embeddings_queue;")
    num_embeddings = cursor.fetchone()[0]
    print(f'Number of embeddings: {num_embeddings}')
    if num_embeddings == 0:
        print('Warning: The embeddings_queue table is empty.')

    # Check the embedding_fulltext_data table
    try:
        cursor.execute("SELECT * FROM embedding_fulltext_data LIMIT 5;")
        data = cursor.fetchall()
        for row in data:
            print(row)
    except Exception as e:
        print(f'Error reading the embedding_fulltext_data table: {e}')

    # Close the connection to the database
    conn.close()

if __name__ == '__main__':
    main()