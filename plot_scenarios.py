#!/usr/bin/env python

from datetime import date

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
    df = pd.read_csv(
        f"scenario_{name}/outputs/position.csv", index_col=[0], parse_dates=True
    )
    df.sort_index()
    data[name] = df

fig = plt.figure()
for name, df in data.items():
    plt.plot(df.index, df.cumulative, label=name)

plt.gca().yaxis.set_major_formatter(formatter)
plt.legend()
plt.xlim(date(2021, 1, 1), date(2024, 1, 1))
fig.autofmt_xdate()
plt.savefig("scenarios.png", dpi=300)
