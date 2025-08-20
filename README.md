# Billionaires Data Analysis

This project explores billionaire data from 2002–2021.  
It uses **Pandas**, **SQLite**, and **Matplotlib** to clean, store, query, and visualize insights.

---

## Features

1. **Data Cleaning**
   - Fixes column naming issues (`natinality` → `nationality`)
   - Standardizes data types
   - Exports a cleaned CSV

2. **Database Integration**
   - Loads cleaned data into SQLite
   - Adds indexes for performance

3. **SQL Analysis**
   - Net worth share by nationality
   - Mean and median net worth/age
   - Top sources of wealth
   - Top 3 trending billionaires (2002–2021)

4. **Visualizations**
   - Pie chart: Net worth share by nationality
   - Histogram: Net worth distribution with mean/median markers
   - Boxplot: Age distribution with mean/median markers
   - Bar chart: Top sources of wealth
   - Line chart: Top 3 trending billionaires over time