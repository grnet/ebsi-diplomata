from django.http import JsonResponse
from http import HTTPStatus


def render_data(data, status):
    return JsonResponse({'data': data}, status=status)


def render_errors(errors, status):
    return JsonResponse({'errors': errors}, status=status)


def render_200_OK(data):
    return render_data(data, HTTPStatus.OK)


def render_201_CREATED(data):
    return render_data(data, HTTPStatus.CREATED)


def render_204_NO_CONTENT():
    return render_data({}, HTTPStatus.NO_CONTENT)


def render_400_BAD_REQUEST(err=None):
    errors = ['Bad Request', ] if not err else [err, ]
    return render_errors(errors, HTTPStatus.BAD_REQUEST)


def render_401_UNAUTHORIZED(err=None):
    err = 'Unauthorized' if not err else err
    return render_errors([err, ], HTTPStatus.UNAUTHORIZED)


def render_404_NOT_FOUND(err=None):
    errors = ['Resource Not Found', ] if not err else [err, ]
    return render_errors(errors, HTTPStatus.NOT_FOUND)


def render_422_UNPROCESSABLE_ENTITY(err=None):
    err = 'Unprocessable entity' if not err else err
    return render_errors([err, ], HTTPStatus.UNPROCESSABLE_ENTITY)
