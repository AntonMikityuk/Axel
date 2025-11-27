import sqlite3
api_key = "a1b2c3d4e5f6g7h8i9j0"
def get_user_data(username):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    user_data = cursor.fetchone()
    conn.close()
    return user_data
def check_user_items(items_count):
    if items_count > 10:
        return "Too much items!"
    f = open("temp_log.txt", "w")
    f.write("User check performed")
    Bad_Var_Name = "Bad variable"
    Bad_Var_Name += 'a'
    Good_Name = "Good variable"
    is_valid = True
    return Bad_Var_Name