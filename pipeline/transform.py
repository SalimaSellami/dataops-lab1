import pandas as pd


def clean_orders(df):
    df = df.copy()

    df["country"] = df["country"].astype("string").str.strip().str.title()

    df["_flag"] = ""

    df.loc[df["customer_id"].isna(), "_flag"] += "missing_customer_id;"
    df.loc[pd.to_datetime(df["order_date"], errors="coerce").isna(), "_flag"] += "invalid_date;"
    df.loc[df["quantity"] <= 0, "_flag"] += "invalid_quantity;"
    df.loc[~df["unit_price"].between(0.01, 1000), "_flag"] += "invalid_unit_price;"

    duplicate = df.duplicated(subset=["order_id"], keep="first")
    df.loc[duplicate, "_flag"] += "duplicate_order_id;"

    rejected = df[df["_flag"] != ""].copy()
    rejected["reject_reason"] = rejected["_flag"].str.rstrip(";").str.split(";")
    rejected = rejected.explode("reject_reason")

    clean = df[df["_flag"] == ""].copy()

    clean = clean.drop(columns=["_flag"])
    rejected = rejected.drop(columns=["_flag"])

    return clean, rejected


def revenue_by_country(df):
    result = df.copy()
    result["revenue"] = result["quantity"] * result["unit_price"]

    return (
        result.groupby("country", as_index=False)["revenue"]
        .sum()
        .sort_values("country")
    )