from django.db import models

# Create your models here.
class MomFile(models.Model):
 
    title = models.CharField(max_length = 80)
    file = models.FileField(upload_to='files/')
 
    class Meta:
        ordering = ['title']
     
    def __str__(self):
        return f"{self.title}"

class Task(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    task = models.CharField(max_length=200)
    task_description = models.TextField()
    deadline = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class CreateMoM(models.Model):
    title = models.CharField(max_length=100)
    date = models.CharField(max_length=20)
    location = models.CharField(max_length=100)
    attendees = models.TextField()
    agenda = models.TextField()
    discussion = models.TextField()

    def __str__(self):
        return self.title