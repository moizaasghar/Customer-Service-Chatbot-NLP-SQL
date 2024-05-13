import sqlite3

def create_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file"""
    conn = sqlite3.connect(db_file)
    return conn

def create_table(conn, create_table_sql):
    """Create a table from the create_table_sql statement"""
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Exception as e:
        print(e)

def insert_user(conn, user):
    sql = '''INSERT INTO users(name, email, address, area_id)
             VALUES(?,?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, user)
    conn.commit()
    return cur.lastrowid

def insert_package(conn, package):
    sql = '''INSERT INTO packages(package_name, speed_limit, monthly_cost)
             VALUES(?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, package)
    conn.commit()
    return cur.lastrowid

def insert_area(conn, area):
    sql = '''INSERT INTO areas_of_operation(area_name, description)
             VALUES(?,?)'''
    cur = conn.cursor()
    cur.execute(sql, area)
    conn.commit()
    return cur.lastrowid

def insert_service_ticket(conn, ticket):
    sql = '''INSERT INTO service_tickets(user_id, issue_description, status)
             VALUES(?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, ticket)
    conn.commit()
    return cur.lastrowid

def insert_payment_record(conn, payment):
    sql = '''INSERT INTO payment_records(user_id, amount, payment_date)
             VALUES(?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, payment)
    conn.commit()
    return cur.lastrowid

def create_database():
    database = "isp_database.db"
    conn = create_connection(database)
    if conn is not None:
        sql_statements = [
            """CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                address TEXT NOT NULL,
                area_id INTEGER,
                FOREIGN KEY (area_id) REFERENCES areas_of_operation (area_id)
            );""",
            """CREATE TABLE IF NOT EXISTS packages (
                package_id INTEGER PRIMARY KEY AUTOINCREMENT,
                package_name TEXT NOT NULL,
                speed_limit TEXT NOT NULL,
                monthly_cost REAL NOT NULL
            );""",
            """CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            address TEXT NOT NULL,
            area_id INTEGER,
            FOREIGN KEY (area_id) REFERENCES areas_of_operation (area_id)
            );""",
            """CREATE TABLE IF NOT EXISTS packages (
                package_id INTEGER PRIMARY KEY AUTOINCREMENT,
                package_name TEXT NOT NULL,
                speed_limit TEXT NOT NULL,
                monthly_cost REAL NOT NULL
            );""",
            """CREATE TABLE IF NOT EXISTS areas_of_operation (
                area_id INTEGER PRIMARY KEY AUTOINCREMENT,
                area_name TEXT NOT NULL,
                description TEXT
            );""",
            """CREATE TABLE IF NOT EXISTS service_tickets (
                ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                issue_description TEXT NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            );""",
            """CREATE TABLE IF NOT EXISTS payment_records (
                payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount REAL NOT NULL,
                payment_date DATE NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            );"""
        ]
        for statement in sql_statements:
            create_table(conn, statement)
        
        # Insert a new user
        user = ('John Doe', 'johndoe@example.com', '123 Elm Street', 1)
        user_id = insert_user(conn, user)

        # Insert a new package
        package = ('Premium Package', '100Mbps', 99.99)
        package_id = insert_package(conn, package)

        # Insert a new area
        area = ('Downtown', 'Central business district')
        area_id = insert_area(conn, area)

        # Insert a new service ticket
        ticket = (user_id, 'Internet connectivity issue', 'Open')
        ticket_id = insert_service_ticket(conn, ticket)

        # Insert a new payment record
        payment = (user_id, 99.99, '2021-09-01')
        payment_id = insert_payment_record(conn, payment)
        
        conn.close()
    else:
        print("Error! cannot create the database connection.")



def execute_query(conn, query):
    """Execute a SQL query and return the results."""
    cur = conn.cursor()
    try:
        cur.execute(query)
        conn.commit()  # Commit changes if it's an INSERT, UPDATE, or DELETE
        return cur.fetchall()  # Fetch results for SELECT queries
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
