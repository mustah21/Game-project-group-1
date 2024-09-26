def fetchw_airports():
    sql = f"SELECT iso_country, ident, name, type, latitude_deg, longitude_deg FROM airport WHERE continent = 'AS' ORDER by RAND()LIMIT 32"
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

def