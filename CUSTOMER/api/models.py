from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Company(models.Model):
    name = models.CharField(max_length=100, unique=True)
    pdf_file = models.FileField(upload_to='pdfs/')
    description = models.TextField(max_length=1000)
    logo = models.ImageField(upload_to='logos/')
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user_message = models.TextField()
    ai_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation with {self.company.name} by User {self.user.first_name}"
