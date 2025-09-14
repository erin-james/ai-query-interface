import pandas as pd
from typing import Dict
from difflib import get_close_matches
from .semantic_parser_spacy import parse_question_spacy
import time

def load_data() -> Dict[str, pd.DataFrame]:
    """
    Loads CSV files into pandas DataFrames and returns them as a dictionary.
    Assumes files are located in the 'data/' directory.
    """
    customer_df = pd.read_csv("data/Customers.csv")
    inventory_df = pd.read_csv("data/Inventory.csv")
    detail_df = pd.read_csv("data/Detail.csv")
    pricelist_df = pd.read_csv("data/Pricelist.csv")
    print("Inventory columns:", inventory_df.columns.tolist())

    return {
        "customer": customer_df,
        "inventory": inventory_df,
        "detail": detail_df,
        "pricelist": pricelist_df
    }

def fuzzy_match_name(name: str, customer_df: pd.DataFrame) -> str:
    """
    Attempts to match a customer name to a CID using fuzzy string matching.
    Returns the matched CID or None if no match is found.
    """
    full_names = customer_df["FNAME1"].fillna("") + " " + customer_df["LNAME"].fillna("")
    matches = get_close_matches(name, full_names.tolist(), n=1, cutoff=0.6)
    if matches:
        matched_row = customer_df[full_names == matches[0]]
        return matched_row.iloc[0]["CID"]
    return None

