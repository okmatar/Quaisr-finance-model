#!/usr/bin/env python

import shutil
import subprocess
import random
from datetime import date


import yaml
import numpy as np
import matplotlib.pyplot as plt

# random.seed(30)


def to_rundir(scenario):
    name = scenario["name"]
    return f"scenario_{name}"


def to_yaml(variable, fname):
    with open(fname, "w") as f:
        f.write(yaml.dump(variable))


def write_pilots(run_dir, spec):
    count = spec["count"]
    pilot_list = []

    # method: beta distribution sampling
    samples = np.sort(np.random.beta(a=1, b=6, size=count))
    low_ordinal = spec["start_range"][0].toordinal()
    high_ordinal = spec["start_range"][1].toordinal()

    start_date_range = [
        int(i) for i in low_ordinal + (high_ordinal - low_ordinal) * samples
    ]
    for i in range(count):
        start_date = date.fromordinal(start_date_range[i]).strftime("%Y-%m-%d")

        record = {
            "id": f"pilot-auto-{i}",
            "start_date": start_date,
            "duration_months": spec["duration_months"],
            "value": spec["value"],
            "value_type": "once",
        }
        pilot_list.append(record)

    plt.figure()
    plt.plot(start_date_range, np.zeros_like(start_date_range), "o")
    plt.savefig(f"{run_dir}/outputs/ordinal_range_pilots.png")

    to_yaml(pilot_list, f"{run_dir}/assumptions/pilots.yaml")


def write_subscriptions(run_dir, spec):
    count = spec["count"]
    subscription_list = []

    # method: beta distribution sampling
    samples = np.sort(np.random.beta(a=6, b=1, size=count))
    low_ordinal = spec["start_range"][0].toordinal()
    high_ordinal = spec["start_range"][1].toordinal()

    start_date_range = [
        int(i) for i in low_ordinal + (high_ordinal - low_ordinal) * samples
    ]

    for i in range(count):
        start_date = date.fromordinal(start_date_range[i]).strftime("%Y-%m-%d")

        record = {
            "id": f"subscription-auto-{i}",
            "start_date": start_date,
            "duration_months": spec["duration_months"],
            "value": spec["value"],
            "value_type": "monthly",
        }
        subscription_list.append(record)

    plt.figure()
    plt.plot(start_date_range, np.zeros_like(start_date_range), "o")
    plt.savefig(f"{run_dir}/outputs/ordinal_range_subscriptions.png")

    to_yaml(subscription_list, f"{run_dir}/assumptions/subscriptions.yaml")


# load scenarios
with open("scenarios.yaml") as f:
    scenario_list = yaml.load(f, Loader=yaml.FullLoader)


# template all assumptions
for scenario in scenario_list:
    run_dir = to_rundir(scenario)
    shutil.copytree("template", run_dir)
    write_pilots(run_dir, spec=scenario["pilots"])
    write_subscriptions(run_dir, spec=scenario["subscriptions"])


# run all scenerios
for spec in scenario_list:
    print(spec)
    subprocess.run("./model.py", cwd=to_rundir(spec))
