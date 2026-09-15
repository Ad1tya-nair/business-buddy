from app.database import get_connection


connection = get_connection()

cursor = connection.cursor()

tables = cursor.execute(
    """
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name
    """
).fetchall()

print("\nTABLES")

for table in tables:
    print("-", table["name"])


meetings = cursor.execute(
    """
    SELECT *
    FROM meetings
    """
).fetchall()

print("\nMEETINGS")

for meeting in meetings:
    print(dict(meeting))


connection.close()