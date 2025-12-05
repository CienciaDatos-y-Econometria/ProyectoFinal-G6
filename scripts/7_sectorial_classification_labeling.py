from openai import OpenAI
from dotenv import load_dotenv
import os
import pandas as pd
import unicodedata, re
import time

load_dotenv()

client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")

df_2022 = pd.read_csv("stores/noticias_completas_2022.csv", sep='~')
df_2023 = pd.read_csv("stores/noticias_completas_2023.csv", sep='~')
df_2024 = pd.read_csv("stores/noticias_completas_2024.csv", sep='~')
df = pd.concat([df_2022, df_2023, df_2024], ignore_index=True)

df["fecha"] = pd.to_datetime(df["fecha"]) # Date in datetime format

df = df[df["texto"].notna() & (df["texto"] != "")] # Filter out empty texts

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

df_sample = df.sample(n=500, random_state=42)[["clean"]].reset_index(drop=True) # Sample 500 articles for labeling

categories = [
    "Economic activity",
    "Agriculture",
    "Construction",
    "Communications",
    "Education",
    "Electricity, Gas and Water",
    "Security",
    "Poverty",
    "Economic, Social, and Geopolitical Policy",
    "Health",
    "Transportation",
    "Financial variables" # NO TIENE SPORTS NI TOURISM NI CULTURA (CRITICA)
]

categories_str = "; ".join(categories)

# Classification using Deepseek with strict output format

def classify_article(text):
    prompt = f"""
You are a classifier. Classify the following newspaper article into EXACTLY ONE category from the list below.

Allowed categories:
{categories_str}

RULES:
- Output ONLY the category name.
- Do NOT output explanations.
- Do NOT output multiple categories.
- Choose the BEST SINGLE category.

ARTICLE:
{text}
"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,  # deterministic
        max_tokens=20
    )

    label = response.choices[0].message.content.strip()

    # If model outputs something invalid, force correction
    if label not in categories:
        # Re-attempt classification with stricter prompt
        correction_prompt = f"""
The model previously gave an invalid answer.

Classify the following article into EXACTLY one of these categories:
{categories_str}

Output ONLY the category EXACTLY as written above.

ARTICLE:
{text}
"""
        response2 = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": correction_prompt}],
            temperature=0,
            max_tokens=20
        )
        label = response2.choices[0].message.content.strip()

        # Final fallback — if still invalid, assign "Unclassified"
        if label not in categories:
            print(label)
            label = "Unclassified"

    return label

# Run classification on all 500 articles
results = []

for i, row in df_sample.iterrows():
    print(f"Classifying article {i+1} / 500...")
    text = row["clean"]
    label = classify_article(text)
    results.append({"article": text, "label": label})
    time.sleep(1)

# Save results to CSV
df_results = pd.DataFrame(results)
df_results.to_csv("stores/classified_articles.csv", index=False)