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

start = date(2021, 1, 1)
end = date(2026, 1, 1)

data = {}
for scenario in scenario_list:
    id_ = scenario["id"]
    df = pd.read_csv(
        f"scenario_{id_}/outputs/position.csv", index_col=[0], parse_dates=True
    )
    df.sort_index()
    df = df[(df.index.date > start) & (df.index.date < end)]
    data[id_] = df

fig = plt.figure()
for name, df in data.items():
    if name == "medium":
        plt.plot(df.index, df.cumulative, label=name)
    else:
        plt.plot(df.index, df.cumulative, "--", label=name)


plt.hlines(0, xmin=start, xmax=end, colors="red", linestyles="dashed", linewidth=0.5)

plt.gca().yaxis.set_major_formatter(formatter)
plt.legend()
fig.autofmt_xdate()
plt.savefig("scenarios.png", dpi=300)
plt.savefig("scenarios.pdf", dpi=300)
