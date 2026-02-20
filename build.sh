#!/usr/bin/env bash
# ===================================
# 🛡️ Render Build Script
# Agentic Honey-Pot API
# ===================================

set -o errexit  # Exit on error
set -o nounset  # Exit on undefined variable
set -o pipefail # Exit on pipe failure

echo "🛡️ [BUILD] Starting Agentic Honey-Pot API build..."

# Install Python dependencies
echo "📦 [BUILD] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Verify critical dependencies
echo "✅ [BUILD] Verifying installations..."
python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"
python -c "import redis; print(f'Redis: {redis.__version__}')"
python -c "import langgraph; print(f'LangGraph: {langgraph.__version__}')"

# Check if required environment variables are set
echo "🔍 [BUILD] Checking environment variables..."
if [ -z "${API_KEY:-}" ]; then
    echo "⚠️ [BUILD] WARNING: API_KEY not set!"
fi

if [ -z "${REDIS_URL:-}" ]; then
    echo "⚠️ [BUILD] WARNING: REDIS_URL not set!"
fi

if [ -z "${GOOGLE_API_KEY:-}" ]; then
    echo "⚠️ [BUILD] WARNING: GOOGLE_API_KEY not set!"
fi

if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
    echo "⚠️ [BUILD] WARNING: ANTHROPIC_API_KEY not set!"
fi

echo "✅ [BUILD] Build completed successfully!"
echo "🚀 [BUILD] Ready for deployment!"
