#!/usr/bin/env python


import datetime

import matplotlib.pyplot as plt
import pandas as pd

from util import loader, formatter


plt.style.use("dark_background")


# load all assumptions
PILOTS = pd.DataFrame(loader("assumptions/pilots.yaml"))
SUBSCRIPTIONS = pd.DataFrame(loader("assumptions/subscriptions.yaml"))
RAISES = pd.DataFrame(loader("assumptions/raises.yaml"))
STAFF = pd.DataFrame(loader("assumptions/staff.yaml"))
ROLES = loader("assumptions/roles.yaml")
MONTHS = pd.date_range(start="2021/01/01", periods=36, freq="M")

# summarise all revenue sources
sources = pd.merge(SUBSCRIPTIONS, PILOTS, how="outer")


# gather all subscription revenue
subscription_list = []
for i, row in sources[sources.value_type == "monthly"].iterrows():
    start_date = row["start_date"]
    periods = row["duration_months"]
    value = row["value"]
    id_ = row["id"]

    df = pd.DataFrame(
        {
            "months": pd.date_range(start=start_date, periods=periods, freq="M"),
            "value": value,
            "id": id_,
            "value_type": "monthly",
        }
    )
    subscription_list.append(df)

# concat all subscription revenue
revenue = pd.concat([df.set_index("months") for df in subscription_list], axis=0)

# merge in all pilot revenue and raises
pilot_revenue = sources[sources.value_type == "once"].set_index("start_date")
pilot_revenue.set_index(pd.to_datetime(pilot_revenue.index), inplace=True)

raises = RAISES.set_index("start_date")
revenue = pd.concat([revenue, pilot_revenue[["id", "value"]], raises], axis=0).drop(
    columns=["value_type"]
)

# sort revenue by date
revenue.sort_index(inplace=True)

# determine the cumulative revenue
revenue["cumulative"] = revenue.value.cumsum()

cost_list = []
for month in MONTHS:
    # remove duplicate entries (these indicate a change in a member's attributes)
    active = STAFF.sort_values("start_date").drop_duplicates("id", keep="last")
    active = active[month >= active.start_date]
    for id_, role in zip(active.id, active.role):
        base_cost = ROLES[role]["base"]
        monthly_cost = base_cost / 12
        record = {"month": month, "id": id_, "value": -monthly_cost}
        cost_list.append(record)

costs = pd.DataFrame(cost_list).set_index("month")

# determine the cumulative costs
costs["cumulative"] = costs.value.cumsum()

position = pd.concat([revenue, costs], axis=0).drop(columns=["cumulative"]).sort_index()

position = position.groupby(position.index).sum()
position["cumulative"] = position.value.cumsum()

position.cumulative.plot()


# visualisation
fig = plt.figure()
plt.plot(revenue.index, revenue.cumulative, label="revenue")
plt.plot(costs.index, costs.cumulative, label="costs")
plt.gca().yaxis.set_major_formatter(formatter)
plt.legend()
plt.xlim(MONTHS[0], MONTHS[-1])
fig.autofmt_xdate()
plt.savefig("outputs/sources.png", dpi=300)


fig = plt.figure()
plt.plot(position.index, position.cumulative, label="position")
plt.gca().yaxis.set_major_formatter(formatter)
plt.xlim(MONTHS[0], MONTHS[-1])
plt.legend()
fig.autofmt_xdate()
plt.savefig("outputs/position.png", dpi=300)

# save data
position.to_csv("outputs/position.csv")
revenue.to_csv("outputs/revenue.csv")
costs.to_csv("outputs/costs.csv")
