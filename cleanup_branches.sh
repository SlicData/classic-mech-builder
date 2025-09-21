#!/bin/bash

# Branch cleanup script for classic-mech-builder
echo "🧹 Starting branch cleanup for classic-mech-builder..."

# Make sure we're in the right directory
cd "$(dirname "$0")"

# Make sure we're on main branch
echo "📍 Switching to main branch..."
git checkout main

# Update main from origin
echo "🔄 Updating main branch from origin..."
git fetch origin
git pull origin main

# Show current status
echo "📋 Current branch status:"
git branch -v

echo ""
echo "🔍 Checking which branches are merged into main..."

# Check each branch to see if it's merged
BRANCHES_TO_CHECK=(
    "chore/CMB-9-migration-scripts"
    "feature/CMB-10-seed-mech-data" 
    "feature/CMB-8-list-schema"
)

MERGED_BRANCHES=()
UNMERGED_BRANCHES=()

for branch in "${BRANCHES_TO_CHECK[@]}"; do
    if git branch --merged main | grep -q "$branch"; then
        echo "✅ $branch is merged into main"
        MERGED_BRANCHES+=("$branch")
    else
        echo "⚠️  $branch is NOT merged into main"
        UNMERGED_BRANCHES+=("$branch")
    fi
done

echo ""
if [ ${#MERGED_BRANCHES[@]} -gt 0 ]; then
    echo "🗑️  Ready to delete these merged branches:"
    for branch in "${MERGED_BRANCHES[@]}"; do
        echo "   - $branch"
    done
    
    echo ""
    read -p "Delete these merged branches? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        for branch in "${MERGED_BRANCHES[@]}"; do
            echo "🗑️  Deleting $branch..."
            git branch -d "$branch"
        done
        echo "✅ Merged branches deleted!"
    else
        echo "⏸️  Skipped deleting branches"
    fi
else
    echo "ℹ️  No merged branches found to delete"
fi

if [ ${#UNMERGED_BRANCHES[@]} -gt 0 ]; then
    echo ""
    echo "📝 These branches have unmerged changes:"
    for branch in "${UNMERGED_BRANCHES[@]}"; do
        echo "   - $branch"
        echo "     Last commit: $(git log --oneline -1 $branch)"
    done
    
    echo ""
    echo "⚠️  Review these branches manually before deciding to delete them."
    echo "    You can use: git log main..$branch to see unmerged commits"
    echo "    To force delete: git branch -D $branch"
fi

echo ""
echo "📋 Final branch status:"
git branch -v

echo ""
echo "✨ Branch cleanup complete!"
