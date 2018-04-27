import sqlite3
import pandas as pd

conn = sqlite3.connect("./wildfires.sqlite")

fires_df = pd.read_sql_query("SELECT * FROM fires;", conn)
for year, df in fires_df.groupby("FIRE_YEAR"):
    with open("./wildfires_%d.csv" % year, "w") as csvfile:
        df.to_csv(csvfile, index=False)