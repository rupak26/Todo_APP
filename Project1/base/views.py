from .models import Todo,User
from .serializers import loginSerializer,UserRegisterSerializer,TodoSerializer,TododResponseSerializer
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated ,AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken
from rest_framework.exceptions import NotAuthenticated
from rest_framework.parsers import JSONParser
import io
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class UserRegistrationView(APIView):
    permission_classes = []
    def post(self,request):
        serializer = UserRegisterSerializer(data = request.data)
        if serializer.is_valid():
            validated_data = dict(serializer.data)
            user = User.objects.create_user(email=validated_data['email'], password=validated_data['password'])
            user.save()
            return Response({'msg':'Registration Successful'},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)



class userLoginView(APIView):
    permission_classes = []
    def post(self, request):
        serializer = loginSerializer(data=request.data)
        if serializer.is_valid():
            validated_date = dict(serializer.data)
            user = authenticate(email = validated_date["email"], password = validated_date["password"])
            if user:
                desire_id  = user.id
                return Response({"token" : get_tokens_for_user(user)})
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class TodoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.query_params.get('user_id', None)
        if user_id is not None: 
            stu = Todo.objects.filter(user_id = user_id)
            serializer = TodoSerializer(stu ,many = True)
            return Response(serializer.data)
        
        todos = Todo.objects.all()
        serializer = TodoSerializer(todos, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = TodoSerializer(data=request.data)
        if serializer.is_valid():
            newTodo = Todo(title = serializer.data.get('title'), details = serializer.data.get('details') ,user = request.user)
            newTodo.save()
            newTodoSerializer = TododResponseSerializer(newTodo)
            return Response(newTodoSerializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)