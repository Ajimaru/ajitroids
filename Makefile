.PHONY: release preview log clean types help

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

## Removes temporary files (optional extendable)
clean:
	@echo "🧹 Cleaning up devtools directory..."
	@rm -f devtools/*.bak
	@rm -f devtools/*.tmp
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
	@echo "  revert    Revert commit"

## Shows all available targets
help:
	@echo "Makefile Help:"
	@echo "  make release   full-release.sh n"
	@echo "  make preview   Show version & changelog"
	@echo "  make log       Show release log"
	@echo "  make clean     Remove temporary files"
	@echo "  make types     Show commit types"
	@echo "  make help      Show this help"
