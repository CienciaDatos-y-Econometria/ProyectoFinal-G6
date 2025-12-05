import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

# Load the files
fede = pd.read_csv("stores/IPEC_2022_2024_fedesarrollo.csv")
monthly = pd.read_csv("stores/IPEC_monthly_index.csv")
el_tiempo = pd.read_csv("stores/IPEC_monthly_index_el_tiempo.csv")

# Convert year_month to datetime
fede["year_month"] = pd.to_datetime(fede["year_month"])
monthly["year_month"] = pd.to_datetime(monthly["year_month"])
el_tiempo["year_month"] = pd.to_datetime(el_tiempo["year_month"])

# Plot 1
plt.figure(figsize=(12, 6))
plt.plot(fede["year_month"], fede["IPEC"], label="Fedesarrollo IPEC", marker='o', markersize=4, color='green')
plt.plot(monthly["year_month"], monthly["IPEC"], label="Our IPEC", marker='o', markersize=4, color='orange')

plt.xlabel("Date")
plt.ylabel("Index")
plt.title("IPEC Comparison (2022–2024)")
plt.legend()

# Make every month appear on the x-axis
ax = plt.gca()
ax.xaxis.set_major_locator(mdates.MonthLocator())          # tick every month
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))  # format as YYYY-MM

plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig("figures/IPEC_comparison_2022_2024.png")

# Plot 2 - El Tiempo IPEC
plt.clf()
plt.figure(figsize=(12, 6))
plt.plot(fede["year_month"], fede["IPEC"], label="Fedesarrollo IPEC", marker='o', markersize=4, color='green')
plt.plot(el_tiempo["year_month"], el_tiempo["IPEC"], label="El Tiempo IPEC", marker='o', markersize=4, color='blue')

plt.xlabel("Date")
plt.ylabel("Index")
plt.title("IPEC Comparison (2022–2024)")
plt.legend()

# Make every month appear on the x-axis
ax = plt.gca()
ax.xaxis.set_major_locator(mdates.MonthLocator())          # tick every month
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))  # format as YYYY-MM

plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig("figures/IPEC_comparison_el_tiempo_2022_2024.png")

# Plot 3 - Newspaper Shares Stacked Area Chart

colors = {
    "elespectador.com": "#f53b3b",   
    "blogs.elespectador.com": "#ff9999",

    "eltiempo.com": "#003f7f",      
    "blogs.eltiempo.com": "#18b9dd",
    "citytv.eltiempo.com": "#f18f18",

    "larepublica.co": "#7f0000",     

    "noticiasrcn.com": "#45dd3d",    
    "especiales.noticiasrcn.com": "#009e9e",

    "pulzo.com": "#ff66cc",         

    "semana.com": "#cc0000",         
}

def get_color_list(df):
    return [colors.get(col, "#bbbbbb") for col in df.columns]  # fallback = gray


plt.clf()
df = pd.read_csv("stores/newspapers_shares.csv")

df["year_month"] = pd.to_datetime(df["year_month"])
df = df.set_index("year_month")

# Normalize to row shares (percentages)
shares = df.div(df.sum(axis=1), axis=0) * 100

plt.figure(figsize=(14, 7))
plt.stackplot(
    shares.index,
    shares.T,
    labels=shares.columns,
    colors=get_color_list(shares)
)

plt.title("Monthly Newspaper Shares")
plt.ylabel("Share (%)")
plt.xlabel("Month")
plt.xticks(rotation=45)
plt.ylim(0, 100)

plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
plt.tight_layout()

plt.savefig("figures/newspaper_shares_stacked_area.png")


# Plot 4 - Newspaper Shares IPEC Stacked Area Chart
plt.clf()
df = pd.read_csv("stores/newspapers_shares_IPEC_selected.csv")

df["year_month"] = pd.to_datetime(df["year_month"])
df = df.set_index("year_month")

# Normalize to row shares (percentages)
shares = df.div(df.sum(axis=1), axis=0) * 100

