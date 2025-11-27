#!/bin/bash
set -euo pipefail

echo "🚀 Starting Surfer H - Native DOM Approach"
echo "=========================================="
echo "This version uses HTML parsing and CSS selectors"
echo "instead of screenshot-based coordinate detection"
echo ""

# Load environment variables using Python helper
eval "$(uv run python load_env.py HAI_API_KEY HAI_MODEL_URL_NAVIGATION HAI_MODEL_NAME_NAVIGATION)"
echo ""

# Task configuration
echo "📄 Loading task from instructions-native.txt"
URL="file:///home/justine/Documents/surfer-h-cli/automation_forms_filling/login.html"

echo "🌐 Target URL: $URL"
echo "🤖 Model: $HAI_MODEL_NAME_NAVIGATION"
echo ""

# Sync dependencies
echo "📦 Syncing dependencies..."
uv sync

# Set up API keys
export API_KEY_NAVIGATION="$HAI_API_KEY"

# Run the native approach
echo ""
echo "🎯 Starting native DOM agent..."
echo ""
uv run python surferh_native.py
