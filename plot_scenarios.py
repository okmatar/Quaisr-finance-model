#!/usr/bin/env python

import yaml
import pandas as pd
import matplotlib.pyplot as plt

from template.util import formatter


plt.style.use("dark_background")

# load scenarios
with open("scenarios.yaml") as f:
    scenario_list = yaml.load(f, Loader=yaml.FullLoader)


data = {}
for scenario in scenario_list:
    name = scenario["name"]
    df = pd.read_csv(f"scenario_{name}/outputs/position.csv")
    data[name] = df

plt.figure()
for name, df in data.items():
    plt.plot(df.index, df.cumulative, label=name)

plt.gca().yaxis.set_major_formatter(formatter)
plt.legend()
plt.savefig("scenarios.png", dpi=300)
