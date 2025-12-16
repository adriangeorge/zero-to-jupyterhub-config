#!/bin/bash
# Deploy hub configuration modules as ConfigMap

set -e

NAMESPACE="${NAMESPACE:-ibd}"
CONFIGMAP_NAME="hub-config-modules"

echo "=== Deploying Hub Configuration Modules ==="
echo "Namespace: $NAMESPACE"
echo "ConfigMap: $CONFIGMAP_NAME"
echo ""

if ! command -v kubectl &> /dev/null; then
    echo "Error: kubectl is not installed"
    exit 1
fi

# Create namespace if it doesn't exist
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f - > /dev/null 2>&1 || true

# Delete existing ConfigMap if it exists
if kubectl get configmap "$CONFIGMAP_NAME" -n "$NAMESPACE" &> /dev/null; then
    echo "Deleting existing ConfigMap..."
    kubectl delete configmap "$CONFIGMAP_NAME" -n "$NAMESPACE"
fi

# Create new ConfigMap
echo "Creating ConfigMap from hub-config/ directory..."
kubectl create configmap "$CONFIGMAP_NAME" \
    --from-file=hub-config/ \
    -n "$NAMESPACE"

echo ""
echo "✓ ConfigMap created successfully!"
echo ""
echo "Files in ConfigMap:"
kubectl get configmap "$CONFIGMAP_NAME" -n "$NAMESPACE" -o jsonpath='{.data}' | jq -r 'keys[]' | sort 2>/dev/null || kubectl describe configmap "$CONFIGMAP_NAME" -n "$NAMESPACE" | grep -A 20 "Data"


