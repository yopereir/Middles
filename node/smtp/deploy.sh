export NAMESPACE="smtp"
docker build -t smtp .
kubectl delete namespace $NAMESPACE || echo 0
kubectl create namespace $NAMESPACE
kubectl apply -R -f ./*.yaml --namespace $NAMESPACE