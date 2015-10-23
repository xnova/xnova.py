from django.contrib.auth.models import User
from rest_framework import serializers

__author__ = 'rafa'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
