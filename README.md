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

