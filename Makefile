DC ?= docker compose
D-UP ?= ${DC} up -d
D-PS ?= ${DC} ps
D-EXEC-APP ?= ${DC} exec app
PYTEST ?= python3 -m pytest
FLAKE8 ?= flake8 --exit-zero

start-app:
	@if ! ${D-PS} -q app | grep -q "."; then ${DC} -f docker-compose.yml up -d app; fi

rebuild-app:
	${D-UP} --build app

bash: start-app
	${D-EXEC-APP} bash

pytest: start-app
	${D-EXEC-APP} ${PYTEST}

flake8: start-app
	${D-EXEC-APP} ${FLAKE8}
