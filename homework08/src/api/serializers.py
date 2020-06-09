from rest_framework import serializers
from accounts.models import User
from notes.models import Note


class NoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Note
        fields = ('id', 'title', 'body', 'pub_date',
                  'tags', 'owner', 'access')


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'is_active', 'is_confirmed', 'is_staff',
                  'secret_key')
