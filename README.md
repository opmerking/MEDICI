# Florence ABM 1427

**Agent-Based Simulation of Economic Behavior in Renaissance Florence**

This repository contains the code for an agent-based model (ABM) simulating household-level economic dynamics in 15th-century Florence. The simulation draws on historical datasets from the *Catasto* of 1427 and 1457, along with tax and mortality records, to replicate wealth distribution trends, trade interactions, and demographic shifts over time.

## 🔍 Project Overview

The simulation:
- Models over 9,000 historical households from the 1427 *Catasto*
- Implements economic production, trading behavior, taxation, and mortality
- Uses historical forced loans and epidemic data to simulate instability
- Tracks wealth distribution, inequality (Gini coefficient), and demographic evolution over 30 simulated years

## 📂 Structure

- `Run.py` — Main script to execute the simulation and generate plots
- `model.py` — Core model logic and simulation engine
- `agent.py` — Definition of the household agents and their behavior
- `data/` — Folder containing the historical datasets:
  - `Catasto_1427.csv`
  - `Catasto_1457.csv`
  - `forcedloans.txt`
  - `mortality.txt`

## 🛠️ Requirements

Install dependencies using pip:

```bash
pip install pandas numpy matplotlib seaborn mesa
```

---
Note: This readme was written by ChatGPT.
