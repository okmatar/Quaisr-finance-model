#!/usr/bin/env python

import logging
import shutil
import subprocess
<<<<<<< HEAD
=======

from datetime import date
from typing import List
>>>>>>> master

from util import write_pilot_set, write_subscription_set, to_rundir, load_scenarios

<<<<<<< HEAD
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
=======
import yaml
import numpy as np
from pydantic import parse_obj_as

from template.schemas import Scenario, PilotSet, SubscriptionSet
>>>>>>> master

# random.seed(30)
scenario_list = load_scenarios("scenarios.yaml")

# template all scenarios
for scenario in scenario_list:
    shutil.copytree("template", to_rundir(scenario))

<<<<<<< HEAD
    # remove the default (template) assumptions
    shutil.rmtree(f"{to_rundir(scenario)}/assumptions")
=======
def to_rundir(scenario):
    return f"scenario_{scenario.name}"


def to_yaml(variable, fname):
    with open(fname, "w") as f:
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
    to_yaml(pilot_list, f"{run_dir}/assumptions/pilots.yaml")


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
    to_yaml(subscription_list, f"{run_dir}/assumptions/subscriptions.yaml")
>>>>>>> master

    # add the top-level common assumptions
    shutil.copytree("assumptions", f"{to_rundir(scenario)}/assumptions")

<<<<<<< HEAD
    # clear pilots and subscriptions
    open(f"{to_rundir(scenario)}/assumptions/pilots.yaml", "w").close()
    open(f"{to_rundir(scenario)}/assumptions/subscriptions.yaml", "w").close()

    for pilot_set in scenario.pilot_sets:
        write_pilot_set(to_rundir(scenario), s=pilot_set)
    for subscription_set in scenario.subscription_sets:
        write_subscription_set(to_rundir(scenario), s=subscription_set)

# run and visualise all scenerios
for scenario in scenario_list:
    logger.info(f"running scenario {scenario.id}")
=======
# load scenarios
with open("scenarios.yaml") as f:
    scenario_list = parse_obj_as(List[Scenario], yaml.load(f, Loader=yaml.FullLoader))

# template all scenarios
for scenario in scenario_list:
    run_dir = to_rundir(scenario)
    shutil.copytree("template", run_dir)
    for pilot_set in scenario.pilot_sets:
        write_pilot_set(run_dir, s=pilot_set)
    for subscription_set in scenario.subscription_sets:
        write_subscription_set(run_dir, s=subscription_set)

# run and visualise all scenerios
for scenario in scenario_list:
    print(scenario)
>>>>>>> master
    subprocess.run("./model.py", cwd=to_rundir(scenario))
    subprocess.run("./plot_model.py", cwd=to_rundir(scenario))
