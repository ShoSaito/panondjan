from django.urls import path
from django.views.generic import TemplateView
from . import views 

urlpatterns = [
    path('', TemplateView.as_view(template_name="panondjan/index.html"), name='panondjan_index'),
    path('demo/', views.DataManage.as_view(), name='panondjan_demo'),
    
]