plt.figure(figsize=(14, 7))
plt.stackplot(
    shares.index,
    shares.T,
    labels=shares.columns,
    colors=get_color_list(shares)
)

plt.title("Monthly Newspaper Shares (IPEC-selected articles)")
plt.ylabel("Share (%)")
plt.xlabel("Month")
plt.xticks(rotation=45)
plt.ylim(0, 100)

plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
plt.tight_layout()

plt.savefig("figures/newspaper_shares_IPEC_selected_stacked_area.png")

# Plot 5 - Monthly Sector Distribution Stacked Bar Charts
plt.clf()
df = pd.read_csv("stores/IPEC_sector_monthly_counts.csv")

# Convert year_month to datetime
df["year_month"] = pd.to_datetime(df["year_month"])

# Sort by month
df = df.sort_values("year_month")
sector_cols = [c for c in df.columns if c != "year_month"]

# Fedesarrollo Aggregation 

others_components = [
    "Transportation",
    #"Poverty", (NEVER CLASSIFIED)
    #"Communications",
    "Electricity, Gas and Water",
    #"Agriculture",
    "Construction",
    "Education"
]

df["Others"] = df[others_components].sum(axis=1)

main_sectors = [
    "Economic, Social, and Geopolitical Policy",
    "Economic activity",
    "Security",
    "Financial variables",
    "Health",
    "Others"
]

df_main = df[["year_month"] + main_sectors]

# Convert to percentages
df_pct = df_main.copy()
df_pct[main_sectors] = df_main[main_sectors].div(df_main[main_sectors].sum(axis=1), axis=0) * 100

# Monthly 3x12 stacked bars

months = df_pct["year_month"].dt.to_period("M").astype(str).tolist()
values = df_pct[main_sectors].values

fig, axes = plt.subplots(3, 12, figsize=(22, 10), sharey=True)

for i, ax in enumerate(axes.flat):
    if i >= len(months):
        ax.axis("off")
        continue

    month_label = months[i]
    row = df_pct[df_pct["year_month"].dt.to_period("M").astype(str) == month_label][main_sectors].iloc[0]

    bottom = 0
    for sector in main_sectors:
        ax.bar(0, row[sector], bottom=bottom, label=sector)
        bottom += row[sector]

    ax.set_title(month_label, fontsize=9)
    ax.set_xticks([])
    ax.set_xlim(-0.5, 0.5)

# Only one legend outside
handles, labels = axes[0][0].get_legend_handles_labels()
fig.legend(handles, labels, loc="upper center", ncol=3, bbox_to_anchor=(0.5, 1.05))

fig.suptitle("Distribución mensual por sector de noticias de incertidumbre (2022–2024)", fontsize=14)
plt.tight_layout()
plt.savefig("figures/monthly_sector_distribution_stacked_bars.png")

# Plot 6 - Annual Sector Distribution Stacked Bar Chart

df_pct["year"] = df_pct["year_month"].dt.year
df_year = df_pct.groupby("year")[main_sectors].sum()

# Convert to percentages again after aggregation
df_year_pct = df_year.div(df_year.sum(axis=1), axis=0) * 100

plt.figure(figsize=(10, 7))

bottom = np.zeros(len(df_year_pct))

years = df_year_pct.index.astype(str)

for sector in main_sectors:
    plt.bar(years, df_year_pct[sector], bottom=bottom, label=sector)
    bottom += df_year_pct[sector]

# Percentage labels
for i, year in enumerate(years):
    cum = 0
    for sector in main_sectors:
        val = df_year_pct.loc[int(year), sector]
        if val >= 3:  # avoid clutter
            plt.text(i, cum + val/2, f"{val:.1f}%", ha="center", va="center", fontsize=10)
        cum += val

plt.title("Distribución anual por sector de noticias de incertidumbre (2022–2024)")
plt.ylabel("% del total anual de noticias seleccionadas")
plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
plt.tight_layout()
plt.savefig("figures/annual_sector_distribution_stacked_bar.png")