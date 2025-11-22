# Add JupyterHub Helm repository
helm repo add jupyterhub https://hub.jupyter.org/helm-chart/
helm repo update

# Install or upgrade JupyterHub using Helm

RELEASE_NAME="ibd-jupyterhub"
NAMESPACE="ibd"
CHART_VERSION="4.3.1"
helm upgrade --cleanup-on-fail \
  --install $RELEASE_NAME jupyterhub/jupyterhub \
  --namespace $NAMESPACE \
  --create-namespace \
  --version=$CHART_VERSION \
  --values config.yaml
  