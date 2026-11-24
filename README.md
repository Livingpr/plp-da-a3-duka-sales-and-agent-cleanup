# Duka Sales Exploration and Agent Data Cleanup

**Author:** EUNICE LIVINGPROOF | **Cohort:** 1MILDEVS

## Summary

This repository has two engagements.

1. **Duka Electronics.** The Head of Sales wants answers for the half-year review (January to June 2026). `duka_sales_exploration.ipynb` inspects 1,000 orders, builds derived columns, ranks branches and products, compares weekends with weekdays, finds the best and worst months and exports the Premium online orders from Nairobi and Mombasa. `excel/duka_branch_summary.xlsx` reproduces the branch totals with SUMIFS, adds a region with XLOOKUP and includes a PivotTable whose totals match pandas.
2. **Mobile money agent network.** The legacy transaction extract contains deliberately injected problems. `cleaning_pipeline.py` holds a reusable `clean_agent_data(txns, agents)` function that returns the clean data and a log. `agent_cleanup.ipynb` audits the raw data, calls the pipeline, validates the merge, builds a county summary and a weekly pivot table, and ends with a Data Quality Report.

## Agent data: before and after

| | Rows |
|---|---|
| Raw `agent_transactions.csv` | 612 |
| `outputs/agent_transactions_clean.csv` | 600 |
| Duplicate `txn_id` rows removed | 12 |

## How to regenerate the data and run the notebooks

    pip install -r requirements.txt
    python generate_data.py
    jupyter nbconvert --to notebook --execute --inplace duka_sales_exploration.ipynb
    jupyter nbconvert --to notebook --execute --inplace agent_cleanup.ipynb

`generate_data.py` writes `duka_sales.csv`, `agents.csv` and `agent_transactions.csv` (the raw files are not committed). In Google Colab, upload the repository files, run `generate_data.py` first, then run each notebook with Runtime, then Run all.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Livingpr/plp-da-a3-duka-sales-and-agent-cleanup/blob/main/duka_sales_exploration.ipynb)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Livingpr/plp-da-a3-duka-sales-and-agent-cleanup/blob/main/agent_cleanup.ipynb)

## Duka Executive Summary

- Nairobi is the strongest branch, earning KES 26,106,100 (36.4% of the KES 71,792,500 half-year revenue), 1.9 times the revenue of Mombasa.
- Laptop is the top product by revenue at KES 41,535,000 (57.9% of revenue) while ranking number 2 for units sold (639 units), because each one costs KES 65,000.
- Weekend orders average KES 71,972 against KES 71,724 on weekdays (+0.3%), and 27.7% of all 1,000 orders fall on weekends.
- April 2026 was the best month at KES 13,518,300 and June 2026 the weakest at KES 10,903,400, a gap of 24.0%.
- Online orders number 320 (32.0% of orders) with an average of KES 71,207, which is +0.6% against KES 70,759 in store.
