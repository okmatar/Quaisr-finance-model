#!/usr/bin/env python

import random

import matplotlib.pyplot as plt
import pandas as pd
import pendulum

from util import loader


plt.style.use("dark_background")

# load assumptions for present scenario
PILOTS = pd.DataFrame(loader("assumptions/pilots.yaml"))
SUBSCRIPTIONS = pd.DataFrame(loader("assumptions/subscriptions.yaml"))
TIERS = loader("assumptions/tiers.yaml")
RAISES = pd.DataFrame(loader("assumptions/raises.yaml"))
STAFF = pd.DataFrame(loader("assumptions/staff.yaml"))
OVERHEADS = pd.DataFrame(loader("assumptions/overheads.yaml"))
ROLES = loader("assumptions/roles.yaml")

TIMELINE = loader("assumptions/timeline.yaml")
MONTHS = pd.date_range(start=TIMELINE["start"], end=TIMELINE["end"], freq="M")


assert len(SUBSCRIPTIONS) > 0, "At least one subscription must be set."
assert len(PILOTS) > 0, "At least one pilot must be set."


# summarise all revenue sources
sources = pd.merge(SUBSCRIPTIONS, PILOTS, how="outer")


def to_value(tier_name: str):
    tier = list(filter(lambda x: x["id"] == tier_name, TIERS))
    assert len(tier) == 1
    return tier[0]["value"]


def to_upgrade_after_months(tier_name: str):
    assert tier_name in ["low", "medium"]  # high can't be upgraded
    tier = list(filter(lambda x: x["id"] == tier_name, TIERS))
    assert len(tier) == 1
    return tier[0]["upgrade_after_months"]


def upgrade_tier(tier_name: str):
    assert tier_name in ["low", "medium", "high"]
    if tier_name == "low":
        return "medium"
    if tier_name == "medium":
        return "high"
    if tier_name == "high":
        return "high"


# keep a note of whether revenue is from a converted pilot
# i.e. a pilot that has graduated into a subscription
sources["converted_pilot"] = False

# create new "converted-pilot" subscriptions
subscriptions_from_pilots_list = []
for i, pilot in PILOTS.iterrows():
    id_ = pilot.id
    start_tier_name = pilot.conversion["start_tier"]
    subscription_duration_months = pilot.conversion["subscription_duration_months"]
    acceptance_fraction = pilot.conversion["fraction"]
    start_date = (
        pendulum.parse(pilot.start_date)
        .add(months=pilot.pilot_duration_months)
        .to_date_string()
    )
    record = {
        "id": f"converted-pilot-{id_}",
        "kind": "subscription",
        "start_date": start_date,
        "start_tier": start_tier_name,
        "subscription_duration_months": subscription_duration_months,
        "value_type": "monthly",
        "value": to_value(start_tier_name),
        "tier": start_tier_name,
        "converted_pilot": True,
    }
    # probabilistically add subscription based on pilot.conversion["fraction"]
    if random.random() < acceptance_fraction:
        subscriptions_from_pilots_list.append(record)

subscriptions_from_pilots = pd.DataFrame(subscriptions_from_pilots_list)
sources = sources.append(subscriptions_from_pilots)


# gather all subscription revenue
subscription_list = []

# add existing subscriptions from assumptions
for i, row in sources[sources.value_type == "monthly"].iterrows():
    start_date = row.start_date
    periods = row.subscription_duration_months
    value = row.value
    id_ = row.id
    kind = row.kind
    start_tier = row.start_tier
    converted_pilot = row.converted_pilot

    df = pd.DataFrame(
        {
            "months": pd.date_range(start=start_date, periods=periods, freq="M"),
            "value": to_value(start_tier),
            "id": id_,
            "value_type": "monthly",
            "kind": kind,
            "converted_pilot": converted_pilot,
            "tier": start_tier,
        }
    )
    subscription_list.append(df)

# upgrade tier based on subscription age
first_upgrade = to_upgrade_after_months("low")
second_upgrade = to_upgrade_after_months("medium")

for df in subscription_list:
    df["age"] = (df["months"] - df["months"].iloc[0]).astype("timedelta64[M]")
    # upgrade tier after 12 months
    df.tier = df.tier.map(upgrade_tier).where(df["age"].gt(first_upgrade), df.tier)
    # upgrade tier after 24 months
    df.tier = df.tier.map(upgrade_tier).where(
        df["age"].gt(first_upgrade + second_upgrade), df.tier
    )
    # update values
    df.value = df.tier.apply(to_value)

# concat all subscription revenue
revenue = pd.concat([df.set_index("months") for df in subscription_list], axis=0)


# merge in all pilot revenue and raises
pilot_revenue = sources[sources.value_type == "once"].set_index("start_date")
pilot_revenue.set_index(pd.to_datetime(pilot_revenue.index), inplace=True)
raises = RAISES.set_index(pd.to_datetime(RAISES.start_date))
revenue = pd.concat(
    [revenue, pilot_revenue[["id", "value", "kind", "converted_pilot"]], raises], axis=0
).drop(columns=["value_type"])

# sort revenue by date
revenue.sort_index(inplace=True)

# determine the cumulative revenue
revenue["cumulative"] = revenue.value.cumsum()

# determine the annual run rate
# select all subscription revenue
monthly_recurring_revenue = (
    revenue[revenue.kind == "subscription"]["value"].resample("M").sum()
)
annual_run_rate = 12 * monthly_recurring_revenue
annual_run_rate = annual_run_rate.reindex(MONTHS, fill_value=0)

# determine all costs
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

# determine the annual burn rate
# this is the annualised change in total cash position
monthly_burn_rate = position["value"]
annual_burn_rate = 12 * monthly_burn_rate


# save data
position.to_csv("outputs/position.csv")
revenue.to_csv("outputs/revenue.csv")
costs.to_csv("outputs/costs.csv")
annual_run_rate.to_csv("outputs/annual_run_rate.csv")
annual_burn_rate.to_csv("outputs/annual_burn_rate.csv")

