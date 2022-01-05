# ebsi-diplomas web

**Web service for online EBSI-diplomas agents**

**DISCLAIMER: This is only a prototype and not currently intended for
production. Private keys are stored as plaintext in a file.**

![Python >= 3.10](https://img.shields.io/badge/python-%3E%3D%203.10-blue.svg)

Django application capable of issuing and verifying diplomas upon request from
a client, while also resolving DIDs which have been registered to the EBSI
ledger.

It uses `ssi-lib` as its backend (currently a wrapper of
[`waltid-ssikit`](https://github.com/walt-id/waltid-ssikit)).

## Install and run

## Issuance functionality

Submitted content is currently not compared against the issuer's database. This
means that any issuance request with a well-formed paylaod leads to the award
of a verifiable diploma, even if the payload (and thus the content of the
generated credential) does not correspond to reality. This should change in the
future, once the issuer's database is populated with users and a policy is
specified for transforming submitted payloads to user and diploma data.

## REST API endpoints

#### `GET api/v1/did`

Show current DID alias.

#### `PUT api/v1/did/create`

Create or update DID.

**Note**: This is administrative and should be exposed only to authorized
officials.

#### `POST api/v1/credentials/issue`

Issue verifiable diploma according to submitted content.

**Note**: See *Issuance functionality* above.

#### `POST api/v1/credentials/verify`

Verify presented credentials.

## Development

### Database

### Tests
