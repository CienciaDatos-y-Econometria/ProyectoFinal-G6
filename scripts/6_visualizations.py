import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Load the files
fede = pd.read_csv("stores/IPEC_2022_2024_fedesarrollo.csv")
monthly = pd.read_csv("stores/IPEC_monthly_index.csv")

# Convert year_month to datetime
fede["year_month"] = pd.to_datetime(fede["year_month"])
monthly["year_month"] = pd.to_datetime(monthly["year_month"])

# Plot
plt.figure(figsize=(12, 6))
plt.plot(fede["year_month"], fede["IPEC"], label="Fedesarrollo IPEC", marker='o', markersize=4)
plt.plot(monthly["year_month"], monthly["IPEC"], label="Our IPEC", marker='o', markersize=4)

plt.xlabel("Date")
plt.ylabel("Index")
plt.title("IPEC Comparison (2022–2024)")
plt.legend()

# ---- Make every month appear on the x-axis ----
ax = plt.gca()
ax.xaxis.set_major_locator(mdates.MonthLocator())          # tick every month
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))  # format as YYYY-MM

plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig("figures/IPEC_comparison_2022_2024.png")
