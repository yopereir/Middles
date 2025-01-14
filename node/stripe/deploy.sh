export NAMESPACE="stripe"
while test $# -gt 0; do
  case "$1" in
    -i|--ingress)
      echo "Ingress controller will be installed and port-forwarded to 80."
      kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.1.2/deploy/static/provider/cloud/deploy.yaml
      sleep 20
      kubectl delete -A ValidatingWebhookConfiguration ingress-nginx-admission
      sudo kubectl port-forward --namespace=ingress-nginx service/ingress-nginx-controller 80:80
      shift
      ;;
    *)
      break
      ;;
  esac
done

# Set dns resolution
if $(cat /etc/hosts | grep -q mystripeserver.test);then
 sudo sed -i -e "s/.*mystripeserver.test.*/$(echo "127.0.0.1 mystripeserver.test")/" /etc/hosts;
 else 
 echo "127.0.0.1 mystripeserver.test" | sudo tee -a /etc/hosts;
fi

# Build docker contianer
docker build -t $NAMESPACE .

# Deplot to k8s
kubectl delete namespace $NAMESPACE || echo 0 # delete any exising resources
kubectl create namespace $NAMESPACE
kubectl create secret generic stripe-env-file --from-file=.env --namespace $NAMESPACE
kubectl apply -R -f ./*.yaml --namespace $NAMESPACE