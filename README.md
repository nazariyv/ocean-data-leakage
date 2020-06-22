# Ocean Protocol Data Leakage Privacy Hack

[![banner](https://raw.githubusercontent.com/oceanprotocol/art/master/github/repo-banner%402x.png)](https://oceanprotocol.com)

[![Inline docs](http://inch-ci.org/github/dwyl/hapi-auth-jwt2.svg?branch=master)](http://inch-ci.org/github/dwyl/hapi-auth-jwt2)

Whoever stumbles on this, my name is Nazariy, and I worked on the Ocean Protocol's Gitcoin privacy hack to protect the data against leaks by the means of running the algorithms on the mentioned data.

This repo is a part of a number of other repos that form the complete submission. This section [Repo dependencies on which I have worked](#repo-dependencies-on-which-i-have-worked) talks about all of the repos.

I would like to thank Ocean Protocol, and particularly Alex for helping me navigate their cool tech stack and setting up my environment.

## Table of Contents

[DEV](#dev)

[Repo dependencies on which I have worked](#repo-dependencies-on-which-i-have-worked)

[Code Features](#filter-code-features)

[Conditions Rationale & Workings](#conditions-rationale--workings)

[Video Link Where I talk about this task](#video-link-where-i-talk-about-this-task)

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

## Repo dependencies on which I have worked

[brizo](https://github.com/nazariyv/brizo.git)

- to be able to pass data categories into workflow so that we can filter by keywords by category

---

[operator-engine](https://github.com/nazariyv/operator-engine.git)

- to be able to create an additional "filter" job in between the "algorithm" and "publish" pod who sole purpose is to take the outputs of the algorithm pod and check for potential data leaks. The `4` conditions that it runs are:

1. checks if the output is encrypted input
2. whether output is small in size compared input
3. whether the input and output is correlated too much
4. whether there are no keywords given the data category of the input

---

[this-repo](https://github.com/nazariyv/ocean-data-leakage.git)

- to define dummy algorithms to test the filter pod against
- to define the filter pod with all its logic (in filter/)
- to define a Makefile that simplifies config and start-up of the compute-to-data service

## Filter code features

### Neat things

- Statically typed
- Pylinted
- Black formatted
- Pytest covered 😉 (conditions folder `86%`; run `make test` fin `filter`; this will generate `htmlcov/index.html` in the same folder)
- AAAAND

# HAS ACTUAL COMMENTS

<div style="text-align:center"><img src="https://66.media.tumblr.com/85936cc9f4ddb696d391863f4c3f134b/tumblr_odtjxfgzXw1qgf1i8o1_250.gif"/></div>

Me writing comments

<div style="text-align:center"><img src="https://i.giphy.com/media/LmNwrBhejkK9EFP504/giphy.webp"/></div>

## Filter pod overview

Has `4` conditions that the algorithm output should meet:

1. Its size be `10%` or smaller than the input
2. The output is not encrypted input
3. Not too correlated
4. Has no keywords

### Conditions rationale & workings

1. **Size**. Easy, all of the outputs have to be `10%` smaller than all of the inputs.
2. **Not Encrypted**. Output after running the algo cannot be encrypted. I have decided to use entropy measure to determine if the output is encrypted. Please see the below for why we use the formula that we use (I have used `binwalk` tool as an inspiration for this)

<div style="text-align:center;max-width:1024px;max-height:1400px"><img src="assets/shannon.png" /></div>

^I realize I have not explained the "why" part in that image. And the explanation may not be `100%` clear. Basically, we make an upper bound on Shannon entropy by `(1)` ignoring all the probabilities of `0`, `(2)` using log base `2` function to get the maximum Shannon entropy of `8`. Normalize this and we get a value in the range `[0, 1]` (another typo, obviously, in the above equations). We set the threshold to the default value of `0.85`. If the file has larger entropy than that, we believe it is encrypted. What distinguishes encrypted files from non-encrypted is their high randomness of the character distribution. This is picked up by our algorithm. Another note to make is that we compute the entropy in blocks of `1024` bytes by default. This value can be changed.

3. **Not correlated**. This was the toughest one, thinking-wise. If we use simple correlation measure like Pearson's correlation coefficient, then we are likely not going to get a good result. This is because this measure is not shift invariant. If we scramble the data around, then the correlation coefficient will be different. Put it simply, it is order dependent. On top of that the input is `10%` smaller. So which part of input corresponds to which part of output. Well, can we calculate the correlation of features? No, because there is no restriction on the form of the output data, so columns can be shuffled too. On top of even that, we can have different file types that would each require unique parsing. This is all pretty bad. So, why not use our trusty entropy again? And use we do. We take the output's file size (we know it is 10% size of the original dataset) and read the input (note I have not said input**s**) in blocks of its size. This way we evaluate the entropy contents of blocks of same size and have a rough idea about how much entropy there is in the original. We take the average over all of these. Compare this to the entropy of the input +/- the epsilon threshold

   **Détour**

   > env variable: `CORRELATION_ENTROPY_THRESH` that you have to set. Remember if you set it to `0.05`, then that is `0.1` in total, since we do +/- the entropy. I have set it to `0.075` by default because I thought that `0.1` is too high and will raise too many false positives and `0.05` is too low and won't raise them at all, not that we actually need them... So consider looking at a real-wrold data and adjusting as needed

4. **Does not contain any keywords**. If you thought this would be the easiest part, you'd be wrong. This was the toughest. First of all we need to pull the category of the data (we define keywords for each category for each environment in a `yaml` file in the `filter/conditions/config`). This, thanks a lot to Alex for the help here, meant making some tweaks in brizo, to forward the required data to op-engine. Once we have the keywords it becomes easy to check if a file contains them. However, each file type requires special handling. I have added the reader for `csv` files. The complexity of this algorithm is incredibly poor however. It is cubic. It is of the order of the number of keywords times the number of words in the file times the number of files. So consider dropping this condition completely.

   **Détour**

   > To understand why I went with "baking the keyword config files into the Docker image" consider this passage from Viktor Farcic's book:
   >
   > > If we were to start developing a new application today, it would be, among other things, distributed, scalable, stateless, and fault tolerant. Those are some of today’s needs. While we might question how many of us know how to design an application with those quality attributes in mind, hardly anyone would argue against having any of them. What is often forgotten is the configuration. Which mechanism should your new application use to configure itself? How about environment variables?
   > >
   > > > Environment variables fit well into distributed systems. They are easy to define, and they are portable. They are the ideal choice for configuration mechanism of new applications.
   > >
   > > However, in some cases, the configuration might be too complex for environment variables. In such situations, we might need to fall back to files (hopefully YAML). When those cases are combined with legacy applications which are almost exclusively using file-based configuration, it is evident that we cannot rely only on environment variables.
   > >
   > > When a configuration is based on files, the best approach we can take is to bake the configuration into a Docker image. That way, we are going down the fully-immutable road. Still, that might not be possible when our application needs different configuration options for various clusters (e.g., testing and production).

## Anyone wants to share in the bounty of the hack? Feel free to extend my work and ping me with questions

## Video Link Where I talk about this task

<div style="text-align:center"><img src="https://66.media.tumblr.com/f62f00b474ffbe5fb589d29ba0fdd0ec/tumblr_ndctwzSBuE1rraqsio1_400.gifv" /></div>
