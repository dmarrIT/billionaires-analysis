import pandas as pd
import pathlib
import matplotlib.pyplot as plt
import sqlite3

# ========== Read data =========

raw_data = pd.read_csv("./data/billionaires.csv")
# print(raw_data.shape, raw_data.info(),'\n', raw_data.head(10))

# ========== Clean data ==========

raw_data.rename(columns={
    "net_worth": "net_worth_billion_usd",
    "natinality": "nationality"
    }, inplace=True)
# print(raw_data.head(10))

# standardize object data types
for col in raw_data.columns:
    if raw_data[col].dtype == "object":
        raw_data[col] = raw_data[col].str.strip()

# # check for missing values
# print(raw_data.isnull().sum())

# ensure data type is correct for numeric values
raw_data["net_worth_billion_usd"] = pd.to_numeric(raw_data["net_worth_billion_usd"], errors="coerce")
raw_data["age"] = pd.to_numeric(raw_data["age"], errors="coerce")
raw_data["year"] = pd.to_numeric(raw_data["year"], errors="coerce")
raw_data["rank"] = pd.to_numeric(raw_data["rank"], errors="coerce")

# export cleaned data
cleaned_data = raw_data
cleaned_data.to_csv("./exports/billionaires_cleaned.csv", index=False)

# ========== Add cleaned data to db ==========

# create db folder and connection
pathlib.Path("./db").mkdir(parents=True, exist_ok=True)
con = sqlite3.connect("./db/spotify.db")

# load cleaned data to db
cleaned_data.to_sql("billionaires", con, if_exists="replace", index=False)

# add indexes for performance
con.execute("CREATE INDEX IF NOT EXISTS idx_nationality ON billionaires(nationality)")
con.execute("CREATE INDEX IF NOT EXISTS idx_networth ON billionaires(net_worth_billion_usd)")
con.execute("CREATE INDEX IF NOT EXISTS idx_age ON billionaires(age)")
con.execute("CREATE INDEX IF NOT EXISTS idx_source ON billionaires(source_wealth)")
con.commit()

# # create cursor, view database for testing
# cur = con.cursor()
# cur.execute("PRAGMA table_info(billionaires);")
# schema = cur.fetchall()
# for col in schema:
#     print(col)


# ========== Answer questions ==========

#TODO restructure questions and queries to account for the fact that this is a top ten list with duplicate names, sources, etc. over multiple years

# What is the percentage breakdown of billionaires by nationality in this data set?

query = """
SELECT nationality, SUM(net_worth_billion_usd) as total_billion_usd
FROM billionaires
GROUP BY nationality
ORDER BY total_billion_usd DESC
"""

df_by_nationality = pd.read_sql_query(query, con)
df_by_nationality["pct_of_global"] = (df_by_nationality["total_billion_usd"] / df_by_nationality["total_billion_usd"].sum()) * 100
print(df_by_nationality)

# What is the mean and median net worth in this data set?

mean_net_worth = cleaned_data["net_worth_billion_usd"].mean()
median_net_worth = cleaned_data["net_worth_billion_usd"].median()
print(mean_net_worth, median_net_worth)

# What is the mean and median age in this data set?

mean_age = cleaned_data["age"].mean()
median_age = cleaned_data["age"].median()
print(mean_age, median_age)

# Which what are the top five sources of wealth by net worth in this data set?

query = """
SELECT source_wealth, SUM(net_worth_billion_usd) as total_billion_usd
FROM billionaires
GROUP BY source_wealth
ORDER BY total_billion_usd DESC
"""

df_by_source = pd.read_sql_query(query, con)
print(df_by_source)

# Who are the top three trending billionaires?

# =========== Visualize insights ==========

