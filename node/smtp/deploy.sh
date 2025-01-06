export NAMESPACE="node-smtp"
docker build -t $NAMESPACE .
kubectl delete namespace $NAMESPACE || echo 0
kubectl create namespace $NAMESPACE
kubectl apply -R -f ./*.yaml --namespace $NAMESPACE