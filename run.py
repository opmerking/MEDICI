# Main simulation runner for agent-based modeling of Renaissance Florence.
# Runs the simulation with 30 timesteps covering a year each by default.
# Also creates three different wealth distribution plots, although more plots are possible.
# Utilizes Mesa 3.2.0.
#
# Fabian Lohmann, July 2025
# FDLohmann@gmail.com

# %% Data preprocessing
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

#%%   Run the simulation once
model = Florence(1, df_1427, forced_loans_dict, mortality_dict, seed=1)
for _ in range(30):          # Run the simulation with 30 timesteps.
    model.step()
print("Simulation completed.")
data = model.datacollector.get_model_vars_dataframe()


#%% Plots
#---------------------------------------------------------------------#

### Gini coefficient evolution plot
plt.figure(figsize=(8, 3.8))
plt.plot(data.index + 1427, data['Gini'], color='#1f77b4', marker='o')
plt.xlabel('Year')
plt.ylabel('Gini Coefficient')
plt.grid(True)
plt.tight_layout()
plt.savefig('Gini.png', dpi=300)
plt.show()



### Average wealth plot
plt.figure(figsize=(8, 3.8))
years = data.index + 1427
plt.plot(years, data['Avg_Wealth'], marker='o', color='#1f77b4', label='Average wealth')

# Highlight wars (shaded regions)
war_periods = [
    (1424, 1428),
    (1429, 1433),
    (1451, 1454)
]

for start, end in war_periods:
    plt.axvspan(start, end, color='gray', alpha=0.2, label='War' if start == 1424 else None)

# Mark epidemics (dashed lines) 
epidemic_years = [1430, 1434, 1437, 1438, 1449, 1450, 1457]
for year in epidemic_years:
    plt.axvline(year, color='#1f77b4', linestyle='--', alpha=0.6, label='Epidemic' if year == 1430 else None)

plt.xlabel('Year')
plt.ylabel('Average household wealth')
plt.grid(True)
plt.legend(
    loc='lower left',
    frameon=True,
    facecolor='white',
    framealpha=0.9,
    fancybox=True
)
plt.tight_layout()
plt.savefig('avg_wealth.png', dpi=300)
plt.show()


### Bar plot, wealth distribution

# Define wealth class thresholds
bins = [0, 29, 210, 893, 2634, 14299, float('inf')]
labels = ['Poor', 'Lower_Mid', 'Upper_Mid', 'Wealthy', 'Affluent', 'Elite']
df_1457['total2'] = pd.cut(df_1457['total'], bins=bins, labels=labels, right=False)

# Count households in each class
historical_counts_dict = df_1457['total2'].value_counts().reindex(labels)
historical_counts = historical_counts_dict.tolist()

# Get initial and final counts from collected_data
initial_counts = [
    collected_data['Poor_Households'].iloc[0],
    collected_data['Lower_Mid_Households'].iloc[0],
    collected_data['Upper_Mid_Households'].iloc[0],
    collected_data['Wealthy_Households'].iloc[0],
    collected_data['Affluent_Households'].iloc[0],
    collected_data['Elite_Households'].iloc[0]
]

final_counts = [
    collected_data['Poor_Households'].iloc[-1],
    collected_data['Lower_Mid_Households'].iloc[-1],
    collected_data['Upper_Mid_Households'].iloc[-1],
    collected_data['Wealthy_Households'].iloc[-1],
    collected_data['Affluent_Households'].iloc[-1],
    collected_data['Elite_Households'].iloc[-1]
]

wealth_classes = ['Poor\n(0–29)', 'Lower Middle\n(29–210)', 'Upper Middle\n(210–893)', 
                  'Wealthy\n(893–2,634)', 'Affluent\n(2,634–14,299)', 'Elite\n(14,299+)']

x = np.arange(len(wealth_classes))
width = 0.2

fig, ax = plt.subplots(figsize=(8, 3))

bars1 = ax.bar(x - 1.5*width, initial_counts, width, label='1427', color='#1f77b4', alpha=0.8)
bars2 = ax.bar(x - 0.5*width, historical_counts, width, label='1457 Historical', color="#165581", alpha=0.8)
bars3 = ax.bar(x + 0.5*width, final_counts, width, label='1457 Simulated', color="#0f3957", alpha=0.8)

ax.set_xlabel('Wealth Class (Florins)', fontsize=12)
ax.set_ylabel('Number of Households', fontsize=12)


ax.set_xticks(x)
ax.set_xticklabels(wealth_classes, fontsize=10)
ax.legend(fontsize=8)

# Add value labels
for bars in [bars1, bars2, bars3]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 50,
                f'{int(height):,}', ha='center', va='bottom', fontsize=6)

max_height = max(max(initial_counts), max(historical_counts), max(final_counts))
ax.set_ylim(top=max_height * 1.1)
ax.set_yticks(np.arange(0, max_height * 1, 1000))

plt.tight_layout()
plt.savefig('bars.png', dpi=300)
plt.show()

#%%
