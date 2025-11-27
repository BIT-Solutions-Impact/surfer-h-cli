#!/bin/bash
set -euo pipefail

echo "🚀 Starting Surfer H - Form Filling Task"
echo "=========================================="

# Load environment variables using Python helper
eval "$(uv run python load_env.py HAI_API_KEY HAI_MODEL_URL_NAVIGATION HAI_MODEL_NAME_NAVIGATION HAI_MODEL_URL_LOCALIZATION HAI_MODEL_NAME_LOCALIZATION)"
echo ""

# Task configuration
# The task is read from the instructions.txt file
TASK=$(cat instructions.txt)
# The URL points to the local login form.
URL="file:///home/justine/Documents/surfer-h-cli/automation_forms_filling/login.html"

echo "🎯 Starting task from instructions.txt"
echo "🌐 Target URL: $URL"
echo "🤖 Model: $HAI_MODEL_NAME_NAVIGATION"
echo "🤖 Model: $HAI_MODEL_NAME_LOCALIZATION"
echo ""

# Sync dependencies
echo "📦 Syncing dependencies..."
uv sync

# Set up API keys for the run
export API_KEY_NAVIGATION="$HAI_API_KEY"
export API_KEY_LOCALIZATION="$HAI_API_KEY"

# Run the surfer-h-cli command
uv run surfer-h-cli \
    --task "$TASK" \
    --url "$URL" \
    --max_n_steps 30 \
    --base_url_localization "$HAI_MODEL_URL_LOCALIZATION" \
    --model_name_localization "$HAI_MODEL_NAME_LOCALIZATION" \
    --temperature_localization 0.7 \
    --base_url_navigation "$HAI_MODEL_URL_NAVIGATION" \
    --model_name_navigation "$HAI_MODEL_NAME_NAVIGATION" \
    --temperature_navigation 0.0