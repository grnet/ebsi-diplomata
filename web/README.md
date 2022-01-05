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
means that any issuance request with a well-formed payload leads to the award
of a verifiable diploma, even if the payload (and thus the content of the
generated credential) does not correspond to reality. This should change in the
future, once the issuer's database is populated with users and a policy is
specified for transforming submitted payloads to user and diploma data.

## REST API endpoints

#### `GET api/v1/did`

Show current DID alias.

**Code**: `200 OK`

```json
{
    "data": {
        "did": "did:ebsi:z24xwq2QbuphdKgmQDTTg7vn"
    }
}
```

**Code**: `512`

```json
{
    "errors": [
        "No DID found"
    ]
}
```

#### `PUT api/v1/did/create`

Create or update DID.

```json
{
    "algo": "Ed25519",
    "token": "eyJhbGciOiJFUzI1NksiLCJ0eXAiOiJKV1QifQ.eyJleHAiOjE2NDE0MDQyMzUsImlhdCI6MTY0MTQwMzMzNSwiaXNzIjoiZGlkOmVic2k6emNHdnFnWlRIQ3Rramd0Y0tSTDdIOGsiLCJvbmJvYXJkaW5nIjoicmVjYXB0Y2hhIiwidmFsaWRhdGVkSW5mbyI6eyJhY3Rpb24iOiJsb2dpbiIsImNoYWxsZW5nZV90cyI6IjIwMjItMDEtMDVUMTc6MjI6MTRaIiwiaG9zdG5hbWUiOiJhcHAucHJlcHJvZC5lYnNpLmV1Iiwic2NvcmUiOjAuOSwic3VjY2VzcyI6dHJ1ZX19.5XtFq7bAagG9fgAYw1nHxZES7htRnl_froU1-KPTOEQsOPXBngQRsAnjh-h_EpjUVv4kq6XXtiMiaB6X_aTe2g",
    "onboard": true
}
```

**Note**: This is administrative and should be exposed only to authorized
officials.

#### `POST api/v1/credentials/issue`

Issue verifiable diploma according to submitted content.

```json
{
    "holder": "did:ebsi:zrd6pK5wiACqxVed4gwJc7P",
    "vc_type": "DIPLOMA",
    "content": {
        "person_id": 666,
        "name": "John",
        "surname": "Doe",
        "subject": "Mathematics"
    }
}
```

**Note**: See *Issuance functionality* above.

#### `POST api/v1/credentials/verify`

Verify presented credentials.

```json
{
    "presentation": {
        ...
    }
}
```

## Development

### Database

### Tests
