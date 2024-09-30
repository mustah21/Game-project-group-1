import mysql.connector
import random
from geopy import distance

connection= mysql.connector.connect(
    host='127.0.0.1',
    port= 3306,
    database= 'time_travellers_quest',
    user='root',
    password= 'asus',
    autocommit=True,
)

def fetch_airports ():
    sql= """ SELECT airport.name AS airport_name, country.name AS country_name, ident, type, latitude_deg, longitude_deg
    FROM airport, country 
    WHERE airport.iso_country = country.iso_country AND country.continent = "AS"
    AND type="large_airport"
     ORDER BY RAND() LIMIT 32;"""
    cursor= connection.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

def fetch_targets():
    sql = f"SELECT * FROM goal"
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


def get_targets_info():
    sql= "SELECT * FROM target"
    cursor= connection.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

def create_player (p_name, start_money, start_fuel, start_time, current_airport,air_ports):
    sql = "INSERT INTO player (name,money,fuel,time,current_airport_id) VALUES (%s, %s, %s, %s, %s)"
    cursor = connection.cursor(dictionary=True)
    cursor.execute(sql,(p_name,start_money,start_fuel,start_time, current_airport))
    play_id= cursor.lastrowid

    targets= get_targets_info()
    target_list=[]
    for target in targets:
        for i in range(0, target['probability'], 1):
            target_list.append(target['id'])

    airports_with_targets= air_ports[1:].copy()
    random.shuffle(airports_with_targets)

    for i, targ_id in enumerate(target_list):
        sql= "INSERT INTO target_location (target_id, location, player_id) VALUES (%s, %s, %s)"
        cursor= connection.cursor(dictionary=True)
        cursor.execute(sql,(play_id,airports_with_targets[i]["ident"],targ_id))
    return play_id

def get_airport_by_icao(icao):
    sql= f"""SELECT airport.name AS airport_name, country.name AS country_name, ident, type, latitude_deg, longitude_deg
    FROM airport, country
    WHERE airport.iso_country = country.iso_country AND
    ident=%s"""
    cursor=connection.cursor()
    cursor.execute(sql,(icao,))
    result=cursor.fetchone()
    return result

def check_target(targ_id, current_airport):
    sql = f"""SELECT airport.ident, airport.name as airport_name, target.id, target.name AD target_name, target.value
    FROM airport
    JOIN target_location ON target_location.location=airport.ident
    JOIN target ON target.id= target_location.target_id
    WHERE player= %s AND
    airport= %s"""
    cursor = connection.cursor(dictionary=True)
    cursor.execute(sql, (targ_id, current_airport))
    result = cursor.fetchone()
    if result is None:
        return False
    return result

def calculate_distance_by_coordinates(current_airport, target_airport):
    first = get_airport_by_icao(current_airport)
    second= get_airport_by_icao(target_airport)
    return distance.distance((first['latitude_deg'], first['longitude_deg']),( second['latitude_deg'], second['longitude_deg'])).km

def airports_in_domain(icao_code,air_ports,player_fuel):
    in_domain_airports=[]
    for air_port in air_ports:
        dist_ance= calculate_distance_by_coordinates(icao, air_port['ident'])
        if 0<dist_ance<=player_fuel:
            in_domain_airports.append(air_port)
    return in_domain_airports

def update_location(icao, player_fuel, money, goal_id):
    sql = f'''UPDATE player SET current_airport_id = %s, fuel = %s, money = %s WHERE id = %s'''
    cursor = connection.cursor(dictionary=True)
    cursor.execute(sql, (icao, player_fuel, money,goal_id))