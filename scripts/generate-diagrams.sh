#!/usr/bin/env bash
set -e

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

# Create output directory
mkdir -p docs/reference/diagrams

# Generate class diagrams
echo "Generating class diagram..."
pyreverse -o png -p Ajitroids modul/

# Move to docs
if [ -f "classes_Ajitroids.png" ]; then
    mv classes_Ajitroids.png docs/reference/diagrams/classes.png
    echo "✓ Class diagram: docs/reference/diagrams/classes.png"
fi

if [ -f "packages_Ajitroids.png" ]; then
    mv packages_Ajitroids.png docs/reference/diagrams/packages.png
    echo "✓ Package diagram: docs/reference/diagrams/packages.png"
fi

echo "Done! Diagrams generated in docs/reference/diagrams/"
