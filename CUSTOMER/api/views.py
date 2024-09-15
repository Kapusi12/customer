from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework import viewsets
from .models import Company, Conversation
from .serializers import CompanySerializer, ConversationSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from .ai_model import get_response


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class CompanyListView(APIView):
    def get(self, request):
        companies = Company.objects.all()
        serializer = CompanySerializer(companies, many=True)
        return Response(serializer.data)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email = request.data.get('email')
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email,
                                            password=password)
            user.save()
            return Response({"success": "User created successfully"}, status=status.HTTP_201_CREATED)
        except:
            return Response({"error": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = User.objects.filter(username=username).first()
        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({"error": "Invalid credentials", }, status=status.HTTP_400_BAD_REQUEST)


class CompanyRegistrationView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Company registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QueryView(APIView):
    def post(self, request):
        company_name = request.data.get('company_name')
        user_message = request.data.get('message')
        username = request.data.get('username')

        company = Company.objects.get(name=company_name)
        responses = get_response(user_question=user_message, company_file_url=company.pdf_file.url)
        ai_response = responses
        user = User.objects.get(username=username)
        conversation = Conversation.objects.create(
            user=user,
            company=company,
            user_message=user_message,
            ai_response=ai_response
        )

        # Serialize the conversation for return
        conversation_serializer = ConversationSerializer(conversation)

        # Return the response to the mobile app
        return Response(conversation_serializer.data, status=status.HTTP_200_OK)


class ConversationView(APIView):
    def post(self, request):
        username = request.data.get('username')
        try:
            user = User.objects.get(username=username)
            conversations = Conversation.objects.filter(user=user)
            print(conversations)
            if conversations.exists():
                serializer = ConversationSerializer(conversations, many=True)
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"message": "No conversations yet!"}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
