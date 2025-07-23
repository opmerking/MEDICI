# MEDICI-1427

**Model for Early Dynamics and Interactions in Commercial Italy**

This repository contains the code for an Agent-Based Model (ABM) of economic behavior in Renaissance Florence. The model simulates economic dynamics at a household-level from 1427 to 1457, drawing on historical datasets from the *Catasto* of 1427 and 1457, along with tax and mortality records, to replicate wealth distribution trends, trade interactions, and demographic shifts over time.

## Project Overview

The simulation:
- Models over 9,000 historical households from the 1427 *Catasto*
- Implements economic production, trading behavior, taxation, and mortality
- Uses historical forced loans and epidemic data to simulate economic instability
- Tracks wealth distribution, inequality (Gini coefficient), and demographic evolution over 30 simulated years

## Structure

- `Run.py` — Main script runner. Runs the simulation with 30 timesteps of a year each, and generate plots.
- `model.py` — Core model class. Incorporates taxes, economic instability, population changes, guides general agent behavior.
- `agent.py` — Defines household agents, enables the production of economic value and trading behavior.
- `data/` — Folder containing the historical datasets:
  - `Catasto_1427.csv`
  - `Catasto_1457.csv`
  - `forcedloans.txt`
  - `mortality.txt`

## Requirements

Install dependencies using pip:

```bash
pip install pandas numpy matplotlib seaborn mesa
```

## Sources

_Online Catasto of 1427_. Version 1.3. Edited by David Herlihy, Christiane Klapisch-Zuber, R. Burr Litchfield and Anthony Molho. [Machine readable data file based on D. Herlihy and C. Klapisch-Zuber, _Census and Property Survey of Florentine Domains in the Province of Tuscany, 1427-1480._] Florentine Renaissance Resources/STG: Brown University, Providence, R.I., 2002. The 1427 Catasto data is publicly available at: http://cds.library.brown.edu/projects/catasto/overview.html

The 1457 Catasto is available at: https://doi.org/10.3886/E192821V1. The 1457 Catasto is licensed with Creative Commons: https://creativecommons.org/licenses/by/4.0/

Mortality data comes from the historical Florentine Dowry Fund: https://doi.org/10.2105/AJPH.75.5.528. A S Morrison, J Kirshner, and A Molho “_Epidemics in Renaissance Florence._”, American Journal of Public Health 75, no. 5 (May 1, 1985): pp. 528-535.

Forced loans data comes from: Anthony Molho, _Florentine Public Finances in the Early Renaissance, 1400–1433_ (Cambridge, MA, 1971), 10, 62, and Elio Conti, _L’imposta diretta a Firenze nel Quattrocento,
1427–1494_ (Rome, 1984), 81, 83.

## Acknowledgments
This project was completed as part of the Research Methods for Artificial Intelligence course at the Open University of the Netherlands. Special thanks to the Brown University Digital Humanities team and to the Sapienza Università di Roma team for making the Catasti data publicly available.
