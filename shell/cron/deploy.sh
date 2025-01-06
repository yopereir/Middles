export NAMESPACE="shell-cron"
docker build -t $NAMESPACE .
kubectl delete namespace $NAMESPACE || echo 0
kubectl create namespace $NAMESPACE
envsubst < kubernetes-stack.yaml | kubectl apply -R -f - --namespace $NAMESPACE