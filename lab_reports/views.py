# lab_Reports/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

 
 
from .models import LabTechnician

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from patients.models import Patient
from lab_reports.models import LabReport
from .models import LabTechnician
 