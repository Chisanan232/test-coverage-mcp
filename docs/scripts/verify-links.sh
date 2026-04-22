#!/bin/bash

# Verify all documentation links
# This script checks for broken internal links in the documentation

set -e

echo "🔍 Verifying documentation links..."

# Check for broken markdown links
echo "Checking markdown files for broken links..."
find docs/contents -name "*.md" -type f | while read file; do
  # Extract all markdown links
  grep -o '\[.*\](.*\.md)' "$file" | while read link; do
    # Extract the path
    path=$(echo "$link" | sed 's/.*(\(.*\.md\)).*/\1/')

    # Check if the file exists
    if [ ! -f "docs/contents/$path" ]; then
      echo "❌ Broken link in $file: $path"
      exit 1
    fi
  done
done

# Check for broken docusaurus links
echo "Checking docusaurus configuration links..."
if grep -r "to: '.*'" docs/docusaurus.config.ts | grep -v "http" | while read line; do
  path=$(echo "$line" | sed "s/.*to: '\(.*\)'.*/\1/")
  # Basic validation - just check if it looks reasonable
  if [[ ! "$path" =~ ^/[a-z0-9/_-]+$ ]]; then
    echo "⚠️  Potentially invalid path: $path"
  fi
done; then
  :
fi

echo "✅ Documentation links verified successfully!"
