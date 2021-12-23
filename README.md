# ebsi-diplomas

**Issuance and verification of university diplomas in the SSI/EBSI context.**

![Python >= 3.10](https://img.shields.io/badge/python-%3E%3D%203.10-blue.svg)

This is a simulation of the verifiable diplomas lifecycle in the Self-Sovereign
Identity (SSI) context. Digital identities of involved parties are
decentralized identifiers (DIDs) registered at the European Blockchain Service
Infrastructure (EBSI) ledger.

Purpose of this project is the stabilization of issuer and verifier REST APIs
along with implementing a reference wallet and a Python package to be used by
all involved agents. To this end,
[`waltid-ssikit`](https://github.com/walt-id/waltid-ssikit) has been chosen as
a SSI/EBSI backend of acclaimed general general utility.

### Components

- [`web`](./web): Django app exposing a REST API with issuance and verification
  endpoints. Online issuers and verifiers are instances of this service.
- [`wallet`](./wallet): Local application for managing multiple identities,
  storing credentials and interacting with online issuers and verifiers. It is
  intended for use by credential holders and offline verifiers.
- [`ssi-lib`](./ssi-lib): Python library providing core SSI capabilities to the
  above agents. These include DID registration to the EBSI ledger and DID
  resolution.

## Setup

Make sure to initialize submodules when cloning the project:

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

**Note**: Building the containers from zero takes several minutes due to the
compilation time of the [`waltid-ssikit`](https://github.com/walt-id/waltid-ssikit)
dependency.

## Quickstart

Run the `issuer` and `verifier` services at `localhost:7000-1` respectively with:

```commandline
docker-compose up
```

Once both services are up, create a DID for each with:

```commandline
./create-dids
```

**WARNING**: You will be asked to provide an EBSI token for onboarding the newly
created DIDs. If an invalid or expired token is provided, DIDs will fail to
onboard and will not be stored. Run with `--no-register` if you want to create
DIDs without registering them to the EBSI, but remember that non-registered
DIDs fail to resolve and thus be effectively involved in protocol operations.

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

**Upon any such update make sure to rebuild the containers.**

### [`ssi-lib`](./ssi-lib)

When introducing changes to `ssi-lib` make sure to rebuild the containers.

### Mounted volumes

### Tests
