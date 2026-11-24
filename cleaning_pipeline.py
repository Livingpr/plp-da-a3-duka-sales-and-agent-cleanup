"""Cleaning pipeline for the mobile-money agent network extract."""
import pandas as pd

TYPE_MAP = {"deposit": "Deposit", "withdrawal": "Withdrawal"}


def clean_agent_data(txns, agents):
    """Clean the agent transactions extract and merge it with the agent register.

    Rules applied, in order:
      1. Uniqueness: drop duplicate txn_id rows (keep the first).
      2. Consistency: standardise txn_type to 'Deposit' or 'Withdrawal'.
      3. Validity: convert amount to numeric ('N/A', blanks and text become NaN)
         and txn_date to datetime (fixing '/' separators).
      4. Outliers: flag amounts above the IQR upper fence in is_outlier.
      5. Completeness: flag missing amounts in amount_imputed, then fill them
         with the median amount of the same transaction type.
      6. Merge: left join to the agent register; unknown agents get the county
         'Unknown' and agent_known = False. No rows are dropped.

    Returns (clean_df, log), where log is a list of plain-English sentences.
    """
    log = []
    out = txns.copy()
    n_start = len(out)

    # 1. Uniqueness
    n_exact = int(out.duplicated().sum())
    out = out.drop_duplicates(subset="txn_id", keep="first").copy()
    log.append(f"Uniqueness: removed {n_start - len(out)} duplicate txn_id rows "
               f"({n_exact} were exact copies); {len(out)} rows remain")

    # 2. Consistency of txn_type
    cleaned_type = out["txn_type"].str.strip().str.lower().map(TYPE_MAP)
    n_changed = int((out["txn_type"] != cleaned_type).sum())
    n_unmapped = int(cleaned_type.isna().sum())
    out["txn_type"] = cleaned_type
    log.append(f"Consistency: standardised txn_type on {n_changed} rows "
               f"({n_unmapped} could not be mapped)")

    # 3. Validity and types
    amount_text = out["amount"].astype("string").str.replace(",", "", regex=False)
    out["amount"] = pd.to_numeric(amount_text, errors="coerce").astype("float64")
    n_slash = int(out["txn_date"].astype("string").str.contains("/", regex=False).sum())
    date_text = out["txn_date"].astype("string").str.replace("/", "-", regex=False)
    out["txn_date"] = pd.to_datetime(date_text, format="%Y-%m-%d")
    log.append(f"Validity: converted amount to numeric ({int(out['amount'].isna().sum())} "
               f"missing or invalid) and fixed {n_slash} dates written with '/'")

    # 4. Outliers: IQR fences on the amounts actually recorded
    q1, q3 = out["amount"].quantile([0.25, 0.75])
    upper = q3 + 1.5 * (q3 - q1)
    out["is_outlier"] = out["amount"] > upper
    log.append(f"Outliers: flagged {int(out['is_outlier'].sum())} amounts above "
               f"the upper fence of KES {upper:,.0f} (kept, not deleted)")

    # 5. Completeness: flag first, then impute
    out["amount_imputed"] = out["amount"].isna()
    type_median = out.groupby("txn_type")["amount"].transform("median")
    out["amount"] = out["amount"].fillna(type_median)
    log.append(f"Completeness: imputed {int(out['amount_imputed'].sum())} amounts "
               f"with the median of the same txn_type, and flagged them")

    # 6. Merge with the agent register
    register = agents.copy()
    register["onboarded"] = pd.to_datetime(register["onboarded"])
    n_before = len(out)
    out = out.merge(register[["agent_id", "county", "onboarded"]], on="agent_id",
                    how="left", validate="many_to_one", indicator=True)
    out["agent_known"] = out["_merge"].eq("both")
    out = out.drop(columns="_merge")
    out["county"] = out["county"].fillna("Unknown")
    n_unknown = int((~out["agent_known"]).sum())
    assert len(out) == n_before, "merge changed the row count"
    log.append(f"Merge: {n_before} rows in, {len(out)} rows out; "
               f"{n_unknown} transactions reference unknown agents "
               f"(county set to 'Unknown', rows kept)")

    columns = ["txn_id", "agent_id", "txn_type", "amount", "txn_date",
               "amount_imputed", "is_outlier", "county", "onboarded", "agent_known"]
    out = out[columns].sort_values("txn_id").reset_index(drop=True)
    return out, log
