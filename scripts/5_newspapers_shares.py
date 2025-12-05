import pandas as pd
import unicodedata, re

df_2022 = pd.read_csv("stores/noticias_completas_2022.csv", sep='~')
df_2023 = pd.read_csv("stores/noticias_completas_2023.csv", sep='~')
df_2024 = pd.read_csv("stores/noticias_completas_2024.csv", sep='~')
df = pd.concat([df_2022, df_2023, df_2024], ignore_index=True)

src_col = "url"

pattern = re.compile(r"https?://(?:www\.)?[^/\s]+", re.IGNORECASE)
seen = set()
for val in df[src_col].dropna().astype(str):
    m = pattern.search(val)
    if m:
        domain = m.group(0).rstrip("/").lower()
        seen.add(domain)
for d in sorted(seen):
    print(d) # Prints all unique domains found in the URLs

domains = ["https://blogs.elespectador.com",
           "https://blogs.eltiempo.com",
           "https://citytv.eltiempo.com",
           "https://especiales.noticiasrcn.com",
           "https://www.elespectador.com",
           "https://www.eltiempo.com",
           "https://www.larepublica.co",
           "https://www.lasillavacia.com",
           "https://www.noticiasrcn.com",
           "https://www.pulzo.com",
           "https://www.semana.com"]

df_filtered = df[df[src_col].str.startswith(tuple(domains), na=False)]
# Make graph of shares per month for each newspaper
df_filtered["fecha"] = pd.to_datetime(df_filtered["fecha"]) # Date in datetime format
df_filtered["year_month"] = df_filtered["fecha"].dt.to_period("M") # Extract year-month for grouping
shares = df_filtered.groupby(["year_month", df_filtered[src_col].str.extract(r"https?://(?:www\.)?([^/\s]+)", re.IGNORECASE)[0]]).size().unstack(fill_value=0)
shares.reset_index().to_csv("stores/newspapers_shares.csv", index=False)