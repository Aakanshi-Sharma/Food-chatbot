import mysql.connector

global conn
conn = mysql.connector.connect(
    host='localhost',
    username="root",
    password="root",
    database="pandeyji_eatery"
)


def get_order_status(order_id: int):
    cur = conn.cursor()
    query = "SELECT status FROM order_tracking WHERE order_id = %s"
    cur.execute(query, (order_id,))
    result = cur.fetchone()

    cur.close()
    conn.close()

    if result is not None:
        return result[0]
    else:
        return None
