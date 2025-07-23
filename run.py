# %% 

from model import Florence
import matplotlib.pyplot as plt
import pandas as pd
import mesa
import numpy as np
import seaborn as sns

# Load the dataframes
df_1427 = pd.read_csv("data/Catasto_1427.csv")
df_1457 = pd.read_csv("data/Catasto_1457.csv")

# Trades data preprocessing
df_1427['trade'] = df_1427['trade'].astype(str)                                 # Convert to string
df_1427['trade_last2'] = df_1427['trade'].str[-2:]                              # Only the last two digits are relevant
target_codes = {'21', '22', '23', '24', '25', '26', '27'}                       # Arti Maggiori codes
artimag_df = df_1427[df_1427['trade_last2'].isin(target_codes)]                 # Filter for the Arti maggiori
other_df = df_1427[~df_1427['trade_last2'].isin(target_codes)]                  # Filter for households not in Arti Maggiori
arti_mag_counts = artimag_df['trade_last2'].value_counts().sort_index()         # Count how many households per Arti Maggiori trade
population_1427 = df_1427['bocche'].sum()                                       # Counted population 1427
population_1457 = df_1457['bocche'].sum()                                       # Counted population 1457
df_1427['wealth'] = df_1427['total'] - df_1427['deductions']                    # Add wealth columns for easy calculations
artimag_df['wealth'] = artimag_df['total'] - artimag_df['deductions']           
other_df['wealth'] = other_df['total'] - other_df['deductions']

total_n = len(df_1427)                            # Total number of households
arti_mag_n = len(artimag_df)                      # Number of households in the Arti Maggiori
other_n = len(other_df)                           # Number of households not in the Arti Maggiori  

# Wealth distribution data
sum_total = df_1427['total'].sum()                # Total investments
sum_deductions = df_1427['deductions'].sum()      # Total deductions
net_wealth = sum_total - sum_deductions           # Aggregate private net wealth
tax_threshold = df_1427["taxable"].quantile(0.88) # The amount of taxable wealth required to be in the top 12 percent 
# Total wealth of each guild

# Tax rate based on forced loans
forced_loans = pd.read_csv("data/forcedloans.txt", sep='\t')                # Forced loans in each year
forced_loans_dict = dict(zip(forced_loans['Year'], forced_loans['Amount'])) # Convert to dictionary

# Population loss
mortality = pd.read_csv("data/mortality.txt", sep='\t')  # Mortality numbers per 1000 people
mortality_total = mortality['Mortality'].sum()
mortality_dict = dict(zip(mortality['Year'], mortality['Mortality']))
birthrate = .05 # per person

start_year = 1427

# Create grouped df to create groups of 100 people in the trade = other category for an alternate simulation configuration
other_df_sorted = other_df.sort_values(by='wealth', ascending=False)
other_df_sorted = other_df_sorted.reset_index(drop=True)
other_df_sorted['group'] = other_df_sorted.index // 100
other_df_grouped = other_df_sorted.groupby('group').sum(numeric_only=True)  # Contains groups of 100 people with all values summed.

#%%   Simple implementation
model = Florence(1, df_1427, forced_loans_dict, mortality_dict)
for _ in range(30):          # Run the simulation with x timesteps.
    model.step()
print("Simulation completed.")
collected_data = model.datacollector.get_model_vars_dataframe()

# %%

# Create 3 subplots in a single row
fig, axes = plt.subplots(3, 1, figsize=(10, 12))

# First plot
sns.lineplot(data=gini['Top_10_Percent_Wealth_Share'], ax=axes[0])
axes[0].set_title("Top 10 Percent Wealth Share")
axes[0].set_xlabel("Time")

# Second plot
sns.lineplot(data=gini['Avg_Wealth'], ax=axes[1])
axes[1].set_title("Average Wealth")
axes[1].set_xlabel("Time")

# Third plot
sns.lineplot(data=gini['Total_Wealth'], ax=axes[2])
axes[2].set_title("Total Wealth")
axes[2].set_xlabel("Time")

plt.tight_layout()
plt.show()


#%%
g = sns.lineplot(data=gini['Gini'])
g.set(title="Gini Coefficient over Time", ylabel="Gini Coefficient"); 
