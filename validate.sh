#!/usr/bin/env bash
# ===================================
# 🛡️ Pre-Deployment Validation Script
# Run this before deploying to Render
# ===================================

set -e  # Exit on error

echo "🛡️ [VALIDATE] Starting pre-deployment validation..."
echo ""

# ===================================
# 1. Check Required Files
# ===================================
echo "📁 [VALIDATE] Checking required files..."

REQUIRED_FILES=(
    "Dockerfile"
    "render.yaml"
    "build.sh"
    "requirements.txt"
    "main.py"
    "config.py"
    "graph.py"
    ".dockerignore"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file exists"
    else
        echo "  ❌ $file is missing!"
        exit 1
    fi
done

echo ""

# ===================================
# 2. Check .env is gitignored
# ===================================
echo "🔒 [VALIDATE] Checking .env is gitignored..."

if grep -q "^\.env$" .gitignore; then
    echo "  ✅ .env is in .gitignore"
else
    echo "  ⚠️  WARNING: .env should be in .gitignore!"
fi

echo ""

# ===================================
# 3. Validate Python Syntax
# ===================================
echo "🐍 [VALIDATE] Validating Python syntax..."

PYTHON_FILES=(
    "main.py"
    "config.py"
    "graph.py"
)

for file in "${PYTHON_FILES[@]}"; do
    if python -m py_compile "$file" 2>/dev/null; then
        echo "  ✅ $file syntax valid"
    else
        echo "  ❌ $file has syntax errors!"
        exit 1
    fi
done

echo ""

# ===================================
# 4. Check Critical Dependencies
# ===================================
echo "📦 [VALIDATE] Checking requirements.txt..."

CRITICAL_DEPS=(
    "fastapi"
    "uvicorn"
    "gunicorn"
    "redis"
    "langgraph"
    "anthropic"
    "google-generativeai"
)

for dep in "${CRITICAL_DEPS[@]}"; do
    if grep -q "$dep" requirements.txt; then
        echo "  ✅ $dep in requirements.txt"
    else
        echo "  ❌ $dep missing from requirements.txt!"
        exit 1
    fi
done

echo ""

# ===================================
# 5. Validate Dockerfile
# ===================================
echo "🐳 [VALIDATE] Checking Dockerfile..."

if grep -q "FROM python:3.11" Dockerfile; then
    echo "  ✅ Using Python 3.11 base image"
else
    echo "  ⚠️  WARNING: Not using Python 3.11 base image"
fi

if grep -q "gunicorn" Dockerfile; then
    echo "  ✅ Gunicorn configured in Dockerfile"
else
    echo "  ❌ Gunicorn not found in Dockerfile!"
    exit 1
fi

echo ""

# ===================================
# 6. Validate render.yaml
# ===================================
echo "📋 [VALIDATE] Checking render.yaml..."

if grep -q "type: web" render.yaml; then
    echo "  ✅ Web service configured"
else
    echo "  ❌ Web service not configured in render.yaml!"
    exit 1
fi

if grep -q "healthCheckPath: /health" render.yaml; then
    echo "  ✅ Health check path configured"
else
    echo "  ⚠️  WARNING: Health check path not configured"
fi

echo ""

# ===================================
# 7. Environment Variable Checklist
# ===================================
echo "🔑 [VALIDATE] Environment variable checklist:"
echo ""
echo "  Before deploying to Render, ensure you have:"
echo "  [ ] API_KEY (strong random string)"
echo "  [ ] REDIS_URL (from Redis Cloud/Upstash/Railway)"
echo "  [ ] GOOGLE_API_KEY"
echo "  [ ] ANTHROPIC_API_KEY"
echo "  [ ] GUVI_CALLBACK_URL"
echo "  [ ] GUVI_API_KEY"
echo ""

# ===================================
# Summary
# ===================================
echo "✅ [VALIDATE] All validation checks passed!"
echo ""
echo "📝 Next steps:"
echo "  1. Set up external Redis (see DEPLOYMENT.md Step 1)"
echo "  2. Create Web Service on Render (see DEPLOYMENT.md Step 2)"
echo "  3. Configure environment variables (see DEPLOYMENT.md Step 3)"
echo "  4. Deploy and verify (see DEPLOYMENT.md Steps 4-5)"
echo ""
echo "📖 Full deployment guide: DEPLOYMENT.md"
echo ""
echo "🚀 Ready for deployment!"
