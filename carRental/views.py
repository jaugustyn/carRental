from rest_framework.response import Response
from rest_framework.views import status
from rest_framework import viewsets
from .models import Car
from .serializers import CarSerializer


# Create your views here.


class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer

    def perform_create(self, serializer):
        request = serializer.context['request']
        serializer.save(created_by=request.user.id)

    def perform_update(self, serializer):
        request = serializer.context['request']
        serializer.save(created_by=request.user.id)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.created_by = request.user.id
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)



