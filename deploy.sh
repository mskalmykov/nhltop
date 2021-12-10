#!/bin/bash

# Azure deploy:
export TF_VAR_DB_PASSWORD=${TF_VAR_DB_PASSWORD:-`pwgen 14 1`}
export COMMIT_ID=`git rev-parse HEAD`
terraform -chdir=./azure/ apply
terraform -chdir=./azure/ output -raw acr_username ; echo
terraform -chdir=./azure/ output -raw acr_password ; echo
terraform -chdir=./azure/ output -raw kube_config  ; echo
az aks get-credentials --resource-group EPAM_Diploma --name aks1 --admin --overwrite-existing
az acr login --name mskepamdiplomaacr
docker build -t nhltop:$COMMIT_ID ./app/
docker tag nhltop:$COMMIT_ID mskepamdiplomaacr.azurecr.io/nhltop:$COMMIT_ID
docker push mskepamdiplomaacr.azurecr.io/nhltop:$COMMIT_ID
kubectl create ns dev
kubectl create ns prod
kubectl create ns monitoring
sed -s -e "s/{{ DB_NAME }}/test/"          \
       -e "s/{{ NAMESPACE }}/dev/"         \
       -e "s/{{ COMMIT_ID }}/$COMMIT_ID/"  \
       ./k8s/deploy-tpl.yaml | kubectl -n dev apply -f -
sed -s -e "s/{{ DB_NAME }}/nhltop/"        \
       -e "s/{{ NAMESPACE }}/prod/"        \
       -e "s/{{ COMMIT_ID }}/$COMMIT_ID/"  \
       ./k8s/deploy-tpl.yaml | kubectl -n prod apply -f -
kubectl -n dev  create secret generic appsec --from-literal=db_password=$TF_VAR_DB_PASSWORD
kubectl -n prod create secret generic appsec --from-literal=db_password=$TF_VAR_DB_PASSWORD

# Monitoring:
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring
kubectl apply -f ./k8s/sm.yaml
kubectl get secret -n monitoring prometheus-grafana \
       	-o jsonpath={.data.admin-user} | base64 -d ; echo
kubectl get secret -n monitoring prometheus-grafana \
	-o jsonpath={.data.admin-password} | base64 -d ; echo
kubectl -n monitoring port-forward \
	svc/prometheus-kube-prometheus-prometheus \
	--address 0.0.0.0 9090 &
kubectl -n monitoring port-forward \
	svc/prometheus-grafana \
	--address 0.0.0.0 3000:80 &

cat <<EOF
Development environment:

    http://msk-epam-diploma-dev.westeurope.cloudapp.azure.com/

Production environment:

    http://msk-epam-diploma-prod.westeurope.cloudapp.azure.com/

EOF
