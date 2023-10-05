from django.urls import path
from . import  views

urlpatterns = [
    path('',views.main,name='main_page'),
    path('upload/', views.upload_file, name='upload_page'),
    path('table/', views.table, name='table_page'),
    path('edit_task/<int:task_id>/', views.edit_task, name='edit_task'),
    path('download-excel/', views.download_excel, name='download_excel'),
    path('regenerate/', views.regenerate_tasks, name='regenerate_tasks'),
    path('create/', views.create_mom, name='create_mom'),
    path('add_task/', views.add_task, name='add_task'),
    path('delete_task/<int:task_id>/', views.delete_task, name='delete_task'),
    path('instruction_page/', views.instruction_page, name='instruction_page'),


    





]