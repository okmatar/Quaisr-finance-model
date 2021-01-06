# Scenarios

Financial modelling for pilots and subscription model.

## Getting started

```sh
pip install -r template/requirements.txt
./run_scenarios.py
./plot_scenarios.py
```

If you're running this repeatedly, use:

```
make clean && make run
```

The assumptions are loaded from:

* `scenarios.yaml`: This file is used to create the conditions of each scenario.
* `assumptions/*.yaml`: This file is used to create assumptions that are common to all test scenarios.

:warning: The assumption files in `template/assumptions/*.yaml` should not be edited as they will be overwritten by the higher-level scripts: they exist only so that `template` is a standalone model that can be run in isolation if needed.

## Running the tests

The test scenario can be run using:

```
make clean && make test
```

The test scenario loads assumptions from:

* `scenarios.test.yaml`: This file is used to create the conditions of each test scenario.
* `assumptions_test/*.yaml`: This file is used to create assumptions that are common to all test scenarios.

## Model detail

### Common assumptions

These are assumptions that are common to each scenario. Common assumptions are set by editing the template files in the `assumptions/` folder.

* `assumptions/overheads.yaml`

  These are recurring costs. Each entry will repeat: for example to represent a cost that repeats once per year starting on 2021-04-01 you could add:

  ```yaml
  - id: legal
    start_date: 2021-04-01
    value: 30_000
    value_type: yearly
    kind: overhead
  ```

  Note: `yearly` is currently the only supported value type.

* `assumptions/raises.yaml`

  Used to add in once-off cash injections, for example to add £700k on 2021-03-01 use:

  ```yaml
  - id: seed_1
    kind: raise
    start_date: 2021-03-01
    value: 700_000
    value_type: once
  ```

  Note: `once` is currently the only supported value type.

* `assumptions/roles.yaml`

  Define roles within the company, for example frontend developer, systems developer. Define salaries, overheads and bonus for each role type.

* `assumptions/staff.yaml`

  Set company staff. Each member has a unique id – repeated entries of the same id indicate changes in member attributes. The model will always look for the most recent (in terms of dates) entry and apply that condition to the unique staff member.

* `assumptions/tiers.yaml`

  Set the monthly revenue for each subscription tier: low, medium and high are hard-coded tier names.

* `assumptions/timeline.yaml`

  Set the global start and end date for all scenarios.

### Specific assumptions

These are assumptions that are specific to each scenario.

* `scenarios.yaml`

  Scenarios consist of revenue that comes from pilots and subscriptions. You can create sets of pilots, for example to create two sets of pilots you could use:

  ```yaml
  pilot_sets:
      - id: early
        count: 4
        start_range:
          - 2021-01-01
          - 2021-08-01
        spacing: early
        value: 50_000
        duration_months: 3
        conversion:
          fraction: 0.8
          start_tier: medium
      - id: late
        count: 4
        start_range:
          - 2022-01-01
          - 2023-01-01
        spacing: early
        value: 50_000
        duration_months: 3
        conversion:
          fraction: 0.8
          start_tier: medium
  ```

  Here, we'd have 4 pilots in the first set and another 4 in the second (making a total of 8 pilots). Sets allow us to use time ranges, so for the early set above its 4 pilots will occur between 2021-01-01 and 2021-08-01 with a bias towards placing the pilots early on within that time range. A fraction of the pilots can be automatically converted to subscriptions using the conversion `fraction` assumption.

  Subscriptions can be similarly defined in sets, for example to create two sets of subscriptions, use:

  ```yaml
  subscription_sets:
    - id: from_pilots
      count: 4
      start_range:
        - 2021-01-01
        - 2022-06-01
      spacing: late
      start_tier: medium
      upgrade_period_months: 18
      total_duration_months: 48
    - id: from_sales
      count: 20
      start_range:
        - 2021-01-01
        - 2024-01-01
      spacing: late
      start_tier: low
      upgrade_period_months: 18
      total_duration_months: 48
  ```

  Subscriptions begin at the pricing specified by the `start_tier` field, before increasing to the next highest tier after a period of `upgrade_period_months` months. ⚠️ Not yet implemented!