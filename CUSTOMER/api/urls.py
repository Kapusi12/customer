from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, CompanyListView, QueryView, ConversationView

from .views import RegisterView, LoginView, CompanyRegistrationView

router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/', include(router.urls)),
    path('api/register_company/', CompanyRegistrationView.as_view(), name='register-company'),
    path('api/companies/', CompanyListView.as_view(), name='company-list'),
    path('api/query/', QueryView.as_view(), name='query'),
    path('api/conversations/', ConversationView.as_view(), name='conversations'),
]
