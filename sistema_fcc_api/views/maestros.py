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
            role = 'maestro'
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

            group, created = Group.objects.get_or_create(name=role)
            group.user_set.add(user)
            user.save()

            teacher = Profesores.objects.create(user=user,
                                                clave_profesor = request.data['clave_profesor'],
                                                fecha_nacimiento = request.data['fecha_nacimiento'],
                                                cubiculo = request.data['cubiculo'],
                                                area_investigacion = request.data['area_investigacion'],
                                                materias = request.data['materias'],
                                                rfc = request.data['rfc'],
                                                edad = request.data['edad'],
                                                telefono = request.data['telefono']
                                            )
            teacher.save()
            return Response({"teacher_created_id": teacher.id }, 201)
        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)
        
#Se tiene que modificar la parte de edicion y eliminar
class MaestrosViewEdit(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def put(self, request, *args, **kwargs):
        # iduser=request.data["id"]
        print(request.data)
        maestro = get_object_or_404(Profesores, id=request.data["id"])
        maestro.clave_profesor = request.data["clave_profesor"]
        maestro.fecha_nacimiento = request.data["fecha_nacimiento"]
        maestro.telefono = request.data["telefono"]
        maestro.rfc = request.data["rfc"]
        maestro.cubiculo = request.data["cubiculo"]
        maestro.area_investigacion = request.data["area_investigacion"]
        maestro.materias = request.data["materias"]
        maestro.edad = request.data["edad"]
        maestro.save()
        temp = maestro.user
        temp.first_name = request.data["first_name"]
        temp.last_name = request.data["last_name"]
        temp.save()
        user = ProfesorSerializer(maestro, many=False).data

        return Response(user,200)
    
    def delete(self, request, *args, **kwargs):
        maestro = get_object_or_404(Profesores, id=request.GET.get("id"))
        try:
            maestro.user.delete()
            return Response({"details":"Maestro eliminado"},200)
        except Exception as e:
            return Response({"details":"Algo pasó al eliminar"},400)
