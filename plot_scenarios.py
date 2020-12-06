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
end = date(2024, 1, 1)

data = {}
for scenario in scenario_list:
    name = scenario["name"]
    df = pd.read_csv(
        f"scenario_{name}/outputs/position.csv", index_col=[0], parse_dates=True
    )
    df.sort_index()
    df = df[(df.index.date > start) & (df.index.date < end)]
    data[name] = df

fig = plt.figure()
for name, df in data.items():
    if name == "medium":
        plt.plot(df.index, df.cumulative, label=name)
    else:
        plt.plot(df.index, df.cumulative, "--", label=name)


# plt.fill_between(
#     data["low"]["cumulative"],
#     data["low"]["cumulative"],
#     data["high"]["cumulative"],
# )

# len(data["low"])
# len(data["high"])


plt.gca().yaxis.set_major_formatter(formatter)

# plt.xlim(date(2021, 1, 1), date(2024, 1, 1))
fig.autofmt_xdate()
plt.savefig("scenarios.png", dpi=300, transparent=True)
plt.savefig("scenarios.pdf", dpi=300)
