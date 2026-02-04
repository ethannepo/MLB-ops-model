import sqlite3 as sql
import pandas as pd
import glob
from pathlib import Path

# Create empty DB file

Path("data/complete_data.db").touch()

db_file = "data/complete_data.db"
with sql.connect(db_file,timeout=1000) as conn:
    cur = conn.cursor()

for file in glob.glob("data/*.csv"):
    df = pd.read_csv(file)
    print("Creating Table:", file[5:-4].replace("-",""))
    df.to_sql(file[5:-4].replace("-",""), conn, if_exists='replace', index=False)

conn.commit()

colors_with_abbr_query = """
CREATE TABLE colors_with_abbr AS
SELECT 
    a.full_name AS Name,
    a.abbreviation AS Abbr,
    c.hex AS Color
FROM abbr a
JOIN colors c 
    ON a.full_name = c.Team
"""
conn.execute(colors_with_abbr_query)
conn.commit()

players_teams_colors_query = """
CREATE TABLE players_teams_colors AS
SELECT 
    t.Name AS Player,
    t.Team AS Team,
    c.Color AS Color,
    NULL AS OPS,
    NULL AS Predicted_OPS
FROM team_data t
JOIN colors_with_abbr c
    ON t.Team = c.Abbr
"""
conn.execute(players_teams_colors_query)
conn.commit()

add_stats_query = """
UPDATE players_teams_colors
SET
    OPS = o.OPS,
    Predicted_OPS = o.Predicted_OPS
FROM ops_diff_2025 o
WHERE o.Player = players_teams_colors.Player;
"""
conn.execute(add_stats_query)
conn.commit()

conn.close()

