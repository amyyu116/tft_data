Tech stack:
RIOT API
PostgreSQL database (local)
Apache Airflow

### Ubuntu Setup

log into ubuntu
`wsl -d Ubuntu`

### activate virtual environment

`source airflow_venv/bin/activate`

### local postgresql database

start command
`sudo service postgresql start`

switch to admin perms
`sudo -i -u postgres`

setting up tft db perms on postgreSQL

```
CREATE DATABASE tft_data;
CREATE USER admin WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE tft_data TO admin;
\q
```

### populating the DB

`python3 tft_players.py`
`python3 tft_match_history.py`
`python3 tft_match.py`
