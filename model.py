import pandas as pd
import mesa
import numpy as np
from agent import household

# Load the dataframe
df_1427 = pd.read_csv("data/Catasto_1427.csv")

# Gini coefficient function
def compute_gini(model):
    wealths = [agent.wealth for agent in model.agents]
    
    if not wealths or len(wealths) == 0:
        return 0
    
    # Handle negative wealth
    wealths = [max(0, w) for w in wealths]
    total_wealth = sum(wealths)
    
    if total_wealth == 0:
        return 0
    
    # Sort wealths
    sorted_wealths = sorted(wealths)
    n = len(wealths)
    
    # Gini formula
    cumsum = 0
    for i, wealth in enumerate(sorted_wealths):
        cumsum += (i + 1) * wealth
    
    gini = (2 * cumsum) / (n * total_wealth) - (n + 1) / n
    
    return gini

# Create the Renaissance Florence model
class Florence(mesa.Model):

    def __init__(self, n, df_1427, forced_loans_dict, mortality_dict, seed):      # Seed makes the model reproducible by controlling RNG's
        super().__init__(seed=seed)
        self.num_agents = len(df_1427)
        self.year = 1427                            # Starting year
        #self.year_abstract = 1427.0                # Starting year alternate representation by adding .25 to every season
        #self.quarter = 1                           # 1=Winter, 2=Spring, 3=Summer, 4=Fall
        self.war = True                             # At the start of the simulation Florence is at war with Milan.
        self.Cosimo = False                         # Cosimo de' Medici has not yet come to power.
        self.forced_loans_dict = forced_loans_dict  # Dictionary with total forced loans, includes taxes
        self.mortality_dict = mortality_dict        # Dictionary with mortality rates in plague years
        self.instability = 0                        # Baseline instability is zero
        self.instability_input = 0
        self.instability_decay_rate = 0.5           # 50% instability decay per year
        self.tax_total = 0                          # Initiate total tax variable
        self.taxable_total = 0
        self.tax_eligible_households = 0
        self.tax_percentage = 0.1525                # Literature value between 1428-1433
        self.plague = False
        self.population = 38269                     # The sum of all bocche for all households
        self.population_new = 0
        self.deaths = 0
        
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Gini": compute_gini,
                "Total_Households": lambda m: len(m.agents),
                "Total_Population": lambda m: sum(a.bocche for a in m.agents),
                "Avg_Household_Size": lambda m: np.mean([a.bocche for a in m.agents]),
                "Total_Wealth": lambda m: sum(a.wealth for a in m.agents),
                "Avg_Wealth": lambda m: np.mean([a.wealth for a in m.agents]),
                "Median_Wealth": lambda m: np.median([a.wealth for a in m.agents]),
                "Poor_Households": lambda m: len([a for a in m.agents if a.wealth_class == 0]),
                "Lower_Mid_Households": lambda m: len([a for a in m.agents if a.wealth_class == 1]),
                "Upper_Mid_Households": lambda m: len([a for a in m.agents if a.wealth_class == 2]),
                "Wealthy_Households": lambda m: len([a for a in m.agents if a.wealth_class == 3]),
                "Affluent_Households": lambda m: len([a for a in m.agents if a.wealth_class == 4]),
                "Elite_Households": lambda m: len([a for a in m.agents if a.wealth_class == 5]),
                "Top_10_Percent_Wealth_Share": lambda m: sum(sorted([a.wealth for a in m.agents])[-len(m.agents)//10:]) / sum(a.wealth for a in m.agents) if sum(a.wealth for a in m.agents) > 0 else 0,
                "Instability": lambda m: m.instability,
                "Avg_Debt_Ratio": lambda m: np.mean([a.deductions/a.investments if a.investments > 0 else 0 for a in m.agents])
            },
            agent_reporters={
                "Wealth": "wealth",
                "Investments": "investments",
                "Deductions": "deductions",
                "Bocche": "bocche",
                "Wealth_Class": "wealth_class"
            }
        )
        
        # Create agents
        for i, row in df_1427.iterrows():        # Arti Maggiori agents
            household.create_agents(
                model=self, 
                n=n,
                investments = row["total"],
                deductions = row["deductions"],
                trade = row["trade_last2"],
                bocche = row["bocche"],
                )

        ### Potential city government agent ###            
        # city_government.create_agents(
        #     model=self,
        #     n=1,
        #     treasury = -682000,             # The amount of money the city starts with
        # )

        self.classified_agents = {i: [] for i in range(6)}      # This will create a list for each wealth class

        print(f"Simulation started.")
        print(f"There are {str(self.num_agents)} households.")
        
        self.datacollector.collect(self)    # Collect data initial circumstances

    def step(self):         # Advance the model by one step
        
        # Advance the calendar
        self.year += 1
        print(f"\nYear {str(self.year)}.")
        print(f"Population: {str(self.population)}.")        

        ### Alternative for using quarters as timestep: ###
        # self.quarter += 1       
        # self.year_abstract += 0.25
        # if self.quarter > 4:
        #     self.quarter = 1
        #     self.year += 1
        # print(f"Year {str(self.year)}, quarter {str(self.quarter)}.")

        # Historical events
        if self.year == 1429:
            print("War with Milan ends.")
            self.war = False
        if self.year == 1430:
            print("War with Lucca begins.")
            self.war = True
        if self.year == 1434:
            print("War with Lucca ends.")
            self.war = False
            print("Cosimo de' Medici comes to power.")
            self.Cosimo = True
        if self.year == 1451:
            print("War with Venice and Aragon begins.")  
            self.war = True
        if self.year == 1454:
            print("War with Venice and Aragon ends.")
            self.war = False

        # Calculate tax percentage by dividing the required tax amount by taxable amount 
        self.tax_total = self.forced_loans_dict[self.year]   # Total forced loans that year, includes taxes
        self.agents.do("calculate_taxable")
        self.taxable_total = sum(agent.taxable for agent in self.agents)
        self.tax_eligible_households = sum(1 for agent in self.agents if agent.taxable > 0)
        self.tax_percentage = self.tax_total / self.taxable_total
        if self.tax_percentage > 0.9:                   # Hard limit of 90%
            self.tax_percentage = 0.9

        # Calculate the instability as a function of total taxes and whether there is a plague
        if self.year in self.mortality_dict and self.mortality_dict[self.year] > 20:
                self.plague = True
                print("An epidemic has struck the city.")
                self.instability_input = (self.tax_total / 1000000 * 1.5) * 0.65
        else:
            self.plague = False
            self.instability_input = (self.tax_total / 1000000) * 0.65
        self.instability = (self.instability * self.instability_decay_rate) + self.instability_input
        if self.instability > 1:
            self.instability = 1

        # Deaths are modeled with a simple decay function based on the known populations in 1427 and 1458.
        self.population_new = 38269 * np.exp(-0.0058084 * (self.year - 1427))
        self.births = round(self.population*.05)    # Average birthrate in Italy in the 15th century.
        self.deaths = round(self.population + self.births - self.population_new)
        self.population = round(self.population_new)
        
        # Distribute deaths randomly
        for _ in range(self.deaths):
            #household = self.random.choice(list(self.agents))
            household = self.random.choices(
                self.agents, 
                weights=[agent.bocche for agent in self.agents]
            )[0]
            household.bocche -= 1
            if household.bocche <= 0:                           # Household dies if members reach 0
                heirs_n = self.random.randint(1, 5)             # Between 1 and 5 random heirs
                heirs = []
                for _ in range(heirs_n):
                    heirs.append(self.random.choice(self.agents))
                if household.wealth >= 0:                       # Distribute remaining wealth randomly
                    for heir in heirs:
                        heir.investments += household.investments / heirs_n
                        heir.deductions += household.deductions / heirs_n
                else:                                           # Heir is a creditor in this case
                    for heir in heirs:                    
                        heir.investments += household.investments / heirs_n  
                self.agents.remove(household)

        # Distribute births randomly
        for _ in range(self.births):
            #household = self.random.choice(list(self.agents))
            household = self.random.choices(
                self.agents, 
                weights=[agent.bocche for agent in self.agents]
            )[0]            
            household.bocche += 1        

        # Fill the wealth class sorted list
        for agent in self.agents:
            self.classified_agents[agent.wealth_class].append(agent) 

        # Agent actions
        #print("Households are producing goods, trading, paying taxes...")
        self.agents.shuffle_do("trading_phase")         # Every agent produces value and randomly trades with other agents
        self.agents.do("recalculation_phase")           # Every agent manages their wealth and is taxed
        #self.agents.do("population_changes")            # Households die and split
        
        self.num_agents = len(self.agents)
        print(f"This year {str(self.deaths)} people have died. There are now {str(self.num_agents)} households.")
        
        # Collect data
        self.datacollector.collect(self)       
