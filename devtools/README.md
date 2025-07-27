# Table of Contents

- [Table of Contents](#table-of-contents)
- [Intro](#intro)
  - [Included Files](#included-files)
- [Documentation release-manager.sh](#documentation-release-managersh)
  - [Features](#features)
  - [How it works](#how-it-works)
  - [Usage](#usage)
  - [Requirements](#requirements)
  - [Notes](#notes)
- [Documentation: generate\_docs.py](#documentation-generate_docspy)
  - [Features](#features-1)
  - [How it works](#how-it-works-1)
  - [Usage](#usage-1)
  - [Requirements](#requirements-1)
  - [Notes](#notes-1)
- [Dokumentation: full-release.sh](#dokumentation-full-releasesh)
  - [Markdownlint Integration](#markdownlint-integration)
  - [Black Integration](#black-integration)
  - [flake8 Integration](#flake8-integration)
  - [Pytest, Coverage und htmlcov Integration](#pytest-coverage-und-htmlcov-integration)
  - [Features](#features-2)
  - [How it works](#how-it-works-2)
  - [Usage](#usage-2)
  - [Requirements](#requirements-2)
  - [Notes](#notes-2)
  - [Commit Types according to Conventional Commits](#commit-types-according-to-conventional-commits)
  - [Further Information](#further-information)

# Intro

This directory contains all development and release tools for the project. It provides:

- Automated versioning and changelog management
- Interactive release and commit workflows
- GitHub release and tag management
- Modern documentation generation for GitHub Pages

The tools are designed to support a clean, maintainable, and reproducible release process for projects, including:

- Bash scripts for release automation and GitHub integration
- Python scripts for documentation generation
- Makefile for easy usage
  
The flow of the `full-release.sh` script is visualized in the file [`full-release-sh.html`](./full-release-sh.html). You can open this HTML file to see a step-by-step overview of the release process.

All scripts are documented below and can be used independently or in combination for a streamlined workflow.

## Included Files

| File                        | Purpose                                                 |
|-----------------------------|---------------------------------------------------------|
| `full-release.sh`           | Complete menu for commit + version + changelog + tag    |
| `release-manager.sh`        | Interactive management of releases and tags             |
| `generate_docs.py`          | Generates HTML documentation from project README.md     |
| `version.txt`               | Stores the current version number (e.g. v0.0.1)         |
| `changelog.md`              | Change log grouped by commit types                      |
| `release.log`               | Log of all releases and commits with timestamps         |
| `release-manager.log`       | Log file for release-manager.sh actions and events      |
| `black-log.txt`             | Contains Black formatting check output for Python files |
| `htmlcov/`                  | Directory for Pytest coverage HTML reports              |
| `flake8-report/`            | Directory for Flake8 HTML linting reports               |
| `markdownlint-report`       | Stores results and warnings from Markdownlint checks    |
| `full-release-sh.html`      | Visualizes the release workflow and process steps       |
| `README.md`                 | Documentation for the release module                    |

# Documentation release-manager.sh

`release-manager.sh` is a Bash script for managing GitHub releases and tags in this repository.

## Features

- Lists all releases and tags with metadata (name, author, date, assets)
- Interactive selection and deletion of releases and tags
- Supports dry-run mode for safe preview
- Logs all actions to a logfile (release-manager.log)
- Uses color-coded status messages for clarity
- detects Github User and repository
- Pagination for large tag/release lists
- Menu-driven selection for releases or tags
- Confirmation prompts before deletion
- API error and rate-limit handling
- Customizable log file location

## How it works

- The script uses the GitHub API to list, select, and delete releases and tags interactively.
- You can choose between managing releases or tags in a menu.
- For each item, you can preview and confirm deletion (with dry-run support).
- All actions and warnings are logged to a logfile for traceability.
- The script supports pagination for large lists and color-coded status messages for clarity.

## Usage

- In the terminal: `./devtools/release-manager.sh`

## Requirements

- Bash (POSIX compliant, tested with bash and zsh)
- curl
- jq
- git (for local repo detection)
- Internet connection (for GitHub API)

## Notes

- The script modifies remote tags and releases on GitHub; use dry-run to preview before deleting.
- API rate limits may apply for large operations; check error messages if requests fail.
- Log files are created in the devtools directory and can be customized via options.
- The script is interactive and requires user confirmation for destructive actions.
- For best results, ensure your local repository is up to date with the remote before running.

# Documentation: generate_docs.py

The script `generate_docs.py` generates a modern, responsive HTML documentation page from the `README.md` in the project root. The generated file is saved as `docs/index.html` and can be published directly with GitHub Pages.

## Features

- Converts Markdown to HTML with semantic structure
- Responsive design for desktop and mobile
- Embeds repository release link in the footer
- Customizable CSS via style.css
- Fast, offline execution

## How it works

- Reads the `README.md` from the project root.
- Converts the Markdown content to HTML and embeds it in a responsive layout with header, footer, and container.
- The footer automatically contains a link to the releases of the current GitHub repository.
- The page title is taken from the first heading in the README or defaults to "Page".

## Usage

- In the terminal: `python /devtools/generate_docs.py`

## Requirements

- Python 3.8+
- `markdown` package (see `requirements.txt`)

## Notes

- Images must be placed in the `assets/<your image folder>/` folder to be displayed correctly everywhere.
- The README.md must uses the same image paths as the generated website.
- The script does not require internet access and works completely offline.
- If the stylesheet `docs/assets/css/style.css` is missing, the generated HTML will not be styled.
- The output file `docs/index.html` will be overwritten each time the script runs.
- For best results, keep your project README up to date and use semantic Markdown headings.

# Dokumentation: full-release.sh

`full-release.sh` is the central release and version management script for this project. It streamlines the entire publishing process, ensures consistent versioning, and automates the creation of changelogs and tags. The module is designed for developers who need a reliable and traceable release workflow.

## Markdownlint Integration

The release script checks all Markdown files using `markdownlint`. Results are saved in `devtools/markdownlint-report` (`report.html`). Warnings **do not** abort the release process.

## Black Integration

All Python files in `modul/` and `tests/` are checked with Black in dry-run mode (`--check`). The output and any formatting warnings are saved in `devtools/black-logs.txt`. Warnings **do not** abort the release process.

## flake8 Integration

All Python files in `modul/` and `tests/` are checked with `flake8`. Additionally, an HTML report is generated in `devtools/flake8-report/` (`index.html`). Warnings or errors **do not** abort the release process.

## Pytest, Coverage und htmlcov Integration

The release script runs all tests using `pytest`. Test coverage is measured with the `--cov` option, and an HTML report is generated in the `/devtools/htmlcov` directory at the project root. If any test fails, the release script will **abort** immediately.

## Features

- Interactive commit messages following Conventional Commits
- Semantic versioning (patch / minor / major)
- Automatic changelog generation
- Git tagging + optional push
- Logging & task integration

## How it works

The release module guides you through an interactive workflow for creating commits, updating the version number, generating a changelog, and tagging the release. It enforces semantic versioning and commit message standards (Conventional Commits) to ensure consistency. All actions are logged for traceability. You can run the process via Bash, Makefile, or VSCode tasks. The workflow includes:

- Prompting for commit type and message according to Conventional Commits
- Automatically updating the version number (patch, minor, major)
- Generating and updating the changelog based on commit history
- Creating and optionally pushing a Git tag for the new release
- Logging all release actions for audit and review

## Usage

- In the terminal: `bash devtools/full-release.sh`
- Or: `make release` (Makefile available)
- Or in Visual Studio Code via Task menu

## Requirements

- Bash (POSIX compliant, tested with bash and zsh)
- Python 3.8+ (for documentation generation)
- curl, jq, git (for release scripts)
- Internet connection for GitHub API actions

## Notes

- All tools are designed for reproducible, maintainable releases
- Scripts are modular and can be used independently
- Makefile und VSCode tasks simplify usage for developers
- Ensure your local repository is up to date before running release scripts

## Commit Types according to Conventional Commits

| Type       | Description                                                 |
|------------|-------------------------------------------------------------|
| `feat`     | New feature or enhancement                                  |
| `fix`      | Bug fix                                                     |
| `docs`     | Documentation changes                                       |
| `style`    | Code formatting (no functional changes)                     |
| `refactor` | Code restructuring without changing functionality           |
| `perf`     | Performance optimization                                    |
| `test`     | Tests added or modified                                     |
| `chore`    | Maintenance, build tasks, configuration changes             |
| `ci`       | Changes to CI/CD configurations                             |
| `build`    | Changes to build system or dependencies                     |
| `revert`   | Revert a previous commit                                    |

> Tip: This structure facilitates automatic changelog generation and semantic versioning.

## Further Information

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)