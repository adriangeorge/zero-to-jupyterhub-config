#!/bin/bash
set -e
# Step 1: Create the directory in minikube node
echo "Step 1: Creating directory in minikube node..."
minikube ssh "sudo mkdir -p /mnt/shared-datasets && sudo chmod 777 /mnt/shared-datasets"

# Step 2: Copy datasets to minikube node
echo "Step 2: Copying datasets to minikube node..."
for file in datasets/*.csv datasets/README.md; do
    if [ -f "$file" ]; then
        echo "  Copying $file..."
        minikube cp "$file" /mnt/shared-datasets/$(basename "$file")
    fi
done

# Step 3: Set proper permissions
# watch out for this one as the default is owned by root:root
echo "Step 3: Setting permissions..."
minikube ssh "sudo chmod -R 755 /mnt/shared-datasets && sudo chown -R 1000:100 /mnt/shared-datasets"
