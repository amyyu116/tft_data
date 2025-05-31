import os
import requests
import psycopg2
import time

# Load Riot API key
with open("riot_key.txt", 'r') as file:
    RIOT_API_KEY = file.read().strip()
    
with open("db_perms.txt", 'r') as file:
    DB_NAME = file.readline().strip()
    USER = file.readline().strip()
    PASSWORD = file.readline().strip()

HEADERS = {"X-Riot-Token": RIOT_API_KEY}
REGION = "na1"
REGION_ROUTING = "americas"

CURRENT_SETS = [14, 10]

# PostgreSQL connection
conn = psycopg2.connect(
    dbname=DB_NAME,  
    user=USER,
    password=PASSWORD,
    host="localhost",
    port="5432"
)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS players (
    puuid TEXT PRIMARY KEY,
    game_name TEXT,
    tag_line TEXT,
    summoner_id TEXT,
    summoner_name TEXT
);
""")
conn.commit()

cur.execute("""
CREATE TABLE IF NOT EXISTS match_history (
    match_id TEXT PRIMARY KEY,
    puuid TEXT,
    game_datetime BIGINT,
    placement INT,
    level INT
);
""")
conn.commit()

riot_tags = [
    # {"gameName": "monoseiros", "tagLine": "NA1"},
    {"gameName": "Dragon Venom8888", "tagLine": "NA1"},
]

def get_puuid(game_name, tag_line):
    url = f"https://{REGION_ROUTING}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()
    return res.json()["puuid"]

def get_all_match_ids(puuid, batch_size=100):
    all_match_ids = []
    start = 0
    
    current_set = True

    while current_set:
        url = (
            f"https://{REGION_ROUTING}.api.riotgames.com/tft/match/v1/matches/by-puuid/"
            f"{puuid}/ids?start={start}&count={batch_size}"
        )
        res = requests.get(url, headers=HEADERS)
        res.raise_for_status()

        match_ids_batch = res.json()
        if not match_ids_batch:
            break

        for match_id in match_ids_batch:
            match_url = f"https://{REGION_ROUTING}.api.riotgames.com/tft/match/v1/matches/{match_id}"
            match_res = requests.get(match_url, headers=HEADERS)
            match_res.raise_for_status()

            match_data = match_res.json()
            # print("found match data: ", match_data)
            set_number = match_data["info"]["tft_set_number"]
            
            if set_number not in CURRENT_SETS:
                current_set = False
                break
            elif set_number != 14:
                continue
            else:
                all_match_ids.append(match_id)
            time.sleep(1.2)

        start += batch_size

    return all_match_ids


def get_match_details(match_id):
    url = f"https://{REGION_ROUTING}.api.riotgames.com/tft/match/v1/matches/{match_id}"
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()
    return res.json()

for player in riot_tags:
    try:
        puuid = get_puuid(player["gameName"], player["tagLine"])
        match_ids = get_all_match_ids(puuid)

        for match_id in match_ids:
            match_data = get_match_details(match_id)
            game_datetime = match_data["info"]["game_datetime"]

            for participant in match_data["info"]["participants"]:
                if participant["puuid"] != puuid:
                    continue
                placement = participant["placement"]
                level = participant["level"]

                # Insert into DB (skip if already exists)
                try:
                    cur.execute("""
                        INSERT INTO match_history (match_id, puuid, game_datetime, placement, level)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (match_id) DO NOTHING;
                    """, (match_id, puuid, game_datetime, placement, level))
                    conn.commit()
                except Exception as e:
                    print(f"Error inserting match {match_id}: {e}")
            
            time.sleep(1.2) 

    except Exception as e:
        print(f"Error with player {player['gameName']}#{player['tagLine']}: {e}")

cur.close()
conn.close()
