import pandas as pd
import unicodedata, re

df_2022 = pd.read_csv("stores/noticias_completas_2022.csv", sep='~')
df_2023 = pd.read_csv("stores/noticias_completas_2023.csv", sep='~')
df_2024 = pd.read_csv("stores/noticias_completas_2024.csv", sep='~')
df = pd.concat([df_2022, df_2023, df_2024], ignore_index=True)


categories = {
    "Uncertainty": ["incertidumbre", "incierto", "incierta"], 
    "Economy": ["economia", "economico", "economica"],
    "Policy": [
        # Fiscal
        "gobierno", "politica fiscal", "presupuesto", "deficit fiscal",
        "deuda publica", "impuesto", "tributaria", "tributario",
        "ministerio de hacienda", "gasto publico",
        # Monetary
        "politica monetaria", "banco de la republica", "emisor",
        # Trade
        "arancel", "arancelaria", "aranceles", "politica comercial"
    ]
}

df["fecha"] = pd.to_datetime(df["fecha"]) # Date in datetime format

def clean_text(text):
    if pd.isna(text):
        return ""
    # Normalize accents
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    # Lowercase
    text = text.lower()
    # Remove special characters
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return text

df["clean"] = df["titulo"].fillna("") + " " + df["texto"].fillna("") # Combine title and text
df["clean"] = df["clean"].apply(clean_text)

def contains_any(text, keywords):
    return any(kw in text for kw in keywords)

df["has_uncertainty"] = df["clean"].apply(lambda x: contains_any(x, categories["Uncertainty"]))
df["has_economy"] = df["clean"].apply(lambda x: contains_any(x, categories["Economy"]))
df["has_policy"] = df["clean"].apply(lambda x: contains_any(x, categories["Policy"]))

df["selected"] = df["has_uncertainty"] & df["has_economy"] & df["has_policy"] # IPEC criteria

df["year_month"] = df["fecha"].dt.to_period("M") # Extract year-month for grouping

monthly_counts = df.groupby("year_month").agg(
    total_articles=("url", "count"),
    selected_articles=("selected", "sum")
)

monthly_counts["ipec_raw"] = (
    monthly_counts["selected_articles"] / monthly_counts["total_articles"]
)

fede = pd.read_csv("stores/IPEC_2022_2024_fedesarrollo.csv") # Official Fedesarrollo IPEC data


# Compute Fedesarrollo mean and std (scaling parameters)
fede_std = fede["IPEC"].std()
fede_mean = fede["IPEC"].mean()

# Standarize
my_mean = monthly_counts["ipec_raw"].mean()
my_std = monthly_counts["ipec_raw"].std()
monthly_counts["ipec_std"] = (monthly_counts["ipec_raw"] - my_mean) / my_std

# Rescale to Fedesarrollo
monthly_counts["IPEC"] = monthly_counts["ipec_std"] * fede_std + fede_mean

# Final index
ipec = monthly_counts["IPEC"].to_frame()
ipec.reset_index().to_csv("stores/IPEC_monthly_index.csv", index=False)