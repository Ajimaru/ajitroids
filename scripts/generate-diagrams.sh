#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$SCRIPT_DIR/.."
cd "$REPO_ROOT"

OUTPUT_DIR="docs/reference/diagrams"

echo "Generating UML diagrams..."

# Check if pyreverse is installed
if ! command -v pyreverse &> /dev/null; then
    echo "Error: pyreverse not found. Install with: pip install pylint"
    exit 1
fi

# Check if graphviz is installed
if ! command -v dot &> /dev/null; then
    echo "Error: graphviz not found. Install with:"
    echo "  Ubuntu/Debian: sudo apt-get install graphviz"
    echo "  macOS: brew install graphviz"
    exit 1
fi

# Create output directory (relative to repo root)
mkdir -p "$OUTPUT_DIR"

# Change to repo root so pyreverse generates images there
cd "$REPO_ROOT"

# Lösche ggf. alte Diagramme im Output-Verzeichnis
rm -f "$OUTPUT_DIR/classes.png" "$OUTPUT_DIR/classes.svg" "$OUTPUT_DIR/packages.png" "$OUTPUT_DIR/packages.svg"
rm -f classes_Ajitroids.png packages_Ajitroids.png

echo "Running pyreverse in repo root: $REPO_ROOT"
cd "$REPO_ROOT"
# Ensure pyreverse can import the project package
PYTHONPATH="$REPO_ROOT" pyreverse -o png -p Ajitroids modul

# Move generated diagrams from repo root into the output dir
if [ -f "$REPO_ROOT/classes_Ajitroids.png" ]; then
    mv "$REPO_ROOT/classes_Ajitroids.png" "$OUTPUT_DIR/classes.png"
    echo "✓ Class diagram: $OUTPUT_DIR/classes.png"
    if command -v convert &> /dev/null; then
        if convert "$OUTPUT_DIR/classes.png" "$OUTPUT_DIR/classes.svg"; then
            echo "✓ Converted to SVG: $OUTPUT_DIR/classes.svg"
            rm -f "$OUTPUT_DIR/classes.png"
            echo "✓ Removed PNG: $OUTPUT_DIR/classes.png"
        else
            echo "Warning: ImageMagick 'convert' failed for classes.png"
        fi
    else
        echo "Warning: ImageMagick 'convert' not found. SVG not generated."
    fi
else
    echo "Error: classes_Ajitroids.png was not generated."
fi

if [ -f "$REPO_ROOT/packages_Ajitroids.png" ]; then
    mv "$REPO_ROOT/packages_Ajitroids.png" "$OUTPUT_DIR/packages.png"
    echo "✓ Package diagram: $OUTPUT_DIR/packages.png"
    if command -v convert &> /dev/null; then
        if convert "$OUTPUT_DIR/packages.png" "$OUTPUT_DIR/packages.svg"; then
            echo "✓ Converted to SVG: $OUTPUT_DIR/packages.svg"
            rm -f "$OUTPUT_DIR/packages.png"
            echo "✓ Removed PNG: $OUTPUT_DIR/packages.png"
        else
            echo "Warning: ImageMagick 'convert' failed for packages.png"
        fi
    else
        echo "Warning: ImageMagick 'convert' not found. SVG not generated."
    fi
else
    echo "Error: packages_Ajitroids.png was not generated."
fi

echo "Done! Diagrams generated in $OUTPUT_DIR/"
