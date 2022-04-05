from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.response import Response
from rest_framework.views import status, APIView
from django.contrib.auth import login, logout
from rest_framework import viewsets, generics, permissions

from .models import Car
from .serializers import CarSerializer, UserSerializer, RegisterSerializer, UserSimpleSerializer

from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView


# Create your views here.


class UserList(generics.GenericAPIView):
    serializer_class = UserSerializer

    @staticmethod
    def get(request, *args, **kwargs):
        print(request.user)
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })


class LoginView(KnoxLoginView, generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSimpleSerializer

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginView, self).post(request, format=None)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get(request):
        try:
            token = AuthToken.objects.filter(user=request.user)
            if token:
                token.delete()
        except Exception:
            "There is no token"
        logout(request)
        return Response(status=status.HTTP_200_OK)


class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        request = serializer.context['request']
        serializer.save(created_by=request.user)

    def perform_update(self, serializer):
        request = serializer.context['request']
        serializer.save(updated_by=request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.created_by = request.user
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
