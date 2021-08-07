
# Version 0.1.2

.DEFAULT_GOAL := full
.PHONY: full
full: init test

init:
	pipenv install && pipenv install -e . && pipenv install --dev

test:
	# pipenv install --dev && pipenv run pytest
	pipenv run pytest tests/unit

watch:
	pipenv run watchmedo shell-command --wait --drop --recursive --patterns="*.py;*.yml;bin/mustacheyou" --command='make test && sleep 30' || e=$$?

.PHONY: init test watch
