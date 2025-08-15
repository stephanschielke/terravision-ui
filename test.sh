#!/bin/bash

# Convenience script to run integration tests
# This is a simple wrapper around the main integration test script

echo "🧪 Running Terravision Integration Tests..."
echo ""

# Make sure we're in the project root
cd "$(dirname "$0")"

# Run the integration test
./scripts/integration-test.sh

echo ""
echo "📚 For more testing options, see the README.md file"
