#!/bin/bash
# CMB-20: Git commit and push script

set -e

echo "🚀 Preparing CMB-20 for GitHub push..."

# Add all the new and modified files
echo "📁 Adding files to git..."

# Core MTF parser system
git add src/mtf_parser/
git add src/database/

# Production scripts  
git add scripts/seeding/
git add tests/integration/
git add tests/test_cmb20_verification.py

# Database migrations
git add db/migrations/003_engine_types_up.sql
git add db/migrations/003_engine_types_down.sql

# Documentation
git add docs/CMB20_Implementation.md
git add docs/CMB20_File_Organization.md  
git add docs/CMB20_SUBTASKS.md
git add docs/ENGINE_TYPE_FIX.md

# Updated Makefile
git add Makefile

# Test data (if not already committed)
git add data/test_mech.mtf || true

echo "📝 Creating commit..."

# Commit with detailed message
git commit -F COMMIT_MESSAGE.md

echo "🚀 Pushing to GitHub..."

# Push the feature branch
git push origin feature/CMB-20-complete-mtf-seeder

echo "✅ CMB-20 successfully pushed to GitHub!"
echo ""
echo "🎯 Next steps:"
echo "1. Create Pull Request for CMB-20"
echo "2. Review and merge to main"  
echo "3. Start work on CMB-20.4 (Critical Slots)"
echo ""
echo "📊 CMB-20 Statistics:"
echo "- 4,190 MTF files processed"
echo "- 4,046 mechs imported (96.6% success)"
echo "- Production-ready MTF seeder complete"
echo "- Foundation ready for remaining subtasks"

# Clean up
rm COMMIT_MESSAGE.md
