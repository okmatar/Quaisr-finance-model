#!/usr/bin/env python


import datetime
import random
from dateutil.relativedelta import relativedelta

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from util import loader, formatter


plt.style.use("dark_background")

TIMELINE = loader("assumptions/timeline.yaml")
MONTHS = pd.date_range(start=TIMELINE["start"], end=TIMELINE["end"], freq="M")
start, end = MONTHS[0], MONTHS[-1]

revenue = pd.read_csv("./outputs/revenue.csv", index_col=0, parse_dates=True)
costs = pd.read_csv("./outputs/costs.csv", index_col=0, parse_dates=True)
position = pd.read_csv("./outputs/position.csv", index_col=0, parse_dates=True)
burn_rate = pd.read_csv("./outputs/annual_burn_rate.csv", index_col=0, parse_dates=True)
run_rate = pd.read_csv("./outputs/annual_run_rate.csv", index_col=0, parse_dates=True)


def annotate_raises():
    raises = revenue[revenue.kind == "raise"]
    for _, r in raises.iterrows():
        timestamp = pd.Timestamp(r.start_date)
        plt.axvline(timestamp, color="r", linestyle="--")
        plt.gca().annotate(
            r.id,
            (mdates.date2num(timestamp), 1_000_000),
            xytext=(10, random.randrange(10, 20)),
            textcoords="offset points",
            arrowprops=dict(arrowstyle="-|>", linewidth=0.5),
            fontsize=6,
        )


# visualisation
fig = plt.figure()
plt.plot(revenue.index, revenue.cumulative, label="revenue")
plt.plot(costs.index, costs.cumulative, label="costs")
plt.gca().yaxis.set_major_formatter(formatter)
plt.legend()
plt.xlim(start, end)
annotate_raises()
fig.autofmt_xdate()
plt.savefig("outputs/sources.png", dpi=300)
plt.savefig("outputs/sources.pdf")


fig = plt.figure()
plt.plot(burn_rate.index, burn_rate.value, label="annual burn rate")
plt.gca().yaxis.set_major_formatter(formatter)
plt.legend()
plt.xlim(start, end)
annotate_raises()
fig.autofmt_xdate()
plt.savefig("outputs/annual_burn_rate.png", dpi=300)
plt.savefig("outputs/annual_burn_rate.pdf")

fig = plt.figure()
plt.plot(run_rate.index, run_rate.value, label="annual run rate")
plt.gca().yaxis.set_major_formatter(formatter)
plt.legend()
plt.xlim(start, end)
annotate_raises()
fig.autofmt_xdate()
plt.savefig("outputs/annual_run_rate.png", dpi=300)
plt.savefig("outputs/annual_run_rate.pdf")


fig = plt.figure()
plt.plot(position.index, position.cumulative, label="position")
plt.gca().yaxis.set_major_formatter(formatter)
plt.xlim(MONTHS[0] - relativedelta(months=6), MONTHS[-1] + relativedelta(months=2))
plt.legend()
fig.autofmt_xdate()
ax = plt.gca()


def annotate(timestamp, cash_position, content):
    ax.annotate(
        content,
        (mdates.date2num(timestamp), cash_position),
        xytext=(10, random.randrange(10, 20)),
        textcoords="offset points",
        arrowprops=dict(arrowstyle="-|>", linewidth=0.5),
        fontsize=6,
    )


# annotate raises
for i, row in revenue[revenue.kind == "raise"].iterrows():
    timestamp = row.name
    content = row.kind
    # lookup position at given date
    cash_position = position.loc[np.datetime64(timestamp.date())].cumulative
    annotate(timestamp, cash_position, content)

# annotate pilots
for i, row in revenue[revenue.kind == "pilot"].iterrows():
    timestamp = row.name
    # content = f"{row.kind}:{row.id}"
    content = f"p"
    # lookup position at given date
    cash_position = position.loc[np.datetime64(timestamp.date())].cumulative
    annotate(timestamp, cash_position, content)

# annotate subscriptions
subscriptions = revenue[revenue.kind == "subscription"].drop_duplicates(
    "id", keep="first"
)
for i, row in subscriptions.iterrows():
    timestamp = row.name
    # content = f"{row.kind}:{row.id}"
    # content = f"{row.kind}"
    if row.converted_pilot:
        content = f"c"
    else:
        content = f"s"
    # lookup position at given date
    cash_position = position.loc[np.datetime64(timestamp.date())].cumulative
    annotate(timestamp, cash_position, content)


years = mdates.YearLocator()
plt.gca().xaxis.set_major_locator(years)

plt.grid(linestyle="--", linewidth=0.5)
plt.ylim(top=2e6)

annotate_raises()

plt.savefig("outputs/position.png", dpi=300)
plt.savefig("outputs/position.pdf")