def query_data(question: str, data_store: Dict[str, pd.DataFrame]) -> str:
    """
    Parses a natural language question and returns a formatted response
    based on the parsed intent and the loaded CSV data.
    """
    parsed = parse_question_spacy(question)
    print("Thinking about:", question)
    print("Parsed intent:", parsed)
    intent = parsed["intent"]
    time.sleep(0.5)

    # Unpack data
    customer_df = data_store["customer"]
    inventory_df = data_store["inventory"]
    detail_df = data_store["detail"]
    pricelist_df = data_store["pricelist"]

    # Intent handlers
    if intent == "count_orders":
        total_orders = len(inventory_df["IID"].drop_duplicates())
        return f"There are {total_orders} total orders."

    elif intent == "total_items":
        total_items = pricelist_df["item_id"].nunique()
        return f"There are {total_items} unique items in the pricelist."

    elif intent == "average_price":
        filtered = pricelist_df[pricelist_df["baseprice"] > 0]
        avg_price = filtered["baseprice"].mean()
        return f"The average price of listed items is ${avg_price:.2f}."

    elif intent == "most_expensive_item":
        item = pricelist_df.sort_values("baseprice", ascending=False).iloc[0]
        return f"The most expensive item is:\n{item['name']} — ${item['baseprice']:.2f}"

    elif intent == "cheapest_item":
        item = pricelist_df[pricelist_df["baseprice"] > 0].sort_values("baseprice").iloc[0]
        return f"The cheapest item is:\n{item['name']} — ${item['baseprice']:.2f}"

    elif intent == "out_of_stock_items":
        out_of_stock = pricelist_df[pricelist_df["stock"] == 0]
        if out_of_stock.empty:
            return "All items are currently in stock."
        items = "\n".join(out_of_stock["name"])
        return f"Out of stock items:\n{items}"

    elif intent == "in_stock_items":
        in_stock = pricelist_df[pricelist_df["stock"] > 0]
        if in_stock.empty:
            return "No items are currently in stock."
        items = "\n".join(in_stock["name"])
        return f"In stock items:\n{items}"

    elif intent == "never_ordered_items":
        ordered_ids = detail_df["price_table_item_id"].unique()
        never_ordered = pricelist_df[~pricelist_df["item_id"].isin(ordered_ids)]
        if never_ordered.empty:
            return "All items have been ordered at least once."
        items = "\n".join(never_ordered["name"])
        return f"Items never ordered:\n{items}"

    elif intent == "most_popular_item":
        grouped = detail_df.groupby("price_table_item_id")["item_count"].sum()
        top_id = grouped.idxmax()
        item = pricelist_df[pricelist_df["item_id"] == top_id].iloc[0]
        return f"The most popular item is:\n{item['name']} — {grouped[top_id]} units sold"

    elif intent == "least_popular_item":
        grouped = detail_df.groupby("price_table_item_id")["item_count"].sum()
        bottom_id = grouped.idxmin()
        item = pricelist_df[pricelist_df["item_id"] == bottom_id].iloc[0]
        return f"The least popular item is:\n{item['name']} — {grouped[bottom_id]} units sold"

    elif intent == "top_customer":
        top_cid = inventory_df["CID"].value_counts().idxmax()
        customer = customer_df[customer_df["CID"] == top_cid].iloc[0]
        full_name = f"{customer['FNAME1']} {customer['LNAME']}"
        return f"The top customer is:\n{full_name} — most orders placed"

    elif intent == "bottom_customer":
        bottom_cid = inventory_df["CID"].value_counts().idxmin()
        customer = customer_df[customer_df["CID"] == bottom_cid].iloc[0]
        full_name = f"{customer['FNAME1']} {customer['LNAME']}"
        return f"The customer with the fewest orders is:\n{full_name}"

    elif intent == "item_price":
        item_name = parsed["item_name"]
        matches = pricelist_df[
            pricelist_df["name"].str.contains(item_name, case=False, na=False)
            & (pricelist_df["baseprice"] > 0)
        ]
        if matches.empty:
            return f"No priced item found matching '{item_name}'."
        items = "\n".join(
            f"{row['name']:<25} ${row['baseprice']:>6.2f}"
            for _, row in matches.iterrows()
        )
        return f"Prices for items matching '{item_name}':\n{items}"

    elif intent == "orders_by_customer":
        cid_or_name = parsed["cid"]
        matched_cid = fuzzy_match_name(cid_or_name, customer_df)
        if not matched_cid:
            return f"No customer found matching '{cid_or_name}'."

        orders = inventory_df[inventory_df["CID"] == matched_cid]
        if orders.empty:
            return f"Customer '{cid_or_name}' has no orders."

        details = detail_df[detail_df["IID"].isin(orders["IID"])].drop_duplicates()
        enriched = details.merge(
            pricelist_df,
            left_on="price_table_item_id",
            right_on="item_id",
            how="left"
        )
        summary = enriched.groupby("name")["item_count"].sum().reset_index()
        items = "\n".join(
            f"{row['item_count']}× {row['name']}"
            for _, row in summary.iterrows()
        )
        return f"Customer '{cid_or_name}' ordered:\n{items}"

    elif intent == "price_filter":
        threshold = parsed["threshold"]
        direction = parsed["direction"]

        # Filter and sort items by price, excluding zero-priced entries
        if direction == "above":
            filtered = pricelist_df[
                (pricelist_df["baseprice"] > threshold) & (pricelist_df["baseprice"] > 0)
            ].sort_values("baseprice", ascending=False)
        else:
            filtered = pricelist_df[
                (pricelist_df["baseprice"] < threshold) & (pricelist_df["baseprice"] > 0)
            ].sort_values("baseprice")

        if filtered.empty:
            return f"No items found with price {direction} ${threshold:.2f}."

        # Format output with aligned columns
        header = f"{'Item Name':<30} {'Price':>10}"
        divider = "-" * 42
        rows = "\n".join(
            f"{row['name']:<30} ${row['baseprice']:>9.2f}"
            for _, row in filtered.iterrows()
        )
        return f"Items priced {direction} ${threshold:.2f}:\n\n{header}\n{divider}\n{rows}"

    elif intent == "filter_by_city":
        city = parsed["city"]
        matches = customer_df[customer_df["CITY"].str.contains(city, case=False, na=False)]
        if matches.empty:
            return f"No customer found matching '{city}'."
        names = "\n".join(
            f"{row['FNAME1']} {row['LNAME']}"
            for _, row in matches.iterrows()
        )
        return f"Customers in {city}:\n{names}"

    # Fallback response
    return "Sorry, I couldn't understand that question."
