from django.conf import settings


def generate_swagger_dict():
    return {
        "swagger": "2.0",
        "info": {
            "version": "1.0.0",
            "title": "GRNET e-Diplomas Service",
            "description": "Issuance and verification of VC diplomas",
        },
        "basePath": settings.API_PREFIX,
        "schemes": [
            "http",
        ],
        "consumes": [
            "application/json",
        ],
        "produces": [
            "application/json",
        ],
        "paths": {
            f"{settings.API_PREFIX}/did": {
                "get": {},
            },
            f"{settings.API_PREFIX}/token": {
                "get": {},
            },
            f"{settings.API_PREFIX}/google/login": {
                "get": {},
            },
            f"{settings.API_PREFIX}/users/current": {
                "get": {},
            },
            f"{settings.API_PREFIX}/credentials/issue": {
                "post": {},
            },
            f"{settings.API_PREFIX}/credentials/verify": {
                "post": {},
            },
        },
        "definitions": {}
    }
