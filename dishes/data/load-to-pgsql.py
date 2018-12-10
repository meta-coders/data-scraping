import psycopg2 as pgsql

connection = pgsql.connect(
    host = "localhost",
    database = "dishes",
    user = "postgres",
    password = "postgres"
)

cursor = connection.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS dishes (
        type text,
        name text,
        price text,
        restaurant text,
        link text,
        addresses text[]
    )
    """
)

csv = open('./restaurants.csv', 'r')
data = [line.replace('\n', '').replace('"', '').split('|') for line in csv]
del data[0]

dishes = []

for row in data:
    addresses = row.pop().split(';')
    addresses = list(map(lambda x: '"' + x + '"', addresses))
    row.append('{' + ','.join(addresses) + '}')
    dishes.append(tuple(row))

cursor.executemany(
    """
    INSERT INTO dishes (
        type, name, price, restaurant, link, addresses
    ) VALUES (
        %s, %s, %s, %s, %s, %s
    )
    """,
    dishes
)

connection.commit()