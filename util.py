from datetime import date
from typing import List


import yaml
import numpy as np
from pydantic import parse_obj_as

from template.schemas import Scenario
from template.schemas import PilotSet, SubscriptionSet


def load_scenarios(fname):
    with open(fname) as f:
        scenario_list = parse_obj_as(
            List[Scenario], yaml.load(f, Loader=yaml.FullLoader)
        )
    return scenario_list


def to_rundir(scenario):
    return f"scenario_{scenario.id}"


def to_yaml(variable, fname, append=True):
    with open(fname, "a" if append else "w") as f:
        f.write(yaml.dump(variable))


def date_range(start_range, spacing="uniform", count=1):

    assert spacing in ["uniform", "early", "late"]

    samples = None
    if spacing == "early":
        #  method: left-weighted beta distribution sampling
        samples = np.sort(np.random.beta(a=1, b=6, size=count))
    elif spacing == "late":
        #  method: right-weighted beta distribution sampling
        samples = np.sort(np.random.beta(a=6, b=1, size=count))
    elif spacing == "uniform":
        #  method: uniform sampling
        samples = np.sort(np.random.uniform(size=count))
    assert samples is not None

    low_ordinal = start_range[0].toordinal()
    high_ordinal = start_range[1].toordinal()
    date_list = [
        date.fromordinal(int(i)).strftime("%Y-%m-%d")
        for i in low_ordinal + (high_ordinal - low_ordinal) * samples
    ]
    return date_list


def write_pilot_set(run_dir, s: PilotSet):
    pilot_list = []
    start_date_range = date_range(s.start_range, spacing=s.spacing, count=s.count)
    for i, start_date in enumerate(start_date_range):
        record = {
            "id": f"pilot-auto-{i}",
            "start_date": start_date,
            "duration_months": s.duration_months,
            "value": s.value,
            "value_type": "once",
            "kind": "pilot",
        }
        pilot_list.append(record)
    to_yaml(pilot_list, f"{run_dir}/assumptions/pilots.yaml", append=True)


def write_subscription_set(run_dir, s: SubscriptionSet):
    subscription_list = []
    start_date_range = date_range(s.start_range, spacing=s.spacing, count=s.count)

    for i, start_date in enumerate(start_date_range):
        record = {
            "id": f"subscription-auto-{i}",
            "start_date": start_date,
            "total_duration_months": s.total_duration_months,
            "start_tier": s.start_tier,
            "value_type": "monthly",
            "kind": "subscription",
        }
        subscription_list.append(record)
    to_yaml(subscription_list, f"{run_dir}/assumptions/subscriptions.yaml", append=True)
