PYTHON = python3
SRC_DIR = src
MAIN_FILE = $(SRC_DIR)/compact_trie.py
MAIN = $(SRC_DIR)/main.py

.PHONY: run test clean help

run:
	$(PYTHON) $(MAIN_FILE)

test:
	$(PYTHON) $(MAIN) $(ARGS)

clean:
	find -name "*.pyc" -delete
	find -name "__pycache__" -type d -exec rm -rf {} +