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

class MateriasAll(generics.CreateAPIView):
    #Esta linea se usa para pedir el token de autenticación de inicio de sesión
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        materias = Materias.objects.all()
        lista = MateriaSerializer(materias, many=True).data

        return Response(lista, 200)

class MateriasStats(generics.CreateAPIView):
    #Esta linea se usa para pedir el token de autenticación de inicio de sesión
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        query = request.GET.get("countBy")
        if query == "days":
            materias = Materias.objects.all()
            dias = {}
            for materia in materias:
                for dia in materia.dias:
                    if dia in dias:
                        dias[dia] += 1
                    else:
                        dias[dia] = 1
            return Response(dias, 200)
        if query == "teachers":
            # COUNT HOW MANY MATERIAS EACH TEACHER TEACH EACH MATERIA
            teachers = Profesores.objects.all()
            teachers = ProfesorSerializer(teachers, many=True).data
            materiasCounter = {}
            for teacher in teachers:
                # teacher is a OrderedDict
                teacher = dict(teacher)
                for materia in teacher['materias']:
                    if materia in materiasCounter:
                        materiasCounter[materia] += 1
                    else:
                        materiasCounter[materia] = 1
            return Response(materiasCounter, 200)


class MateriasView(generics.CreateAPIView):
    def get(self, request, *args, **kwargs):
        materia = get_object_or_404(Materias, id = request.GET.get("id"))
        materia = MateriaSerializer(materia, many=False).data

        return Response(materia, 200)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        materia = MateriaSerializer(data=request.data)
        if not materia.is_valid():
            print(request.data['horario'])
            print(materia.errors)
            return Response(materia.errors, status=status.HTTP_400_BAD_REQUEST)
        materia_for_save = Materias.objects.create(
            nrc = request.data['nrc'],
            nombre = request.data['nombre'],
            seccion=request.data['seccion'],
             horario=request.data['horario'],
             programa_educativo=request.data['programaEducativo'],
             salon=request.data['salon'],
             dias=request.data['dias'],
        )
        materia_for_save.save()
        return Response({"materia_created_id": materia_for_save.id }, 201)

    def put(self, request, *args, **kwargs): 
        materia = get_object_or_404(Materias, id=request.GET.get("id"))
        materia.nrc = request.data["nrc"]
        materia.nombre = request.data["nombre"]
        materia.seccion = request.data["seccion"]
        materia.horario = request.data["horario"]
        materia.programa_educativo = request.data["programaEducativo"]
        materia.salon = request.data["salon"]
        materia.dias = request.data["dias"]
        materia.save()
        materia = MateriaSerializer(materia, many=False).data

        return Response(materia, 200)

    def delete(self, request, *args, **kwargs):
        materia = get_object_or_404(Materias, id=request.GET.get("id"))
        try:
            materia.delete()
            return Response({"details":"Materia eliminada"},200)
        except Exception as e:
            return Response({"details":"Algo pasó al eliminar"},400)

