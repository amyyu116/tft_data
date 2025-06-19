import os
import requests
import psycopg2
import time
import json
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

print("RIOT_API_KEY:", RIOT_API_KEY)
print("DB_NAME:", DB_NAME)
print("USER:", USER)
print("PASSWORD:", PASSWORD)


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
cur.execute("SELECT puuid, game_name, tag_line FROM players WHERE game_name ='monoseiros';")
riot_tags = cur.fetchall()
conn.commit()

cur.execute("""
CREATE TABLE IF NOT EXISTS match (
    puuid TEXT,
    match_id TEXT,
    game_mode TEXT,
    game_datetime BIGINT, 
    patch TEXT,
    level INT,
    placement INT, 
    damage_dealt INT,
    gold_left INT,
    last_round INT,
    PRIMARY KEY (puuid, match_id)
);
""")
cur.execute("""
CREATE TABLE IF NOT EXISTS board_details (
    puuid TEXT, 
    match_id TEXT,
    traits JSONB,
    units JSONB,
    PRIMARY KEY (puuid, match_id)
);
""")
conn.commit()

def get_puuid(game_name, tag_line):
    url = f"https://{REGION_ROUTING}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()
    return res.json()["puuid"]


def get_all_match_ids(puuid, batch_size=100):
    all_match_ids = []
    start = 0

    while True:
        url = (
            f"https://{REGION_ROUTING}.api.riotgames.com/tft/match/v1/matches/by-puuid/"
            f"{puuid}/ids?start={start}&count={batch_size}"
        )
        try:
            res = requests.get(url, headers=HEADERS)
            if res.status_code == 429:
                retry_after = int(res.headers.get("Retry-After", 1))
                print(f"[429] Match ID batch rate limited. Sleeping {retry_after}s")
                time.sleep(retry_after)
                continue
            res.raise_for_status()
            match_ids_batch = res.json()

            if not match_ids_batch:
                break

            for match_id in match_ids_batch:
                match_url = f"https://{REGION_ROUTING}.api.riotgames.com/tft/match/v1/matches/{match_id}"
                try:
                    match_res = requests.get(match_url, headers=HEADERS)
                    if match_res.status_code == 429:
                        retry_after = int(match_res.headers.get("Retry-After", 1))
                        print(f"[429] Match details rate limited. Sleeping {retry_after}s")
                        time.sleep(retry_after)
                        continue  # retry this match_id later (or skip)
                    match_res.raise_for_status()
                    match_data = match_res.json()
                    set_number = match_data["info"].get("tft_set_number", -1)
                    if set_number in (14, 10):
                        if set_number == 14:
                            all_match_ids.append(match_id)
                    else:
                        return all_match_ids
                except requests.RequestException as e:
                    print(f"Error retrieving match {match_id}: {e}")
                    continue

                time.sleep(1.2)

            start += batch_size
            time.sleep(1.2)

        except requests.RequestException as e:
            print(f"Error getting match IDs for {puuid}: {e}")
            break

    return all_match_ids


def get_match_details(match_id):
    url = f"https://{REGION_ROUTING}.api.riotgames.com/tft/match/v1/matches/{match_id}"

    while True:
        try:
            response = requests.get(url, headers=HEADERS)
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 1))
                print(f"[429] Rate limited. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)
                continue
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            print(f"[HTTP ERROR] {response.status_code}: {e}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"[REQUEST ERROR] {e}")
            return None

for player in riot_tags:
    print(player)
    try:
        puuid = player[0]
        game_name = player[1]
        tag_line = player[2]
        match_ids = get_all_match_ids(puuid)

        for i, match_id in enumerate(match_ids):
            match_data = get_match_details(match_id)
            if not match_data:
                continue

            set_number = match_data["info"].get("tft_set_number", 0)
            if set_number not in CURRENT_SETS or set_number != 14:
                continue            
            game_datetime = match_data["info"]["game_datetime"]
            game_mode = match_data["info"]["tft_game_type"]
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

                # insert into DB (skip if already exists)
                try:
                    cur.execute("""
                        INSERT INTO match (
                            puuid,
                            match_id,
                            game_mode,
                            game_datetime, 
                            patch,
                            level,
                            placement,
                            damage_dealt,
                            gold_left,
                            last_round
                        )
                        VALUES (
                            %s,  -- puuid
                            %s,  -- match_id
                            %s,  -- game_mode
                            %s,  -- game_datetime, 
                            %s,  -- patch
                            %s,  -- level
                            %s,  -- placement
                            %s,  -- damage_dealt
                            %s,  -- gold_left
                            %s   -- last_round
                        )
                        ON CONFLICT (puuid, match_id) DO NOTHING;
                    """, (
                        puuid,
                        match_id,
                        game_mode,
                        game_datetime,
                        patch,
                        level,
                        placement,
                        dmgDealt,
                        goldLeft,
                        lastRound,
                    ))
                    print(f"Successfully inserted match {match_id}. ({i}/{len(match_ids)})")
                except Exception as e:
                    print(f"Error inserting match {match_id}: {e}")
                    
                try:
                    cur.execute("""
                        INSERT INTO board_details (
                            puuid,
                            match_id,
                            traits,
                            units
                        )
                        VALUES (
                            %s,  -- puuid
                            %s,  -- match_id
                            %s,  -- traits (JSONB)
                            %s   -- units (JSONB)
                        )
                        ON CONFLICT (puuid, match_id) DO NOTHING;
                    """, (
                        puuid,
                        match_id,
                        json.dumps(traits),
                        json.dumps(units)
                    ))
                except Exception as e:
                    print(f"Error inserting board details for match {match_id}: {e}")
            # respect rate limit
            time.sleep(1.2) 
        print(f"Completed {player}'s games.")
        conn.commit()

    except Exception as e:
        print(f"Error with player {game_name}#{tag_line}: {e}")

cur.close()
conn.close()
