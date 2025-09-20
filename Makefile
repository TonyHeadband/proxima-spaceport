
PYTHON=python

.PHONY: test-ci test-backend

test-ci:
	@echo "Running CI-like tests locally via docker-compose.test.yml"
	@docker-compose -f docker-compose.test.yml build --pull --no-cache
	@docker-compose -f docker-compose.test.yml run --rm backend-test

test-backend:
	@echo "Fallback: run tests using local venv"
	cd backend && $(PYTHON) -m venv .venv || true
	cd backend && . .venv/Scripts/activate >/dev/null 2>&1 || true
	cd backend && $(PYTHON) -m pip install --upgrade pip
	cd backend && $(PYTHON) -m pip install -e .[dev]
	cd backend && pytest -q tests
