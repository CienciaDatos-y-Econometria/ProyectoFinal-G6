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

df["fecha"] = pd.to_datetime(df["fecha"])
df = df[df["texto"].notna() & (df["texto"] != "")]

def clean_text(text):
    if pd.isna(text):
        return ""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return text

df["clean"] = (df["titulo"].fillna("") + " " + df["texto"].fillna("")).apply(clean_text)

def contains_any(text, keywords):
    return any(kw in text for kw in keywords)

df["has_uncertainty"] = df["clean"].apply(lambda x: contains_any(x, categories["Uncertainty"]))
df["has_economy"] = df["clean"].apply(lambda x: contains_any(x, categories["Economy"]))
df["has_policy"] = df["clean"].apply(lambda x: contains_any(x, categories["Policy"]))

# IPEC criteria
df["selected"] = df["has_uncertainty"] & df["has_economy"] & df["has_policy"]

domains = [
    "https://blogs.elespectador.com",
    "https://blogs.eltiempo.com",
    "https://citytv.eltiempo.com",
    "https://especiales.noticiasrcn.com",
    "https://www.elespectador.com",
    "https://www.eltiempo.com",
    "https://www.larepublica.co",
    "https://www.lasillavacia.com",
    "https://www.noticiasrcn.com",
    "https://www.pulzo.com",
    "https://www.semana.com"
]

df = df[df["url"].str.startswith(tuple(domains), na=False)]

df_selected = df[df["selected"]].copy()

# Newspapers shares for IPEC-selected articles
df_selected["year_month"] = df_selected["fecha"].dt.to_period("M")

df_selected["domain"] = df_selected["url"].str.extract(
    r"https?://(?:www\.)?([^/\s]+)", re.IGNORECASE
)

shares_selected = (
    df_selected.groupby(["year_month", "domain"])
    .size()
    .unstack(fill_value=0)
)

# Save output
shares_selected.reset_index().to_csv(
    "stores/newspapers_shares_IPEC_selected.csv", index=False
)
