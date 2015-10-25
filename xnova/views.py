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
        try:
            User.objects.create_user(attributes['name'])
            return HttpResponse(encoder.encode({
                'data': {
                    'type': 'users',
                    'attributes': {
                        'name': attributes['name'],
                        'email': attributes['email'],
                    }
                }
            }))
        except Exception, e:
            return HttpResponse(
                encoder.encode({'errors': [{
                    'detail': 'A user with the same name already exists',
                    'source': {'pointer': '/data/attributes/name'}
                }]}),
                status=400,
                content_type='application/vnd.api+json'
            )

    users = User.objects.all()
    data = [{'attributes': {
        'name': user.username,
        'email': user.email
    }} for user in users]
    return HttpResponse(
        encoder.encode({'data': data}),
        content_type='application/vnd.api+json'
    )
