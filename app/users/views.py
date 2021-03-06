from rest_framework import generics, permissions, authentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from .serializers import UserSerializer, AuthTokenSerializer


class CreateUserApiView(generics.CreateAPIView):
    """A generic Api view that creates a new user"""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new Token for authenticated users"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Update an authenticated user's information"""
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def get_object(self):
        """Return authenticated user"""
        return self.request.user
