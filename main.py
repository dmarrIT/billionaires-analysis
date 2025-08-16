import pandas as pd
import pathlib
import matplotlib.pyplot as plt
import sqlite3

# ========== Read data =========

data = pd.read_csv("./data/billionaires.csv")
# print(data.shape, data.info(),'\n', data.head(10))

# ========== Clean data ==========

data.rename(columns={
    "net_worth": "net_worth_billion_usd",
    "natinality": "nationality"
    }, inplace=True)
# print(data.head(10))

# standardize object data types
for col in data.columns:
    if data[col].dtype == "object":
        data[col] = data[col].str.strip()

# check for missing values
print(data.isnull().sum())

# ensure data type is correct for numeric values
data["net_worth_billion_usd"] = pd.to_numeric(data["net_worth_billion_usd"], errors="coerce")
data["age"] = pd.to_numeric(data["age"], errors="coerce")
data["year"] = pd.to_numeric(data["year"], errors="coerce")
data["rank"] = pd.to_numeric(data["rank"], errors="coerce")

# export cleaned data
cleaned_data = data
cleaned_data.to_csv("./exports/billionaires_cleaned.csv", index=False)

# ========== Add cleaned data to db ==========

pathlib.Path("./db").mkdir(parents=True, exist_ok=True)
con = sqlite3.connect("./db/spotify.db")

# ========== Answer questions ==========

# What is the percentage breakdown of billionaires by nationality in this data set?

# What is the mean, median, and mode net worth in this data set?

# What is the mean, median, and mode age in this data set?

# Which what are the top five sources of wealth by net worth in this data set?

# What are the top three trending billionaires?

# =========== Visualize insights ==========

