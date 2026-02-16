#!/bin/bash
echo "Testing if the exec format error is fixed..."

# Build the image
echo "Building backend image..."
docker build -t backend-test ./backend > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "❌ Failed to build image"
    exit 1
fi

echo "✅ Image built successfully"

# Test if uvicorn command works
echo "Testing uvicorn command availability..."
UVICORN_PATH=$(docker run --rm backend-test sh -c "which uvicorn")
if [ -z "$UVICORN_PATH" ]; then
    echo "❌ uvicorn command not found in container"
    exit 1
else
    echo "✅ uvicorn command found at: $UVICORN_PATH"
fi

# Test if we can import uvicorn
echo "Testing uvicorn import..."
IMPORT_SUCCESS=$(docker run --rm backend-test python -c "import uvicorn; print('success')" 2>/dev/null)
if [ "$IMPORT_SUCCESS" != "success" ]; then
    echo "❌ Failed to import uvicorn in container"
    exit 1
else
    echo "✅ uvicorn import successful"
fi

echo "🎉 All tests passed! The exec format error should be fixed."
echo ""
echo "Summary of changes made:"
echo "1. Added platform specification to Dockerfile to ensure architecture compatibility"
echo "2. Fixed PATH environment variable to include proper bin directories"
echo "3. Updated the CMD to use 'sh -c' which is more reliable across architectures"