# ssi-lib

**Library for EBSI-diplomas involved parties**

![Python >= 3.10](https://img.shields.io/badge/python-%3E%3D%203.10-blue.svg)

Purpose of this library is to serve as a cryptographic software run by all 
EBSI-diplomas python applications. It provides SSI core functionalities
(key generation, DID generation and resolution, issuance of credentials,
verification of presentations) along with the capability of registering DIDs to
the EBSI ledger and resolving them. This is actually a wrapper of the 
[`waltid-ssikit`](https://github.com/walt-id/waltid-ssikit) library, which
acclaims to be a toolkit of such general utility.


## Install

The package can be simply installed with

```
python3 setup.py install 
```

However, in order to be able to use it, you must also build 
[`waltid-ssikit`](https://github.com/walt-id/waltid-ssikit) 
and make the executables of the `./commands` folder globally 
available (e.g., by transfering them inside `/usr/local/sbin` 
for Linux systems). 

## Usage

```python
from ssi_lib import SSI
```

## Development

### Tests
