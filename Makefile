run:
	python run_scenarios.py
	python plot_scenarios.py

test:
	python run_test_scenarios.py

clean:
	rm -rf scenario_*
