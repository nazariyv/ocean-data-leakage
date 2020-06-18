# Ocean Protocol Data Leakage Privacy Hack

## DEV

This section is for those who would like to participate in Ocean Protocol hacks and would like to save themselves some time setting up the environment.

In the root of this project, run: `make dev`

TODO: still need to manully run finalize.sh to input the POSTGRSEDB password and initialize the db

This will start barge for you and will spin up a minikube kubernetes cluster with operator-engine and operator service. Everything will communicate perfectly with everything else

Ensure that you put in your aws creds in operator.yaml if you would like persistance

TODO: tie up the images to versions, etc. Make setting up the environment consistent

TODO: guide the users step by step letting them input all the env variables like aws etc. so that it all works for them out of the box

Tested on:
Darwin 10.15.5
minikube v1.9.2 (required for proper persistent volume behaviour)
kubectl v1.18.4
and Docker/Preferences/Resources/Advanced Memory set to 4 GB RAM (required to successfully build oceancommons client container when running barge)
