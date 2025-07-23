# Agent class for agent-based Renaissance Florence simulation.
# Enables agents to produce economic value, engage in trading, pay off debts.
# Made with Mesa 3.2.0.
# Fabian Lohmann, July 2025
# FDLohmann@gmail.com

import mesa

class household(mesa.Agent):

    def __init__(self, model, investments, deductions, trade, bocche):
        super().__init__(model)
        self.investments = investments
        self.deductions = deductions
        self.wealth = investments - deductions
        self.trade = trade
        if self.trade in [21, 22, 23, 24, 25, 26, 27]:          # Check if the agent is in the Arti Maggiori
            self.artimag = True
        else:
            self.artimag = False
        self.bocche = bocche
        self.taxable = 0        # Initiate taxable variable
        self.trades_n = 1       # Initialize number of trades per step variable
        self.trade_size = 100
        self.trade_strategy = self.random.randint(0, 4)     # Determines whether agents favors small or large amounts of trades
        self.production = 0
        self.remaining_production = 0

        # Determine wealth class of agent based on investments
        if self.investments < 29:           # Bottom 24.8%
            self.wealth_class = 0
        elif self.investments < 210:        # 25.0%
            self.wealth_class = 1
        elif self.investments < 893:        # 24.9%
            self.wealth_class = 2                        
        elif self.investments < 2634:       # 15.0%
            self.wealth_class = 3
        elif self.investments < 14299:      # 9.1%
            self.wealth_class = 4         
        else:                               # Top 1.2%
            self.wealth_class = 5

        self.labor_productivity = 40        # florins per person per year
        self.capital_return_rate = 0.06     # 5-8% was typical for pre-industrial economies
        self.partner_class = 1              # Initialize this variable to choose trading partners

    def say_hi(self):       # Test action
        # Prints agent's ID and wealth.
        print(f"I am agent {str(self.unique_id)}, I have {str(self.wealth)} Florins. I am in guild {str(self.trade)}")
 
    def calculate_taxable(self):
        self.taxable = self.wealth - self.bocche * 200    # 200 Florins tax deduction per family member   
        if self.taxable < 0:
            self.taxable = 0
 
    def trading_phase(self):
        # Every agent produces value based on their investments and household members      
        self.production = round((self.bocche * self.labor_productivity + self.investments * self.capital_return_rate) * (1 - self.model.instability))
        self.remaining_production = round(self.production)
        
        # Every agent randomly trades their production in exchange for wealth
        # Based on trade strategy agents can trade 1 to 10 times, favoring higher trade volumes
        if self.trade_strategy == 0:
            self.trades_n = self.random.randint(1, 3)
        elif self.trade_strategy == 1:
            self.trades_n = self.random.randint(3, 7)
        elif self.trade_strategy == 2:
            self.trades_n = self.random.randint(7, 10)
        elif self.trade_strategy == 3:
            self.trades_n = self.random.randint(8, 10)
        elif self.trade_strategy == 4:
            self.trades_n = self.random.randint(1, 10)        
                
        self.trade_size = round(self.production / self.trades_n)
        
        # Find trade partners and trade
        for _ in range(self.trades_n):
            
            # Randomly choose the wealth class of the trading partner based on the size of the trade
            if self.trade_size < 29:
                self.partner_class = self.random.randint(0,6)
                if self.partner_class > 5:  # Gives double chances of trading within the highest class that can afford it
                    self.partner_class = 0
            elif self.trade_size < 210:
                self.partner_class = self.random.randint(1,6)
                if self.partner_class > 5:  # Gives double chances of trading within the highest class that can afford it
                    self.partner_class = 1
            elif self.trade_size < 893:
                self.partner_class = self.random.randint(2,6)
                if self.partner_class > 5:
                    self.partner_class = 2
            elif self.trade_size < 2634:
                self.partner_class = self.random.randint(3,6)
                if self.partner_class > 5:
                    self.partner_class = 3                
            elif self.trade_size < 14299:
                self.partner_class = self.random.randint(4,6)
                if self.partner_class > 5:
                    self.partner_class = 4                
            else:
                self.partner_class = self.random.randint(5,6)
                if self.partner_class > 5:
                    self.partner_class = 5                                  
            
            # Choose a random trading partner in the picked class and trade!
            if self.model.classified_agents[self.partner_class]:    # Check if there are agents in the class
                trading_partner = self.random.choice(self.model.classified_agents[self.partner_class])
                trading_partner.deductions += self.trade_size
                self.investments += self.trade_size
                self.remaining_production -= self.trade_size

        # Put remaining production into personal wealth
        if self.remaining_production > 0:
            self.investments += self.remaining_production
            self.remaining_production = 0

    def recalculation_phase(self):  # Agents are being taxed and have an opportunity to invest
        
        # Chance to pay off a random debt percentage
        if self.investments > self.deductions:
            if self.wealth_class >= 4:        
                if (0.7 * self.investments) < self.deductions:              # Wealthy aim to keep their debts at 70% of their investments
                        self.deductions_percentage = self.random.random() * 0.3 + self.random.random() * 0.1    # 0.1 for random costs
                else:
                    self.deductions_percentage = self.random.random() * 0.1 # Wealthy always have at least some costs
            elif self.wealth_class == 3:
                if (0.3 * self.investments) < self.deductions:              # Middle class aim to keep their debts at 30% of their investments
                        self.deductions_percentage = self.random.random() * 0.3
                else:
                    self.deductions_percentage = self.random.random() * 0.2 #                     
            else:
                self.deductions_percentage = self.random.random()           # The poor always try to escape their debts
            self.deductions_amount = self.deductions * self.deductions_percentage
            self.deductions -= self.deductions_amount
            self.investments -= self.deductions_amount
            
        if self.taxable > 0:
            # Include forced loans
            self.tax = self.taxable * self.model.tax_percentage
            self.deductions += self.tax                         # Add tax to deductions
            #self.model.city_government.revenue += self.tax     # Add tax to the government
        else:
            self.tax = 0
        
        # There is a chance a household can split due to marriage or other circumstances
        # Likelihood calculation is loosely based on household numbers in the catasti
        if self.bocche >= 2:
            split_probability = (self.bocche**2) * 0.00015      # Exponential likelihood increase with family size 
            # if self.wealth_class >= 4:                            # Optional code to let wealthy families create more branches
            #     split_probability *= 1.5        
            if self.random.random() < split_probability:
                new_bocche = self.random.randint(1, (self.bocche // 2))
                new_investments = round((new_bocche / self.bocche) * self.investments)
                new_deductions = round((new_bocche / self.bocche) * self.deductions)
                self.bocche -= new_bocche            
                self.investments -= new_investments
                self.deductions -= new_deductions
                household.create_agents(
                    model=self.model, 
                    n=1,
                    investments = new_investments,
                    deductions = new_deductions,
                    trade = self.trade,
                    bocche = new_bocche,
                    )
            
        self.wealth = self.investments - self.deductions        # Recalculate wealth

        # Put agent in the appropriate wealth class
        if self.investments < 29:        # Bottom 24.8% in original distribution
            self.wealth_class = 0
        elif self.investments < 210:     # 25.0%
            self.wealth_class = 1
        elif self.investments < 893:     # 24.9%
            self.wealth_class = 2                        
        elif self.investments < 2634:    # 15.0%
            self.wealth_class = 3
        elif self.investments < 14299:   # 9.1%
            self.wealth_class = 4         
        else:                            # Top 1.2%
            self.wealth_class = 5
            


### Potential city government agent ###
# class city_government(mesa,Agent):               # The city
#     def __init__(self, treasury):
#         super().__init__(model)
#         self.treasury = treasury
