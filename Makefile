.PHONY: generate build validate test verify clean

generate:
	python data/generate_synthetic_data.py

build: generate
	python duckdb_local_simulator/build_warehouse.py

validate:
	python validation/validate_duckdb_outputs.py

test:
	pytest -q

verify: clean build validate test

clean:
	rm -f data/source/*.csv outputs/*.csv outputs/*.duckdb
	rm -rf .pytest_cache duckdb_local_simulator/__pycache__ tests/__pycache__ validation/__pycache__ data/__pycache__
