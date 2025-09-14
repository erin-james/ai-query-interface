"""
Semantic parser for natural language queries using spaCy and regex.
Maps user questions to structured intents for downstream data querying.
Supports synonym matching, price filters, location filters, customer queries, and fallback logic.
"""

import spacy
import re

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

# Synonym map for intent classification
INTENT_SYNONYMS = {
    "count_orders": ["how many orders", "total orders", "number of orders"],
    "total_revenue": ["total revenue", "how much money", "total sales"],
    "multi_item_customers": ["more than one item", "ordered more than once", "repeat buyers"],
    "total_items": ["total items", "how many items", "number of products"],
    "average_price": ["average price", "mean price", "typical cost"],
    "most_expensive_item": ["most expensive item", "highest price", "costliest item"],
    "cheapest_item": ["cheapest item", "lowest price", "least expensive item"],
    "out_of_stock_items": ["out of stock", "not available", "unavailable", "sold out"],
    "in_stock_items": ["in stock", "available", "currently stocked"],
    "never_ordered_items": ["items never ordered", "products never ordered", "unsold items"],
    "most_popular_item": ["most popular item", "best selling item", "top seller", "top item", "highest selling item", "most sold item"],
    "least_popular_item": ["least popular item", "worst selling item", "least ordered"],
    "top_customer": ["top customer", "customer with highest orders", "top buyer"],
    "bottom_customer": ["bottom customer", "customer with lowest orders", "least active customer"],
    "recent_orders": ["orders in last month", "orders in past month", "recent purchases"],
    "yearly_orders": ["orders in last year", "orders in past year", "annual orders"],
    "weekly_orders": ["orders in last week", "orders in past week", "weekly purchases"],
    "daily_orders": ["orders today", "orders in past day", "orders in last day", "today's orders"],
}

def parse_question_spacy(question: str) -> dict:
    """
    Parses a natural language question and returns a structured intent dictionary.
    Uses synonym matching, regex patterns, and spaCy NLP for fallback parsing.

    Args:
        question (str): The user's natural language query.

    Returns:
        dict: A dictionary containing the parsed intent and any relevant parameters.
    """
    q = question.lower().strip()

    # Synonym-based intent matching
    for intent, phrases in INTENT_SYNONYMS.items():
        if any(phrase in q for phrase in phrases):
            return {"intent": intent}

    # Location-based queries (e.g., "customers in Raleigh")
    match = re.search(r"(?:customers|orders) (?:in|from) ([a-z\s]+)", q)
    if match:
        return {"intent": "filter_by_city", "city": match.group(1).strip()}

    # Price filters (e.g., "items over $50")
    match = re.search(r"(?:items|products|things|orders).*?(?:over|above|greater than)\s*\$?(\d+)", q)
    if match:
        return {"intent": "price_filter", "threshold": float(match.group(1)), "direction": "above"}
    match = re.search(r"(?:items|products|things|orders).*?(?:under|below|less than)\s*\$?(\d+)", q)
    if match:
        return {"intent": "price_filter", "threshold": float(match.group(1)), "direction": "below"}

    # Fuzzy product matching (e.g., "orders with something like Widget")
    match = re.search(r"(?:orders|purchases).*?(?:like|similar to|containing|with) (.+)", q)
    if match:
        return {"intent": "fuzzy_product_match", "product_hint": match.group(1).strip()}

    # Customer-specific queries (e.g., "what did John Smith order")
    match = re.search(r"(?:what did|what has|show me what) (.+?) (?:order|buy|purchase)", q)
    if match:
        return {"intent": "customer_orders", "customer_name": match.group(1)}

    # Meta queries
    if "columns" in q or "schema" in q:
        return {"intent": "table_schema"}
    if "how many rows" in q or "row count" in q:
        return {"intent": "row_count"}

    # spaCy-based fallback parsing
    doc = nlp(q)

    # Count orders fallback
    if "order" in q and any(tok.lemma_ == "count" for tok in doc):
        return {"intent": "count_orders"}

    # Average price fallback
    if "price" in q and any(tok.lemma_ in ["average", "mean"] for tok in doc):
        return {"intent": "average_price"}

    # Named entity fallback (e.g., person or organization)
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG"]:
            return {"intent": "orders_by_customer", "cid": ent.text}

    # Item price fallback (e.g., "what's the price of Widget")
    for token in doc:
        if token.text in ["price", "cost"]:
            for chunk in doc.noun_chunks:
                if chunk.root.dep_ in ["attr", "dobj", "pobj"]:
                    return {"intent": "item_price", "item_name": chunk.text.strip()}

    # Fallback if no intent matched
    return {"intent": "unknown"}
