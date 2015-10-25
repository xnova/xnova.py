import json

from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse


def player_list(request):
    """
    :type request: rest_framework.
    :rtype: HttpResponse
    """
    encoder = DjangoJSONEncoder()

    if request.method == 'POST':
        content = json.loads(request.body)
        attributes = content['data']['attributes']
        if User.objects.filter(email=attributes['email']).count():
            return HttpResponse(
                encoder.encode({'errors': [{
                    'detail': 'A player with the same email already exists',
                    'source': {'pointer': '/data/attributes/email'}
                }]}),
                status=400,
                content_type='application/vnd.api+json')
        try:
            new_user = User.objects.create_user(
                attributes['name'],
                email=attributes['email'])
            return HttpResponse(
                encoder.encode({
                    'data': {
                        'type': 'users',
                        'id': new_user.id,
                        'attributes': {
                            'name': attributes['name'],
                            'email': attributes['email'],
                        },
                        'links': {
                            'self': '/players/%d/' % (new_user.id,)
                        }
                    }
                }),
                content_type='application/vnd.api+json')
        except Exception, e:
            return HttpResponse(
                encoder.encode({'errors': [{
                    'detail': 'A player with the same name already exists',
                    'source': {'pointer': '/data/attributes/name'}
                }]}),
                status=400,
                content_type='application/vnd.api+json'
            )

    users = User.objects.all()
    data = [{
                'attributes': {'name': user.username, 'email': user.email},
                'links': {'self': '/players/%d/' % (user.id,)},
                'relationships': None
            } for user in users]
    return HttpResponse(
        encoder.encode({'data': data}),
        content_type='application/vnd.api+json'
    )


def player_detail(request, player_id):
    encoder = DjangoJSONEncoder()

    user = User.objects.get(pk=player_id)
    data = {
        'attributes': {'name': user.username, 'email': user.email},
        'relationships': {'homeplanet': None}
    }
    return HttpResponse(encoder.encode({'data': data}),
                        content_type='application/vnd.api+json')
