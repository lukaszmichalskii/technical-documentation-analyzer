VENV=venv
PYTHON=$(VENV)/bin/python3
FILES=$(shell git ls-files '*.py')
MODEL="en_core_web_lg"

build: requirements.txt
	@if [ ! -d $(VENV) ]; then virtualenv -p python3 $(VENV); fi
	@$(PYTHON) -m pip install -r requirements.txt;
	@$(PYTHON) -m spacy download $(MODEL)

format:
	@$(PYTHON) -m black .

run:
	@$(PYTHON) src/main.py

# API_KEY variable needed. Run `export API_KEY=private_key` before
test:
	@$(PYTHON) -m unittest discover tests/

lint:
	@$(PYTHON) -m black --diff --check $(FILES)
	@$(PYTHON) -m pylint --disable=all --enable=unused-import --ignore-patterns=compile.py $(FILES)

clean:
	rm -rf .mypy_cache
