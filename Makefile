# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: ugutierr <ugutierr@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/09/11 15:01:02 by ugutierr          #+#    #+#              #
#    Updated: 2026/09/19 14:30:20 by ugutierr         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

CONFIG ?= config.example.txt

OUTPUT_FILE ?= maze.txt

MYPY_FLAGS = \
	--warn-return-any \
	--warn-unused-ignores \
	--ignore-missing-imports \
	--disallow-untyped-defs \
	--check-untyped-defs

MYPY_EXCLUDE = --exclude '(^|/).venv/'

FLAKE8_FLAGS = --exclude=.venv




install:
	@uv sync
	@echo "Installation complete."

run: install 
	@uv run python3 a_maze_ing.py $(CONFIG)

build:
	@echo "Building project..."
	@uv build --wheel --out-dir .
	@echo "Build complete."




test: install
	@echo "Running test..."
	@uv run pytest tests/

analyze:
	@echo "Analyzing $(OUTPUT_FILE)..."
	@uv run python3 tests/maze_analyzer.py $(OUTPUT_FILE)

debug: install
	@echo "Running a_maze_ing.py...\n"
	@uv run python3 -m pdb a_maze_ing.py $(CONFIG)




flake8:
	@echo "Running flake8..."
	-@uv run flake8 . $(FLAKE8_FLAGS)

lint: install flake8
	@echo "Running mypy..."
	-@uv run mypy . $(MYPY_FLAGS) $(MYPY_EXCLUDE)

lint-strict: install flake8
	@echo "Running mypy..."
	-@uv run mypy . --strict $(MYPY_EXCLUDE)




tree: 
	@tree -a -I '.git|.venv'

clean:
	@echo "Cleaning project..."
	@find . -type d \( -name "__pycache__" \
		-o -name ".mypy_cache" \
		-o -name ".pytest_cache" \) \
  -not -path "./.venv/*" -prune -exec rm -rf {} +
	@rm -f maze.txt




.PHONY: install run build test analyze debug flake8 lint lint-strict clean tree
