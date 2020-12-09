#!/usr/bin/env python


import datetime
import random

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from util import loader, formatter
from model import MONTHS

plt.style.use("dark_background")

TIMELINE = loader("assumptions/timeline.yaml")
MONTHS = pd.date_range(start=TIMELINE["start"], end=TIMELINE["end"], freq="M")
start, end = MONTHS[0], MONTHS[-1]

revenue = pd.read_csv("./outputs/revenue.csv", index_col=0, parse_dates=True)
costs = pd.read_csv("./outputs/costs.csv", index_col=0, parse_dates=True)
position = pd.read_csv("./outputs/position.csv", index_col=0, parse_dates=True)

# visualisation
fig = plt.figure()
plt.plot(revenue.index, revenue.cumulative, label="revenue")
plt.plot(costs.index, costs.cumulative, label="costs")
plt.gca().yaxis.set_major_formatter(formatter)
plt.legend()
plt.xlim(start, end)
fig.autofmt_xdate()
plt.savefig("outputs/sources.png", dpi=300)
plt.savefig("outputs/sources.pdf")

# %%

fig = plt.figure()
plt.plot(position.index, position.cumulative, label="position")
plt.gca().yaxis.set_major_formatter(formatter)
plt.xlim(MONTHS[0], MONTHS[-1])
plt.legend()
fig.autofmt_xdate()
ax = plt.gca()


def annotate(timestamp, cash_position, content):
    ax.annotate(
        content,
        (mdates.date2num(timestamp), cash_position),
        xytext=(20, random.randrange(10, 40)),
        textcoords="offset points",
        arrowprops=dict(arrowstyle="-|>"),
        fontsize=8,
    )


# annotate raises
for i, row in revenue[revenue.kind == "raise"].iterrows():
    timestamp = row.name
    content = row.kind
    # lookup position at given date
    cash_position = position.loc[timestamp.date()].cumulative
    annotate(timestamp, cash_position, content)

# annotate pilots
for i, row in revenue[revenue.kind == "pilot"].iterrows():
    timestamp = row.name
    content = f"{row.kind}:{row.id}"
    # lookup position at given date
    cash_position = position.loc[timestamp.date()].cumulative
    annotate(timestamp, cash_position, content)

# annotate subscriptions
subscriptions = revenue[revenue.kind == "subscription"].drop_duplicates(
    "id", keep="first"
)
for i, row in subscriptions.iterrows():
    timestamp = row.name
    # content = f"{row.kind}:{row.id}"
    content = f"{row.kind}"
    # lookup position at given date
    cash_position = position.loc[timestamp.date()].cumulative
    annotate(timestamp, cash_position, content)


plt.savefig("outputs/position.png", dpi=300)
plt.savefig("outputs/position.pdf")
