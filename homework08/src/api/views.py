from rest_framework import viewsets
from notes.models import Note
from accounts.models import User
from .serializers import NoteSerializer, UserSerializer


class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer
    queryset = Note.objects.all()

    def get_queryset(self):
        if self.request.query_params.get('title', None):
            title = self.request.query_params.get('title', None)
            self.queryset = self.queryset.filter(title__contains=title)
        elif self.request.query_params.get('tag', None):
            tag = self.request.query_params.get('tag', None)
            self.queryset = self.queryset.filter(tags__contains=tag)
        return self.queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def perform_create(self, serializer):
        serializer.save()
