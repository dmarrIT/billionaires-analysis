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
con = sqlite3.connect("./db/billionaires.db")

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

# 1. In the latest year, what was the total share of net worth by nationality in this data set?

query = """
SELECT nationality, SUM(net_worth_billion_usd) as total_billion_usd
FROM billionaires
WHERE year = (SELECT MAX(year) FROM billionaires)
GROUP BY nationality
ORDER BY total_billion_usd DESC
"""

df_by_nationality = pd.read_sql_query(query, con)
df_by_nationality["pct_of_global"] = (df_by_nationality["total_billion_usd"] / df_by_nationality["total_billion_usd"].sum()) * 100
print(df_by_nationality)

# 2. What is the mean and median net worth for the latest year in this data set?

latest_year = cleaned_data["year"].max()
snapshot_df = cleaned_data[cleaned_data["year"] == latest_year]

mean_net_worth = snapshot_df["net_worth_billion_usd"].mean()
median_net_worth = snapshot_df["net_worth_billion_usd"].median()
print(mean_net_worth, median_net_worth)

# 3. What is the mean and median age for the latest year in this data set?

mean_age = snapshot_df["age"].mean()
median_age = snapshot_df["age"].median()
print(mean_age, median_age)

# 4. What are the top sources of wealth by net worth for the latest year in this data set?

query = """
SELECT source_wealth, SUM(net_worth_billion_usd) as total_billion_usd
FROM billionaires
WHERE year=(SELECT MAX(year) FROM billionaires)
GROUP BY source_wealth
ORDER BY total_billion_usd DESC
"""

df_by_source = pd.read_sql_query(query, con)
print(df_by_source)

# 5. Who are the top three trending billionaires from 2002-2021?

query = """
WITH per_person_years AS (
  SELECT name, MIN(year) AS first_year, MAX(year) AS last_year, COUNT(DISTINCT year) AS n_years
  FROM billionaires
  GROUP BY name
),
first_last AS (
  SELECT
    p.name,
    p.first_year,
    p.last_year,
    p.n_years,
    f.net_worth_billion_usd AS first_worth,
    l.net_worth_billion_usd AS last_worth
  FROM per_person_years p
  JOIN billionaires f
    ON f.name = p.name AND f.year = p.first_year
  JOIN billionaires l
    ON l.name = p.name AND l.year = p.last_year
)
SELECT
  name,
  first_year,
  last_year,
  first_worth,
  last_worth,
  (last_worth - first_worth) AS abs_gain,
  CASE WHEN first_worth > 0 THEN (last_worth - first_worth) / first_worth ELSE NULL END AS pct_gain,
  (last_year - first_year) AS years_span
FROM first_last
WHERE n_years >= 3
  AND first_worth IS NOT NULL
  AND last_worth  IS NOT NULL
  AND first_worth > 0
ORDER BY abs_gain DESC
LIMIT 3;
"""

df_top_3_trending = pd.read_sql_query(query, con)
print(df_top_3_trending)

# =========== Visualize insights ==========

# plot net worth share by nationality
df_by_nationality.set_index("nationality")["total_billion_usd"].plot(
    kind="pie",
    figsize=(8, 8),
    autopct="%.1f%%",
    startangle=90,
    legend=False,
    ylabel=""
)
plt.title(f"Share of Billionaire Net Worth by Nationality ({latest_year})")
pathlib.Path("./plots").mkdir(parents=True, exist_ok=True)
plt.savefig("./plots/net_worth_by_nationality.png", dpi=300)