#!/bin/bash

# Configuration
RELEASE_NAME="ibd-jupyterhub"
NAMESPACE="ibd"
CHART_VERSION="4.3.1"


helm repo add jupyterhub https://hub.jupyter.org/helm-chart/
helm repo update

# Create namespace if it doesn't exist
echo "Creating namespace: $NAMESPACE"
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Deploy hub configuration modules as ConfigMap
echo "Deploying hub configuration modules..."
NAMESPACE=$NAMESPACE ./deploy_hub_config.sh

# Apply shared datasets PVC
echo "Creating shared datasets PVC..."
kubectl apply -f shared-datasets.yaml -n $NAMESPACE || {
    echo "Warning: Could not create shared-datasets PVC. It may already exist."
}

# Install or upgrade JupyterHub using Helm
echo "Installing/upgrading JupyterHub..."
helm upgrade --cleanup-on-fail \
  --install $RELEASE_NAME jupyterhub/jupyterhub \
  --namespace $NAMESPACE \
  --create-namespace \
  --version=$CHART_VERSION \
  --values config.yaml \
  --timeout 10m \
  --wait

echo ""
echo "Waiting for hub pod to be ready..."
kubectl wait --for=condition=ready pod -l component=hub -n $NAMESPACE --timeout=300s

echo ""
echo "Setting up default users (admin and teachers)..."
HUB_POD=$(kubectl get pods -n $NAMESPACE -l component=hub -o jsonpath='{.items[0].metadata.name}')
if [ -z "$HUB_POD" ]; then
    echo "ERROR: Could not find hub pod!"
    exit 1
fi

echo "Copying setup script to hub pod..."
kubectl cp setup_static_users.py $NAMESPACE/$HUB_POD:/tmp/setup_static_users.py

echo "Running setup script in hub pod..."
kubectl exec -n $NAMESPACE $HUB_POD -- python3 /tmp/setup_static_users.py
