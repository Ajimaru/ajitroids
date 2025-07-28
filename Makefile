.PHONY: release preview log clean types help lint test

## Executes the full Release workflow
release:
	$(PWD)/devtools/full-release.sh

## Shows current version and last changelog entries
preview:
	@echo "Version:"
	@cat devtools/version.txt
	@echo ""
	@echo "Last Changelog Entry:"
	@tail -n 15 devtools/changelog.md

## Shows release log with timestamps
log:
	@echo "Release Log:"
	@cat devtools/release.log

## Runs all linters (black, markdownlint, flake8)
lint:
	@echo "Running Python formatter (black)..."
	@black --check modul/ tests/ devtools/ 2>&1 | tee "devtools/black.log"
	@echo "Running Markdown linter (markdownlint)..."
	@markdownlint "**/*.md" 2>&1 | tee "devtools/markdownlint-report/report.log"
	@echo "Running Python linter (flake8)..."
	@flake8 modul/ tests/ devtools/ --format=html --htmldir="devtools/flake8-report"
	@echo "Tests and linters completed successfully."


## Runs all tests with pytest
test:
	@echo "Running tests with pytest..."
	@pytest --cov --cov-report=html:devtools/htmlcov --import-mode=importlib

## Removes temporary files (optional extendable)
clean:
	@echo "Cleaning up devtools directory..."
	@rm -f devtools/*.bak
	@rm -f devtools/*.tmp
	@rm -f devtools/black.log
	@rm -rf devtools/flake8-report
	@rm -rf devtools/htmlcov
	@rm -rf devtools/markdownlint-report
	@echo "Clean complete."

## Shows supported commit types
types:
	@echo "Supported commit types:"
	@echo "  feat      New feature"
	@echo "  fix       Bugfix"
	@echo "  docs      Documentation"
	@echo "  style     Formatting"
	@echo "  refactor  Code Refactoring"
	@echo "  perf      Performance"
	@echo "  test      Tests"
	@echo "  chore     Maintenance"
	@echo "  ci        CI/CD"
	@echo "  build     Build System"
	@echo "  ui        User Interface Changes"
	@echo "  api       API Changes"
	@echo "  parser    Parser Changes"
	@echo "  script    Script Changes"
	@echo "  config    Configuration Changes"
	@echo "  test       Test Changes"
	@echo "  revert    Revert commit"
	@echo "  wip       Work in Progress"
	@echo "  security  Security Fix"
	@echo "  deps      Dependency Update"
	@echo "  release   Release Preparation"
	@echo "  merge     Merge Changes"
	@echo "  subtask   Subtask Implementation"

## Shows all available targets
help:
	@echo "Makefile Help:"
	@echo "  make release   execute full-release.sh"
	@echo "  make ci        Run build tests with act"
	@echo "  make preview   Show version & changelog"
	@echo "  make log       Show release log"
	@echo "  make types     Show commit types"
	@echo "  make lint      Run all linters (black, markdownlint, flake8)"
	@echo "  make test      Run all tests with pytest"
	@echo "  make clean     Remove logs and reports"
	@echo "  make help      Show this help"
