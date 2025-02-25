export NAMESPACE="meme-generator"

docker build -t meme-generator-server ./images/meme-generator-server
#docker build -t meme-generator-token-validator ./images/meme-generator-token-validator

kubectl delete namespace $NAMESPACE || echo 0
kubectl create namespace $NAMESPACE
kubectl apply -R -f ./stack-files --namespace $NAMESPACE

# Test
# kubectl port-forward -n $NAMESPACE svc/meme-generator-server-service 8089:8089
# curl -X GET -H "Authorization: Bearer token" "http://localhost:8089/memes?lat=40.73&lon=-73.93&query=food"