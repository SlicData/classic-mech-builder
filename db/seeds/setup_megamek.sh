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
    echo "📥 Downloading MegaMek release data..."
    
    # Download the latest stable release instead of git repository
    # This contains the actual mech data files
    MEGAMEK_VERSION="0.49.19"  # Latest stable version
    DOWNLOAD_URL="https://github.com/MegaMek/megamek/releases/download/v${MEGAMEK_VERSION}/megamek-${MEGAMEK_VERSION}.tar.gz"
    
    echo "   Downloading MegaMek ${MEGAMEK_VERSION}..."
    curl -L "$DOWNLOAD_URL" -o "./data/megamek.tar.gz"
    
    echo "   Extracting MegaMek data..."
    cd ./data
    tar -xzf megamek.tar.gz
    mv "megamek-${MEGAMEK_VERSION}" megamek
    rm megamek.tar.gz
    cd ..
    
    echo "✅ MegaMek release downloaded successfully"
fi

# Count MTF files in the release
MTF_COUNT=$(find "$MEGAMEK_DIR" -name "*.mtf" | wc -l | tr -d ' ')
echo "📊 Found $MTF_COUNT .mtf files available for seeding"

if [ "$MTF_COUNT" -eq 0 ]; then
    echo "⚠️  No MTF files found. Checking directory structure..."
    echo "Directory contents:"
    ls -la "$MEGAMEK_DIR/"
    echo ""
    echo "Looking for data directory:"
    find "$MEGAMEK_DIR" -name "*data*" -type d || echo "No data directory found"
    echo ""
    echo "🔧 The release format may have changed. Checking for zip files..."
    find "$MEGAMEK_DIR" -name "*.zip" | head -5
    
    # Check specifically for mechs.zip
    MECHS_ZIP="$MEGAMEK_DIR/data/mechfiles/mechs.zip"
    if [ -f "$MECHS_ZIP" ]; then
        echo "📦 Found mechs.zip - extracting mech data..."
        cd "$MEGAMEK_DIR/data/mechfiles/"
        unzip -o -q mechs.zip  # -o flag overwrites without prompting
        cd - > /dev/null
        
        # Recount MTF files after extraction
        MTF_COUNT=$(find "$MEGAMEK_DIR" -name "*.mtf" | wc -l | tr -d ' ')
        echo "📊 After extraction: Found $MTF_COUNT .mtf files"
    fi
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
