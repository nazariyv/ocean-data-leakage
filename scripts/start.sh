source scripts/catch-errors.sh
# dependencies
source scripts/utils.sh

# starting the dev environment
minikube delete
sleep 5

# minikube start
minikube start --kubernetes-version v1.16.0

echo '💦 CREATING OCEAN-OPERATOR AND OCEAN-COMPUTE NAMESPACES'
kubectl create ns ocean-operator
kubectl create ns ocean-compute
printOcean 33
sleep 5

echo 'CREATING A DEFAULT STORAGECLASS'
kubectl create -f storage-class/ocean-store.yaml
echo 'SWITCHING OFF THE DEFAULT FLAG ON STANDARD STORAGECLASS'
kubectl patch storageclass standard -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"false"}}}'

echo '🐋 DEPLOYING OCEAN-OPERATOR'
kubectl config set-context --current --namespace ocean-operator
kubectl create -f ocean/config-maps/postgres-configmap.yaml
kubectl create -f ocean/operator-service/postgres-storage.yaml
kubectl create -f ocean/operator-service/postgres-deployment.yaml
kubectl create -f ocean/operator-service/postgresql-service.yaml
kubectl apply -f ocean/operator-service/deployment.yaml
kubectl apply -f ocean/operator-service/role_binding.yaml
kubectl apply -f ocean/operator-service/service_account.yaml
printOcean 66
sleep 5

echo '🦈 DEPLOYING OCEAN-COMPUTE'
kubectl config set-context --current --namespace ocean-compute
kubectl create -f ocean/config-maps/postgres-configmap.yaml
kubectl apply -f ocean/operator-engine/sa.yaml
kubectl apply -f ocean/operator-engine/binding.yaml
kubectl apply -f ocean/operator-engine/operator.yaml
kubectl apply -f ocean/operator-engine/computejob-crd.yaml
kubectl apply -f ocean/operator-engine/workflow-crd.yaml
sleep 30
printOcean 90

echo '🐳 EXPOSING OPERATOR-API PORT'
kubectl expose deployment operator-api --namespace=ocean-operator --port=8050
sleep 15
printOcean 100
echo "🐙 FORWARDING LAPTOP'S 8050 PORT REQUESTS TO OPERATOR-API"
# & is used for "parallel" execution
source scripts/finalize.sh & kubectl -n ocean-operator port-forward svc/operator-api 8050

# todo
# take inputs from the user to fill out the yamls with sed
