# ebsi-diplomas wallet

**Reference implementation of EBSI-diplomas wallet**

![Python >= 3.10](https://img.shields.io/badge/python-%3E%3D%203.10-blue.svg)

Local application for managing multiple identiies (keys and DIDs), storing
verifiable credentials and interacting with online issuers and verifiers.

This is an HTTP-client to the fixed issuer and verifier services running at
`localhost:7000-1` (see `docker-compose.yml` at the root of the project). It
can request diploma issuance and verification of presentations, perform DID
resolution by connecting to the EBSI ledger, locally verify credentials and
generate self-issued credentials for testing and debugging.

The application is currently accessible from within a shell but its core module
is standalone and admits alternative user interfaces. It connects to a local
SQL database and uses `ssi-lib` as its backend (currently a wrapper of
[`waltid-ssikit`](https://github.com/walt-id/waltid-ssikit)).

## Usage

```
$ ./run-wallet.sh --help
```

from inside the root of the project for details.

The wallet is managed via a shell (command interpreter). This is crude but intuitive.
Once inside the shell, type `help` to see available commands and details.

## Development

### Database

Wallet data (keys, DIDs, credentials and verifiable presentations) are
persistenty stored inside `storage/wallet`. In particular, a sqlite file is
created inside this folder for each wallet container. For example, assuming the
wallet runs inside a container called `holder`, the corresponding database may
be accessed from the root of the project with:

```
sqlite3 storage/wallet/holder.db
```

**Note**: From the container's internal viewpoint, the above folder is mounted
to `/home/wallet/storage/holder.db`.

### Tests
