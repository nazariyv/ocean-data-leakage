# Ocean Protocol Data Leakage Privacy Hack

## DEV

To have the output link after you run the jobs you need to define the following in `operator.yaml`. i.e. add your aws key and secret. Create S3 buckets yourself and add their names.

```yaml
- name: AWS_ACCESS_KEY_ID
  
  value: your_key
- name: AWS_SECRET_ACCESS_KEY
  
  value: your_secret_key
- name: AWS_REGION
  
  value: your_region
- name: AWS_BUCKET_OUTPUT
  
  value: "name_of_bucket_without_http_purely_name"
- name: AWS_BUCKET_ADMINLOGS
  
  value: "name_of_different_bucket_without_http_purely_name"
```

---

1. You need to fork this [repo](https://github.com/nazariyv/barge) that includes some amends to the original barge repo. In fact, if I recall correctly, I have only added the URL here

```yaml
OPERATOR_SERVICE_URL: "http://host.docker.internal:8050"
```

in `compose-files/brizo.yaml`

so that the container can get access to the host ip and communicate with the exposed kubernetes port

2. `cd` into barge and run:

```bash
./start_ocean.sh --latest --mongodb
```

3. In a different terminal window, cd into the root of this repo and run

```bash
make dev
```

this links up all the commands from the compute-to-data guide and all you have to do is sit back and enjoy, whilst minkube deploys the kubernetes cluster on your localhost.

Note that commons client ships with barge, you will need to wait a bit for step `2` to complete before you can access it at `localhost:3000`. If you are not getting pretty front-end, chances are the container that is reponsible for building the front-end can't because you have set `2` GB RAM in your Docker Advanced Resources settings. Changet this to `4` GB RAM. You can verify that it is failing due to this reason by going to the dashboard on `localhost:9000` and inspecting the logs of the commonsclient container.

Now that you have fancy front and minikube cluster, head to the faucet navigation item to request some Ocean and ETH. Before you do that, ensure that your MetaMask is running on `localhost:8545`. Barge spins up a local node for us. Once you have requested ETH and Ocean tokens (you will need to approve the transaction). Head over to publish. Publish dataset, I use the with URL method. Once published, you can submit your algos now. This repo has a bunch for you. Start with algos/non-violating one.

Congrats! Your filter data leak protection pod is running.
