.PHONY: install test e1 e2 e3 e4 e5 e6 e7 e8 e9 all live media docker-build docker-run docker-test

install:
	pip install -r requirements.txt

test:
	PYTHONPATH=. pytest -q

e1:; PYTHONPATH=. python -m src.experiments.e1_effective_capital
e2:; PYTHONPATH=. python -m src.experiments.e2_trailing_trap
e3:; PYTHONPATH=. python -m src.experiments.e3_daily_stop
e4:; PYTHONPATH=. python -m src.experiments.e4_overtrading
e5:; PYTHONPATH=. python -m src.experiments.e5_models_compare
e6:; PYTHONPATH=. python -m src.experiments.e6_risk_sweep
e7:; PYTHONPATH=. python -m src.experiments.e7_consistency
e8:; PYTHONPATH=. python -m src.experiments.e8_live_backtest
e9:; PYTHONPATH=. python -m src.experiments.e9_fee_burn

all:
	PYTHONPATH=. python -m src.experiments.run_all

live: all

media:
	PYTHONPATH=. python -m src.experiments.make_media

docker-build:
	docker compose build

docker-run:
	docker compose run --rm research

docker-test:
	docker compose run --rm test
