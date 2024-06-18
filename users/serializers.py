from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer, CharField


class UserRegisterSerializer(ModelSerializer):
    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    class Meta:
        model = get_user_model()
        fields = ('username', )


class UserGetTokenSerializer(ModelSerializer):
    code = CharField(max_length='7')

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    class Meta:
        model = get_user_model()
        fields = ('username', 'code')
