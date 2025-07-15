import os
import requests
import psycopg2
import time
from dotenv import load_dotenv

load_dotenv()
# loading env variables
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
DB_NAME = os.getenv("DB_NAME")
USER = "admin"
PASSWORD = os.getenv("PASSWORD")

HEADERS = {"X-Riot-Token": RIOT_API_KEY}
REGION = "na1"
REGION_ROUTING = "americas"

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
    summoner_level BIGINT,
    revision_date BIGINT,
    icon_id INT
);
""")
conn.commit()


riot_tags = [
    {"gameName": "monoseiros", "tagLine": "NA1"},
    {"gameName": "Dragon Venom8888", "tagLine": "NA1"},
]

def get_puuid(game_name, tag_line):
    url = f"https://{REGION_ROUTING}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()
    return res.json()["puuid"]



for player in riot_tags:
    game_name = player["gameName"]
    tag_line = player["tagLine"]
    
    puuid = get_puuid(game_name, tag_line)

    summoner_url = f"https://{REGION}.api.riotgames.com/tft/summoner/v1/summoners/by-puuid/{puuid}"
    summoner_r = requests.get(summoner_url, headers=HEADERS)
    if summoner_r.status_code != 200:
        print(f"Error for {player} (summoner): {summoner_r.status_code}")
        continue
    summoner_data = summoner_r.json()
    print(summoner_data)
    cur.execute("""
        INSERT INTO players (puuid, game_name, tag_line, summoner_level, revision_date, icon_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (puuid) DO UPDATE SET
            game_name = EXCLUDED.game_name,
            tag_line = EXCLUDED.tag_line,
            summoner_level = EXCLUDED.summoner_level,
            revision_date = EXCLUDED.revision_date,
            icon_id = EXCLUDED.icon_id;
    """, (
        puuid, game_name, tag_line,
        summoner_data["summonerLevel"], summoner_data["revisionDate"], summoner_data["profileIconId"]
    ))
    conn.commit()
    print(f"Saved or updated: {cur}")