#!/usr/bin/env python


import matplotlib.pyplot as plt
import pandas as pd

from util import loader


plt.style.use("dark_background")

# load all assumptions
PILOTS = pd.DataFrame(loader("assumptions/pilots.yaml"))
SUBSCRIPTIONS = pd.DataFrame(loader("assumptions/subscriptions.yaml"))
TIERS = loader("assumptions/tiers.yaml")
RAISES = pd.DataFrame(loader("assumptions/raises.yaml"))
STAFF = pd.DataFrame(loader("assumptions/staff.yaml"))
OVERHEADS = pd.DataFrame(loader("assumptions/overheads.yaml"))
ROLES = loader("assumptions/roles.yaml")

TIMELINE = loader("assumptions/timeline.yaml")
MONTHS = pd.date_range(start=TIMELINE["start"], end=TIMELINE["end"], freq="M")


# summarise all revenue sources
sources = pd.merge(SUBSCRIPTIONS, PILOTS, how="outer")


def to_value(tier_name):
    tier = list(filter(lambda x: x["id"] == tier_name, TIERS))
    assert len(tier) == 1
    return tier[0]["value"]


# gather all subscription revenue
subscription_list = []
for i, row in sources[sources.value_type == "monthly"].iterrows():
    start_date = row["start_date"]
    periods = row["total_duration_months"]
    value = row["value"]
    id_ = row["id"]
    kind = row["kind"]
    start_tier = row["start_tier"]

    df = pd.DataFrame(
        {
            "months": pd.date_range(start=start_date, periods=periods, freq="M"),
            "value": to_value(start_tier),
            "id": id_,
            "value_type": "monthly",
            "kind": kind,
        }
    )
    subscription_list.append(df)

# concat all subscription revenue
revenue = pd.concat([df.set_index("months") for df in subscription_list], axis=0)

# merge in all pilot revenue and raises
pilot_revenue = sources[sources.value_type == "once"].set_index("start_date")
pilot_revenue.set_index(pd.to_datetime(pilot_revenue.index), inplace=True)
raises = RAISES.set_index(pd.to_datetime(RAISES.start_date))
revenue = pd.concat(
    [revenue, pilot_revenue[["id", "value", "kind"]], raises], axis=0
).drop(columns=["value_type"])

# sort revenue by date
revenue.sort_index(inplace=True)

# determine the cumulative revenue
revenue["cumulative"] = revenue.value.cumsum()

cost_list = []
for month in MONTHS:
    # keep last entry that satisfies the month cutoff
    active = (
        STAFF[month >= STAFF.start_date]
        .sort_values("start_date")
        .drop_duplicates("id", keep="last")
    )

    for id_, role, fte in zip(active.id, active.role, active.fte):
        overheads = ROLES["overheads"]
        role_dict = ROLES["roles"]
        base_cost = role_dict[role]["base"]
        bonus = role_dict[role]["bonus"]
        monthly_cost = ((1 + overheads) * base_cost * fte + bonus * base_cost) / 12
        record = {"month": month, "id": id_, "value": -monthly_cost, "kind": "salary"}
        cost_list.append(record)

    active_overheads = (
        OVERHEADS[month >= OVERHEADS.start_date]
        .sort_values("start_date")
        .drop_duplicates("id", keep="last")
    )

    for id_, value, kind in zip(
        active_overheads.id, active_overheads.value, active_overheads.kind
    ):
        monthly_cost = value / 12
        record = {"month": month, "id": id_, "value": -monthly_cost, "kind": kind}
        cost_list.append(record)


costs = pd.DataFrame(cost_list).set_index("month")

# determine the cumulative costs
costs["cumulative"] = costs.value.cumsum()

position = pd.concat([revenue, costs], axis=0).drop(columns=["cumulative"]).sort_index()

# save raw data before we do any aggregation
position_raw = position.copy()
position_raw["cumulative"] = position_raw.value.cumsum()
position_raw.to_csv("outputs/position_raw.csv")

position = position.groupby(position.index).sum()
position["cumulative"] = position.value.cumsum()

# save data
position.to_csv("outputs/position.csv")
revenue.to_csv("outputs/revenue.csv")
costs.to_csv("outputs/costs.csv")
