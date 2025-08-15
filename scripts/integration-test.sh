#!/bin/bash

# Terravision Quick Test Script
# This script runs the complete testing workflow

set -e  # Exit on any error

echo "🚀 Terravision Quick Test Starting..."

# 1. Start services
echo "🔄 Stopping existing services and starting fresh..."
docker compose down -v --remove-orphans 2>/dev/null || true
docker compose up --build -d

# 2. Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
echo "   This may take up to 60 seconds..."

# Wait for backend health check
max_attempts=30
attempt=1
while [ $attempt -le $max_attempts ]; do
    if docker compose ps | grep -q "healthy.*terravision-api"; then
        echo "✅ Backend service is healthy"
        break
    fi
    if [ $attempt -eq $max_attempts ]; then
        echo "❌ Backend service did not become healthy in time"
        echo "📋 Current service status:"
        docker compose ps
        echo "📜 Backend logs:"
        docker compose logs --tail=20 terravision-api
        exit 1
    fi
    echo "   Attempt $attempt/$max_attempts - waiting for backend..."
    sleep 2
    ((attempt++))
done

# Wait a bit more for frontend
sleep 10

# 3. Check service status
echo "🔍 Service status:"
docker compose ps

# 4. Test the write functionality via graph endpoint
echo "📝 Testing graph endpoint (includes write functionality)..."
if curl -X POST http://localhost:3000/api/terravision/graph \
  -H "Content-Type: application/json" \
  -d @examples/terraform-aws-s3.json \
  -o graph-result.txt \
  --silent \
  --max-time 30 \
  --fail; then
    echo "✅ Graph endpoint test successful"
    echo "📄 Response saved to: graph-result.txt"
else
    echo "❌ Graph endpoint test failed"
    echo "📜 Frontend logs:"
    docker compose logs --tail=20 terravision-ui
    echo "📜 Backend logs:"  
    docker compose logs --tail=20 terravision-api
fi

# 5. Test validation
echo "✅ Testing validation endpoint..."
if curl -X POST http://localhost:3000/api/terravision/validate \
  -H "Content-Type: application/json" \
  -d @examples/terraform-aws-s3.json \
  -o validate-result.txt \
  --silent \
  --max-time 30 \
  --fail; then
    echo "✅ Validation endpoint test successful"
    echo "📄 Response saved to: validate-result.txt"
else
    echo "❌ Validation endpoint test failed"
    echo "📜 Recent logs:"
    docker compose logs --tail=20
fi

# 6. Check if diagram output endpoint is accessible
echo "🖼️ Testing diagram output endpoint..."
if curl -I http://localhost:3000/api/terravision/output \
  --silent \
  --max-time 10 \
  --fail > /dev/null; then
    echo "✅ Diagram output endpoint is accessible"
    # Try to download the actual diagram
    if curl -X GET http://localhost:3000/api/terravision/output \
      -o diagram.png \
      --silent \
      --max-time 30 \
      --fail; then
        echo "📄 Diagram downloaded to: diagram.png"
    else
        echo "⚠️  Diagram endpoint accessible but no content available yet"
    fi
else
    echo "❌ Diagram output endpoint test failed"
fi

echo ""
echo "🎉 Testing complete!"
echo ""
echo "📋 Generated files:"
echo "   - graph-result.txt (Graph generation output)"  
echo "   - validate-result.txt (Validation output)"
echo "   - diagram.png (Generated diagram, if available)"
echo ""
echo "🔍 To check logs: docker compose logs -f"
echo "🛑 To stop services: docker compose down -v --remove-orphans"
echo "🌐 Frontend: http://localhost:3000"
echo "🌐 Backend: http://localhost:8001"
