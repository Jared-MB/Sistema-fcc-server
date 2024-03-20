from django.shortcuts import render
from django.db.models import *
from django.db import transaction
from sistema_fcc_api.serializers import *
from sistema_fcc_api.models import *
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.generics import CreateAPIView, DestroyAPIView, UpdateAPIView
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from django.core import serializers
from django.utils.html import strip_tags
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string
import string
import random
import json

class TeachersAll(generics.CreateAPIView):
    #Esta linea se usa para pedir el token de autenticación de inicio de sesión
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        teachers = Profesores.objects.filter(user__is_active = 1).order_by("id")
        lista = ProfesorSerializer(teachers, many=True).data

        return Response(lista, 200)

class TeacherView(generics.CreateAPIView):
    def get(self, request, *args, **kwargs):
        teacher = get_object_or_404(Profesores, id = request.GET.get("id"))
        teacher = ProfesorSerializer(teacher, many=False).data

        return Response(teacher, 200)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user = UserSerializer(data=request.data)
        if user.is_valid():
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            password = request.data['password']

            existing_user = User.objects.filter(username=email).first()

            if existing_user:
                return Response({"message":"Username "+email+", is already taken"},400)
            
            user = User.objects.create_user(username=email, email=email, first_name=first_name, last_name=last_name, is_active=1)
            user.set_password(password)
            user.save()

            teacher = Profesores.objects.create(user=user,
                                                clave_profesor = request.data['id_trabajador'],
                                                fecha_nacimiento = request.data['fecha_nacimiento'],
                                                cubiculo = request.data['cubiculo'],
                                                area_investigacion = request.data['area_investigacion'],
                                                materias = request.data['materias_json']
                                            )
            teacher.save()
            return Response({"teacher_created_id": teacher.id }, 201)
        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)

# class StudentsAll(generics.CreateAPIView):
#     #Esta linea se usa para pedir el token de autenticación de inicio de sesión
#     permission_classes = (permissions.IsAuthenticated,)
#     def get(self, request, *args, **kwargs):
#         students = Alumnos.objects.filter(user__is_active = 1).order_by("id")
#         lista = AlumnoSerializer(students, many=True).data

#         return Response(lista, 200)

# class StudentView(generics.CreateAPIView):
#     #Obtener usuario por ID
#     # permission_classes = (permissions.IsAuthenticated,)
#     def get(self, request, *args, **kwargs):
#         student = get_object_or_404(Alumnos, id = request.GET.get("id"))
#         student = AlumnoSerializer(student, many=False).data

#         return Response(student, 200)

#     @transaction.atomic
#     def post(self, request, *args, **kwargs):
#         user = UserSerializer(data=request.data)
#         if user.is_valid():
#             #Grab user data
#             role = request.data['rol']
#             first_name = request.data['first_name']
#             last_name = request.data['last_name']
#             email = request.data['email']
#             password = request.data['password']
#             #Valida si existe el usuario o bien el email registrado
#             existing_user = User.objects.filter(username=email).first()

#             if existing_user:
#                 return Response({"message":"Username "+email+", is already taken"},400)
            
#             user = User.objects.create_user(username=email, email=email, first_name=first_name, last_name=last_name, is_active=1)
#             user.save()
#             user.set_password(password)

#             group, created = Group.objects.get_or_create(name=role)
#             group.user_set.add(user)
#             group.save()

#             #Create a profile for the user
#             student = Alumnos.objects.create(user=user,
#                                                 telefono = request.data['telefono'],
#                                                 fecha_nacimiento = request.data['fecha_nacimiento'],
#                                                 curp = request.data['curp'],
#                                                 rfc = request.data['rfc'],
#                                                 edad = request.data['edad'],
#                                                 ocupacion = request.data['ocupacion']
#                                             )
#             student.save()
#             return Response({"student_created_id": student.id }, 201)
#         return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)
