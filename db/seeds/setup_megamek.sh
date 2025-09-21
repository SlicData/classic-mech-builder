#!/usr/bin/env bash
set -euo pipefail

echo "🤖 Setting up MegaMek data for Classic Mech Builder"

MEGAMEK_DIR="./data/megamek"

# Create data directory if it doesn't exist
mkdir -p ./data

# Check if MegaMek data already exists
if [ -d "$MEGAMEK_DIR" ]; then
    echo "📁 MegaMek data directory already exists"
    echo "   To update: rm -rf $MEGAMEK_DIR && ./db/seeds/setup_megamek.sh"
else
    echo "📥 Downloading MegaMek repository..."
    
    # Clone the full repository first
    git clone --depth 1 https://github.com/MegaMek/megamek.git "$MEGAMEK_DIR"
    
    echo "✅ MegaMek repository downloaded successfully"
fi

# Count MTF files
MTF_COUNT=$(find "$MEGAMEK_DIR" -name "*.mtf" | wc -l | tr -d ' ')
echo "📊 Found $MTF_COUNT .mtf files available for seeding"

if [ "$MTF_COUNT" -eq 0 ]; then
    echo "⚠️  No MTF files found. Checking directory structure..."
    echo "Directory contents:"
    ls -la "$MEGAMEK_DIR/"
    echo ""
    echo "Looking for mechfiles directory:"
    find "$MEGAMEK_DIR" -name "*mechfiles*" -type d || echo "No mechfiles directory found"
    echo ""
    echo "🔧 Try running: rm -rf $MEGAMEK_DIR && ./db/seeds/setup_megamek.sh"
else
    echo ""
    echo "🚀 Setup complete! Next steps:"
    echo "   1. Run migrations: make migrate"
    echo "   2. Test parsing:   make seed-test"
    echo "   3. Seed database:  make seed-megamek"
fi

echo ""
echo "📖 MegaMek data is licensed under GPL v2.0"
echo "   See: https://github.com/MegaMek/megamek/blob/master/LICENSE.md"
