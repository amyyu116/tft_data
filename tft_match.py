import os
import requests
import psycopg2
import time
import json

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
CREATE TABLE IF NOT EXISTS match (
    puuid TEXT,
    match_id TEXT,
    game_mode TEXT,
    patch TEXT,
    level INT,
    placement INT, 
    damage_dealt INT,
    gold_left INT,
    last_round INT,
    traits JSONB,
    units JSONB,
    PRIMARY KEY (puuid, match_id)
);
""")
conn.commit()


riot_tags = [
    {"gameName": "monoseiros", "tagLine": "NA1"},
    {"gameName": "Dragon Venom8888", "tagLine": "NA1"},
]

def query_puuid(gameName, tagLine):
    cur.execute("""
        SELECT puuid FROM players 
        WHERE game_name = %s AND tag_line = %s
    """, (gameName, tagLine))
    
    result = cur.fetchone()
    if result:
        return result[0]  # puuid
    else:
        return None
    
def get_all_match_ids(puuid):
    cur.execute("""
        SELECT match_id FROM match_history 
        WHERE puuid = %s
    """, (puuid,))
    
    result = cur.fetchall()
    if result:
        return [row[0] for row in result]
    else:
        return []

def get_match_details(match_id):
    url = f"https://{REGION_ROUTING}.api.riotgames.com/tft/match/v1/matches/{match_id}"
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()
    return res.json()

for player in riot_tags:
    try:
        puuid = query_puuid(player["gameName"], player["tagLine"])
        match_ids = get_all_match_ids(puuid)

        for match_id in match_ids:
            match_data = get_match_details(match_id)
            game_datetime = match_data["info"]["game_datetime"]
            gameMode = match_data.get("game_variation") 
            patch = match_data["info"]["game_version"]

            for participant in match_data["info"]["participants"]:
                if participant["puuid"] != puuid:
                    continue
                placement = participant["placement"]
                level = participant["level"]
                dmgDealt = participant["total_damage_to_players"]
                goldLeft = participant["gold_left"]
                lastRound = participant["last_round"]
                traits = participant["traits"]
                units = participant["units"]

                # Insert into DB (skip if already exists)
                try:
                    cur.execute("""
                        INSERT INTO match (
                            puuid,
                            match_id,
                            game_mode,
                            patch,
                            level,
                            placement,
                            damage_dealt,
                            gold_left,
                            last_round,
                            traits,
                            units
                        )
                        VALUES (
                            %s,  -- puuid
                            %s,  -- match_id
                            %s,  -- game_mode
                            %s,  -- patch
                            %s,  -- level
                            %s,  -- placement
                            %s,  -- damage_dealt
                            %s,  -- gold_left
                            %s,  -- last_round
                            %s,  -- traits  (JSONB)
                            %s   -- units   (JSONB)
                        )
                        ON CONFLICT (puuid, match_id) DO NOTHING;
                    """, (
                        puuid,
                        match_id,
                        gameMode,
                        patch,
                        level,
                        placement,
                        dmgDealt,
                        goldLeft,
                        lastRound,
                        json.dumps(traits),   # dump to JSON if they’re Python objects
                        json.dumps(units)
                    ))
                except Exception as e:
                    print(f"Error inserting match {match_id}: {e}")
             
            time.sleep(1.2) 
        print(f"Completed {player}'s games.")
        conn.commit()

    except Exception as e:
        print(f"Error with player {player['gameName']}#{player['tagLine']}: {e}")

cur.close()
conn.close()
