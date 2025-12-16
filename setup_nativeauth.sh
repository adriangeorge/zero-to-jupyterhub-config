#!/bin/bash
# This script re-creates the default users (admin and teachers)
# Run this if you need to reset passwords or recreate users

set -e

NAMESPACE="ibd"

echo "Setting up default users..."

HUB_POD=$(kubectl get pods -n $NAMESPACE -l component=hub -o jsonpath='{.items[0].metadata.name}')

if [ -z "$HUB_POD" ]; then
    echo "ERROR: Hub pod not found. Make sure JupyterHub is installed."
    echo "Run: ./install.sh first"
    exit 1
fi

echo "Found hub pod: $HUB_POD"
echo "Copying setup script..."
kubectl cp setup_static_users.py $NAMESPACE/$HUB_POD:/tmp/setup_static_users.py

echo "Running setup script..."
kubectl exec -n $NAMESPACE $HUB_POD -- python3 /tmp/setup_static_users.py

echo ""
echo "✓ Users setup complete!"




