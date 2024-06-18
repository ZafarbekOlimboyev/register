from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.generics import CreateAPIView
from django.contrib.auth import get_user_model
from rest_framework.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from users.serializers import UserRegisterSerializer, UserGetTokenSerializer
from rest_framework.response import Response

from random import randint

from .models import OneTimePassword


class RegisterView(CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserRegisterSerializer

    def perform_create(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(data={'msg': 'Code sent'}, status=status.HTTP_200_OK, headers=headers)

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}

    def post(self, request, *args, **kwargs):
        phone_number = request.data
        code = randint(100000, 999999)
        print(code)
        OneTimePassword(phone_number=phone_number.get('username'), code=code).save()
        if get_user_model().objects.filter(username=phone_number['username']).exists():
            return Response(data={'msg': 'Code sent1'})
        return self.create(request, *args, **kwargs)


class VerifyCodeView(CreateAPIView):
    serializer_class = UserGetTokenSerializer

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('username')
        code = request.data.get('code')
        if code and phone_number:
            try:
                otp = OneTimePassword.objects.get(phone_number=phone_number, code=code)
                if otp.created_at >= timezone.now() - timedelta(minutes=2) and otp.is_active:
                    otp.is_active = False
                    otp.save()
                    user = get_user_model().objects.get(username=phone_number)
                    token = RefreshToken.for_user(user)
                    return Response({
                        'refresh': str(token),
                        'access': str(token.access_token),
                    }, status=status.HTTP_200_OK)
                otp.is_active = False
                otp.save()
                return Response({"error": "Verification code is invalid or expired."},
                                status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response({"error": "Invalid phone number or verification code."},
                                status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "Phone number and verification code are required."},
                        status=status.HTTP_400_BAD_REQUEST)


