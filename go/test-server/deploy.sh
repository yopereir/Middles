export NAMESPACE="meme-generator"

docker build -t meme-generator-server ./images/meme-generator-server

kubectl delete namespace $NAMESPACE || echo 0
kubectl create namespace $NAMESPACE
kubectl apply -R -f ./stack-files --namespace $NAMESPACE
