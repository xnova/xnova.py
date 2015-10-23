from django.contrib.auth.models import User
from rest_framework import viewsets
from xnova.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
