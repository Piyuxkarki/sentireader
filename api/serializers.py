from rest_framework import serializers
from django.contrib.auth.models import User
from .models import JournalEntry, Results


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}
    

class JournalEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalEntry
        fields = '__all__'


class ResultsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Results
        fields = '__all__'


