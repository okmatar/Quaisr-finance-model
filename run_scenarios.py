#!/usr/bin/env python

import logging
import shutil
import subprocess

from util import write_pilot_set, write_subscription_set, to_rundir, load_scenarios

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# random.seed(30)
scenario_list = load_scenarios("scenarios.yaml")

# template all scenarios
for scenario in scenario_list:
    shutil.copytree("template", to_rundir(scenario))

    # remove the default (template) assumptions
    shutil.rmtree(f"{to_rundir(scenario)}/assumptions")

    # add the top-level common assumptions
    shutil.copytree("assumptions", f"{to_rundir(scenario)}/assumptions")

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
    subprocess.run("./model.py", cwd=to_rundir(scenario))
    subprocess.run("./plot_model.py", cwd=to_rundir(scenario))
