from rest_framework import generics, viewsets
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from src.accounts.models import User
from src.api.models import Predication
from .serializers import (
    UserPasswordChangeSerializer, UserSerializer,
    PredicationSerializer
)
from core import settings
import random
import pickle

""" AUTH USER API' S """


class UserPublicDetailedView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class UserProfileDetailedView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserPasswordChangeView(generics.UpdateAPIView):
    model = User
    serializer_class = UserPasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }
            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


""" PUBLIC API'S """


class PredicationViewSet(viewsets.ModelViewSet):
    serializer_class = PredicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Predication.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = PredicationSerializer(data=request.data)

        print('Creating prediction')

        if serializer.is_valid():
            prediction = serializer.save()
            prediction.user = request.user

            filename = f'{settings.BASE_DIR}\\modelForPrediction.sav'
            message = 0
            try:
                print(filename)
                loaded_model = pickle.load(open(filename, 'rb'))  # loading the model file from the storage
                # predictions using the loaded model file
                scaler = pickle.load(open(f'{settings.BASE_DIR}\\standardScalar.sav', 'rb'))
                prediction = loaded_model.predict(
                    scaler.transform([[random.randint(0, 9), random.randint(0, 9), random.randint(0, 9),
                                       random.randint(0, 9), random.randint(0, 9),
                                       random.randint(0, 9), random.randint(0, 9), random.randint(0, 9),
                                       random.randint(0, 9),
                                       random.randint(0, 9), random.randint(0, 9), random.randint(0, 9),
                                       random.randint(0, 9),
                                       random.randint(0, 9), random.randint(0, 9), random.randint(0, 9),
                                       random.randint(0, 9),
                                       random.randint(0, 9), random.randint(0, 9), random.randint(0, 9),
                                       random.randint(0, 9),
                                       random.randint(0, 9)]]))
                message = prediction
            except:
                message = 0

            prediction.status = message
            prediction = prediction.save()
            return Response(data={'message': f'Predication created, Status = {prediction}'},
                            status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
