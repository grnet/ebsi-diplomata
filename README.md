# ebsi-diplomas

**Issuance and verification of university diplomas in the SSI/EBSI environment**

![Python >= 3.10](https://img.shields.io/badge/python-%3E%3D%203.10-blue.svg)

This simulates the lifecycle of verifiable diplomas in the Self-Sovereign Identity (SSI)
context, where the digital identities of involved parties are decentralized identifiers
(DIDs) registered at the European Blockchain Service Infrastracture (EBSI). Purpose of
this project the stabilization of issuer/verifier REST APIs along with the creation of
a python package which can be used by all involved parties. To this end the
[`waltid-ssikit`](https://github.com/walt-id/waltid-ssikit) library is used 
as a SSI/EBSI backend of acclaimed general utiliy.

## Setup

Make sure to initialize submodules when cloning the project, so that
[`waltid-ssikit`](https://github.com/walt-id/waltid-ssikit) be locally included
(this is necessary for building the components):

```commandline
git clone git@gitlab.grnet.gr:devs/priviledge/ebsi-diplomata.git --recurse-submodules
```

Assuming `docker` is installed, build the wallet application as follows:

```commandline
./run-wallet.sh --only-build
```

Similarly, assuming `docker-compose` is available, build the issuer and verifier
services with:

```commandline
docker-compose build
```

## Quickstart

Run the `issuer` and `verifier` services at `localhost:7000-1` respectively with:

```commandline
docker-compose up
```

Once both services are up, create a DID for each with:

```commandline
./create-dids
```

**Note**: You will be asked to provide an EBSI token for onboarding the newly
created DIDs.

Run the wallet inside a container called `holder` with:

```commandline
./run-wallet.sh
```

You are ready to manage identities and interact via the wallet shell (command
interpreter). Type `help` to see available commands and details.

## Development

### Submodule updates

[`waltid-ssikit`](https://github.com/walt-id/waltid-ssikit) is WIP, so the
included submodule must be regularly updated:

```commandline
git submodule update --remote
```

**Upon any such update, make sure to rebuild the containers.**
