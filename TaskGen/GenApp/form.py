
from django import forms
from .models import MomFile,Task,CreateMoM

class UploadMoM(forms.ModelForm):
    class Meta:
        model = MomFile
        fields = ('title', 'file',)

class TaskEditForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'position', 'task', 'task_description', 'deadline']

class MoMForm(forms.ModelForm):
    class Meta:
        model = CreateMoM
        fields = ['title', 'date', 'location', 'attendees', 'agenda', 'discussion']

class AddTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'position', 'task', 'task_description', 'deadline']