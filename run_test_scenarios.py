#!/usr/bin/env python

import logging
import shutil
import subprocess
import datetime
from dateutil.relativedelta import relativedelta

import pandas as pd

from util import write_pilot_set, write_subscription_set, to_rundir, load_scenarios

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# random.seed(30)
scenario_list = load_scenarios("scenarios.test.yaml")

# template all scenarios
for scenario in scenario_list:
    shutil.copytree("template", to_rundir(scenario))

    # remove the default (template) assumptions
    shutil.rmtree(f"{to_rundir(scenario)}/assumptions")

    # add the top-level common assumptions
    shutil.copytree("assumptions_test", f"{to_rundir(scenario)}/assumptions")

    for pilot_set in scenario.pilot_sets:
        write_pilot_set(to_rundir(scenario), s=pilot_set)
    for subscription_set in scenario.subscription_sets:
        write_subscription_set(to_rundir(scenario), s=subscription_set)

# run and visualise all scenerios
for scenario in scenario_list:
    logger.info(f"running scenario {scenario.id}")
    subprocess.run("./model.py", cwd=to_rundir(scenario))
    subprocess.run("./plot_model.py", cwd=to_rundir(scenario))


TEST_DIR = "scenario_test"

# FIXTURE: extract output information
revenue = pd.read_csv(f"{TEST_DIR}/outputs/revenue.csv", index_col=0, parse_dates=True)

# TEST: check that one of the pilots got created
# extract input information
date_range = scenario_list[0].pilot_sets[0].start_range
# extract output information
start_date = revenue[revenue.id == "pilot-auto-0"].index[0].date()
assert date_range[0] <= start_date
assert start_date <= date_range[1]


# TEST: check that one of the subscriptions got created
# extract input information
date_range = scenario_list[0].subscription_sets[0].start_range
# extract output information
start_date = (
    revenue[revenue.id == "subscription-auto-0"]
    .drop_duplicates("id", keep="first")
    .index[0]
    .date()
)
# we're using pd.date_range(..., freq="M") to model all revenue
# arriving at the end of each month
# here we check whether the pilot revenue came within 1 month of the actual start date
assert date_range[0] <= start_date
assert start_date <= date_range[1] + relativedelta(months=1)
