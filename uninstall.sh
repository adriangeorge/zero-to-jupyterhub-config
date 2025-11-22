#!/bin/bash

# Uninstall JupyterHub Helm release
RELEASE_NAME="ibd-jupyterhub"
NAMESPACE="ibd"

helm uninstall $RELEASE_NAME --namespace $NAMESPACE

# Optionally delete the namespace (uncomment if needed)
kubectl delete namespace $NAMESPACE 
