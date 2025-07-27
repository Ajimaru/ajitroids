
# Documentation: generate_docs.py

The script `generate_docs.py` generates a modern, responsive HTML documentation page from the `README.md` in the project root. The generated file is saved as `docs/index.html` and can be published directly with GitHub Pages.

## How it works
- Reads the `README.md` from the project root.
- Converts the Markdown content to HTML and embeds it in a responsive layout with header, footer, and container.
- Includes the stylesheet `docs/assets/css/style.css`.
- Adjusts image paths so they work both on GitHub and on the website (`assets/screenshots/`).
- The footer automatically contains a link to the releases of the current GitHub repository.
- The page title is taken from the first heading in the README or defaults to "Page".

## Usage
You can run the script directly:

```bash
python devtools/generate_docs.py
```

The generated `docs/index.html` is optimized for GitHub Pages and reflects all changes from the `README.md`.

## Requirements
- Python 3.8+
- `markdown` package (see `requirements.txt`)

## Notes
- Images must be placed in the `assets/screenshots/` folder to be displayed correctly everywhere.
- The README.md uses the same image paths as the generated website.

# Dokumentation: Devtools – Release-Modul

This directory contains all tools for locally controlled versioning, structured commits, and automatic changelogs.

## Included Files

| File                   | Purpose                                              |
|------------------------|------------------------------------------------------|
| `full-release.sh`    | Complete menu for commit + version + changelog + tag   |
| `version.txt`        | Stores the current version number (e.g. v0.0.1)        |
| `changelog.md`       | Change log grouped by commit types                     |
| `release.log`        | Log of all releases and commits with timestamps        |
| `.vscode/tasks.json` | VSCode task for easy release                           |
| `Makefile`           | Makefile for release command                           |
| `devtools/README.md` | Documentation for the release module                   |
| `devtools/`          | Contains all dev tools for releases                    |

## Usage

- In the terminal: `bash devtools/full-release.sh`
- Or: `make release` (Makefile available)
- Or in Visual Studio Code via Task menu

## Features

- Interactive commit messages following Conventional Commits
- Semantic versioning (patch / minor / major)
- Automatic changelog generation
- Git tagging + optional push
- Logging & task integration

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
