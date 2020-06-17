source scripts/catch-errors.sh
# dependencies
source scripts/utils.sh

# starting the dev environment
minikube delete
sleep 5

minikube start

echo 'ADDING METRICS-SERVER (TO ESTIMATE DEV RESOURCE REQUIREMENTS)'
minikube addons enable metrics-server  # todo: remove this and the comments in the yaml files about it and instead create a LimitRange object and remove those resource attributes from yaml. that way, if the resource is not defined, it will fallback to the values in LimitRange

echo '💦 CREATING NAMESPACES OCEAN-OPERATOR AND OCEAN-COMPUTE'
kubectl create ns ocean-operator
kubectl create ns ocean-compute
printOcean 33
sleep 5

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
# 1. add sed substitution of aws env variables into operator.yaml
