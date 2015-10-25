import json
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse


def user_list(request):
    """
    :type request: rest_framework.
    :rtype: HttpResponse
    """
    encoder = DjangoJSONEncoder()
    if request.method == 'POST':
        content = json.loads(request.body)
        return HttpResponse(encoder.encode(
            {
                'data': {
                    'type': 'users',
                    'name': content['data']['name'],
                    'email': content['data']['email'],
                }
            }
        ))
    # if request.method == 'POST':
    #     return HttpResponse(status=201, content_type='application/vnd.api+json')

    # return HttpResponse(encoder.encode([]),
    #                     status=200,
    #                     content_type='application/vnd.api+json')
    return HttpResponse(encoder.encode({'data': []}),
                        content_type='application/vnd.api+json')
