# ebsi-diplomas wallet

**Local wallet app for EBSI-diplomas involved parties.**

![Python >= 3.10](https://img.shields.io/badge/python-%3E%3D%203.10-blue.svg)

This application is a client to the `issuer` and `verifier` services running at
`localhost:7000-1` respectively. It can request issuance and verification of
diplomas from remοte parties while aso managing multiple identities (DIDs)
which can be registered to the EBSI ledger. It can further perform DID resolution 
by connecting to the EBSI ledger, verify any presentation and generate self-issued 
credentials for testing and debugging purposes.

The application is currently accessible from within a shell (command interpreter) 
but its core module is standalone and can admit alternative user interfaces. It
is connected to a local SQL database for storing keys, DIDs, credentials and
verifiable presentations. It uses `ssi-lib` as its backend, which is currently a 
wrapper of [`waltid-ssikit`](https://github.com/walt-id/waltid-ssikit).

## Run wallet

Assuming `sqlite3` is available, `waltid-ssikit` has been built and`ssi-lib` has 
been properly installed, you can run the wallet with

```
$ python3 src
```

However, it is better to run it with docker from inside the project root:

```
$ ./run-wallet.sh
```

This will run the wallet shell inside a container called `holder` and connect
the wallet app to a database mounted at `/storage/wallet/holder.db`.

Run with `--help` to see more options.

## Usage

The wallet is accessed via a shell (command interpreter) where commands for the
basic tasks are available. This is crude but intuitive. Type `help` to see
available commands and details.

## Development
