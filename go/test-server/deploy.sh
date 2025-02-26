export NAMESPACE="meme-generator"

# Build go webserver
docker build -t meme-generator-server ./images/meme-generator-server

# Clear any previous stack
kubectl delete namespace $NAMESPACE || echo 0
# Deploy stack
kubectl create namespace $NAMESPACE
kubectl apply -R -f ./stack-files --namespace $NAMESPACE
