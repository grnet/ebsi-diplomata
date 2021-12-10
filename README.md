# ebsi-diplomas

## Setup

Make sure to initialize submodules when cloning the project, so that
[`waltid-ssikit`](https://github.com/walt-id/waltid-ssikit) be locally included
(this is necessary for building the components):

```commandline
git clone git@gitlab.grnet.gr:devs/priviledge/ebsi-diplomata.git --recurse-submodules
```

Build the wallet application as follows:

```commandline
./run-wallet.sh --only-build
```

Build the issuer and verifier services as follows:

```commandline
docker-compose build
```

## Quickstart

Run the issuer and verifier services with

```commandline
docker-compose up
```

and visit localhost at ports `7000` and `7001` respectively. Run locally
the wallet app with

```commandline
./run-wallet.sh
```

You are now ready to interact with the services.

## Development

### Submodule updates

[`waltid-ssikit`](https://github.com/walt-id/waltid-ssikit) is WIP, so the
included submodule must be regularly updated:

```commandline
git submodule update --remote
```

**Upon any such update, make sure to rebuild wallet and services.**

### Tests
