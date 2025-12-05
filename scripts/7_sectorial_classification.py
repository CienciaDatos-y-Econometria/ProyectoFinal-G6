import pandas as pd
import unicodedata, re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from nltk.corpus import stopwords

spanish_stopwords = stopwords.words("spanish")

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

print(f"Total articles before filtering: {len(df)}")
df = df[df["texto"].notna() & (df["texto"] != "")]
print(f"Total articles after filtering: {len(df)}")

def clean_text(text):
    if pd.isna(text):
        return ""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return text

df["clean"] = df["titulo"].fillna("") + " " + df["texto"].fillna("")
df["clean"] = df["clean"].apply(clean_text)

def contains_any(text, keywords):
    return any(kw in text for kw in keywords)

df["has_uncertainty"] = df["clean"].apply(lambda x: contains_any(x, categories["Uncertainty"]))
df["has_economy"] = df["clean"].apply(lambda x: contains_any(x, categories["Economy"]))
df["has_policy"] = df["clean"].apply(lambda x: contains_any(x, categories["Policy"]))

df["selected"] = df["has_uncertainty"] & df["has_economy"] & df["has_policy"]

df["year_month"] = df["fecha"].dt.to_period("M")

# Load labeled articles for training (500 labeled articles)
labeled = pd.read_csv("stores/classified_articles.csv")
labeled = labeled[labeled["label"] != "Unclassified"]  # remove invalids

X_train = labeled["article"]
y_train = labeled["label"]

# Train TF-IDF (spanish)

tfidf = TfidfVectorizer(
    max_features=5000,
    ngram_range=(1,2),
    stop_words=spanish_stopwords
)

X_tfidf = tfidf.fit_transform(X_train)

clf = LinearSVC() # Linear Support Vector Classifier
clf.fit(X_tfidf, y_train) 

uncertainty_df = df[df["selected"]].copy() # Apply sector classifier to uncertainty-selected articles

X_all = tfidf.transform(uncertainty_df["clean"]) 
uncertainty_df["predicted_sector"] = clf.predict(X_all) # Predict sectors

# Monthly counts of uncertainty articles by sector

monthly_sector_counts = (
    uncertainty_df.groupby(["year_month", "predicted_sector"])
    .size()
    .reset_index(name="count")
)

print("\nMonthly sector counts (long format):")
print(monthly_sector_counts.head())

# Pivot format (months × sectors)
monthly_sector_pivot = monthly_sector_counts.pivot_table(
    index="year_month",
    columns="predicted_sector",
    values="count",
    fill_value=0
)

print("\nMonthly sector counts (pivot format):")
print(monthly_sector_pivot.head())

monthly_sector_pivot.to_csv("stores/IPEC_sector_monthly_counts.csv")
