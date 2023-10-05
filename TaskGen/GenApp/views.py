from django.shortcuts import render,redirect,get_object_or_404
from  django.http import  HttpResponse
from django.core.files.storage import FileSystemStorage  
from .form import UploadMoM,TaskEditForm,MoMForm,AddTaskForm
from .models import Task,CreateMoM,MomFile
import PyPDF2
import openai
import os
import tiktoken
import pandas as pd
import re
import docx

# setup openAi

key = ''

os.environ["OPENAI_API_KEY"] = key

openai.api_key = os.getenv("OPENAI_API_KEY")


# global variables
text = ""

# read text from pdf


def extract_text_from_pdf(pdf_path):
    
    text = ""
    
    with open(pdf_path, "rb") as pdf_file:
        
        # creating a pdf reader object
        pdfReader = PyPDF2.PdfReader(pdf_file)
        
        for page in range(len(pdfReader.pages)):
            
            # creating a page object
            pageObj = pdfReader.pages[page]
            
            # extracting text from page
            text += pageObj.extract_text()
    
    return text

# count the number of tokens

def number_of_tokens(text):
    
    encoding = tiktoken.encoding_for_model("davinci")
    token_count = len(encoding.encode(text))
    
    return token_count
    

# generate reply using GenAi (gpt 3.5 turbo)
def reply_generation(text):

    messages = [ {"role": "system", "content": 
                  "You are a intelligent assistant."} ]
    prompt = f"""
    Create a table with the following headings: Name, Position,Task, Task Description,  Deadline.

    {text} .  generate task descriptions that are clear and contextually
    relevant based on the information within the meeting minutes.

    """
    messages.append(
                {"role": "user", "content":prompt },
            )

    chat = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=messages
            )
    reply = (chat["choices"][0]["message"]["content"])
    messages.append({"role": "assistant", "content": reply})

    prompt = f"""

    remove rows for person dont have any task  


    """
    messages.append({"role": "user", "content": prompt})

    chat = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=messages
            )
    reply = (chat["choices"][0]["message"]["content"])
    messages.append({"role": "assistant", "content": reply})

    prompt = f"""

    If any column is empty, please fill it with "Null." Exclude any other text or responses not related to tables.


    """
    messages.append({"role": "user", "content": prompt})

    chat = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=messages
            )
    reply = (chat["choices"][0]["message"]["content"])
    
    return reply


# create table content from reply

def create_table(reply):

    lines = reply.splitlines()
    actual = []
    for line in lines:
        if bool(re.search(r'/|', line)):

            if '| ' in line :

                if '|-' in line:
                    continue

                if '| Name' in line:
                    actual.append([word.strip() for word in line.strip('|').split('|')])

                elif '|   ' in line:

                    actual.append([word.strip() for word in line.replace('|    ','| Null').strip('|').split('|')])

                elif '| ' in line:
                    actual.append([word.strip() for word in line.strip('|').split('|')])




    table = {key:[] for key in actual[0]}
    for values in actual[1:]:

        for key,value in zip(table.keys(),values):
            table[key].append(value)
            
    return table






# Create your views here.



def main(request):

    CreateMoM.objects.all().delete()
    # Delete all existing tasks from the Task model
    Task.objects.all().delete()

    MomFile.objects.all().delete()

    return render(request,'main.html')

def table(request):
    # Retrieve all tasks from the Task model
    tasks = Task.objects.all()

    # Pass the tasks as a context variable to the template
    return render(request, 'table.html', {'tasks': tasks})






def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        form = TaskEditForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            tasks = Task.objects.all()
            return render(request, 'table.html', {'tasks': tasks})  # Redirect to the table page after editing
    else:
        form = TaskEditForm(instance=task)
    return render(request, 'edit_task.html', {'form': form, 'task': task})

    
def download_excel(request):
    tasks = Task.objects.all()

    # Create a Pandas DataFrame with your task data
    data = {
        'Name': [task.name for task in tasks],
        'Position': [task.position for task in tasks],
        'Task': [task.task for task in tasks],
        'Task Description': [task.task_description for task in tasks],
        'Deadline': [task.deadline for task in tasks],
    }
    df = pd.DataFrame(data)

    # Create an Excel writer object and write the DataFrame to it
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="tasks.xlsx"'
    df.to_excel(response, index=False)

    return response



def regenerate_tasks(request):
    global text
    # Delete all existing tasks from the Task model
    Task.objects.all().delete()
    tokens = number_of_tokens(text)

    if tokens <3500:

        reply = reply_generation(text)
        table = create_table(reply)

        for row_idx in range(len([*table.values()][0])):

            task = Task(

            name=table[[*table.keys()][0]][row_idx],
            position=table[[*table.keys()][1]][row_idx],
            task=table[[*table.keys()][2]][row_idx],
            task_description=table[[*table.keys()][3]][row_idx],
            deadline=table[[*table.keys()][4]][row_idx]
            )
            task.save()
    tasks = Task.objects.all()
    return render(request, 'table.html', {'tasks': tasks})




def create_mom(request):

    global text

    if request.method == 'POST':
        form = MoMForm(request.POST)
        if form.is_valid():
            form.save()

            # Retrieve the first MoM record
            first_mom = CreateMoM.objects.first()

            text = f'title:\n{first_mom.title}\ndate:{first_mom.date}\nlocation:\n{first_mom.location}\nattendees:\n{first_mom.attendees}\nagenda:\n{first_mom.agenda}\ndiscussion:\n{first_mom.discussion}'
            tokens = number_of_tokens(text)

            if tokens <3500:

                reply = reply_generation(text)
                table = create_table(reply)

                for row_idx in range(len([*table.values()][0])):

                    task = Task(

                    name=table[[*table.keys()][0]][row_idx],
                    position=table[[*table.keys()][1]][row_idx],
                    task=table[[*table.keys()][2]][row_idx],
                    task_description=table[[*table.keys()][3]][row_idx],
                    deadline=table[[*table.keys()][4]][row_idx]


                    )

                    task.save()
            

            tasks = Task.objects.all()
            return render(request, 'table.html', {'tasks': tasks})
            


            return redirect('mom_list')  # Redirect to a list view or another page
    else:
        form = MoMForm()
    
    context = {'form': form}
    return render(request, 'create_MoM.html', context)



def add_task(request):
    if request.method == 'POST':
        form = AddTaskForm(request.POST)
        if form.is_valid():
            # Save the new Task instance to the database
            form.save()
            tasks = Task.objects.all()
            return render(request, 'table.html', {'tasks': tasks})  # Redirect to your table page after adding
    else:
        form = AddTaskForm()

    context = {'form': form}
    return render(request, 'add_task_form.html', context)


def create_instruction():

    tasks = Task.objects.all()

    messages = [ {"role": "system", "content": 
                    "You are a intelligent assistant."} ]

    promit = """

    give a enviromental set for creating a web development, by uing visual studio code


    """

    messages.append({
        
        'role' : 'assistant', 'content': promit
    })
    reply = openai.ChatCompletion.create(model="gpt-3.5-turbo",messages=messages)

    return reply['choices'][0]['message']['content']



def instruction_page(request):

    paragraph =  create_instruction()



    return render(request,'instruction_page.html',{'instruction':paragraph})


def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    task.delete()
    tasks = Task.objects.all()
    return render(request, 'table.html', {'tasks': tasks})


def extract_text_from_docx(file_path):

    doc = docx.Document(file_path)

    text = ""

    for paragraph in doc.paragraphs:
        text += paragraph.text + '\n'

    return text

def upload_file(request):

    global text


    if request.method == 'POST':
        form = UploadMoM(request.POST, request.FILES)
        if form.is_valid():
            
            form.save()
            file = form.cleaned_data['file']
            print(file)
            ext = f'{str(file)}'.split('.')[1]

            file_path = os.path.join('media', 'files', str(file))

            if ext == 'pdf':
                text = extract_text_from_pdf(file_path)

            elif ext == 'txt':

                with open(file_path, 'r') as txt:

                    text = txt.read()
            
            elif ext == 'docx':

                text = extract_text_from_docx(file_path)
            
            else :

                form = UploadMoM()
                context = {
                    'form':form,
                   }
                return render(request, 'upload.html', context)

            tokens = number_of_tokens(text)
            
            if tokens <3200:

                reply = reply_generation(text)
                table = create_table(reply)


                for row_idx in range(len([*table.values()][0])):

                    task = Task(

                    name=table[[*table.keys()][0]][row_idx],
                    position=table[[*table.keys()][1]][row_idx],
                    task=table[[*table.keys()][2]][row_idx],
                    task_description=table[[*table.keys()][3]][row_idx],
                    deadline=table[[*table.keys()][4]][row_idx]


                    )

                    task.save()
            

                tasks = Task.objects.all()
                return render(request, 'table.html', {'tasks': tasks})

            else :

                form = UploadMoM()
                context = {
                    'form':form,
                   }
                return render(request, 'upload.html', context)
    else:
        form = UploadMoM()
        context = {
                    'form':form,
                   }
    return render(request, 'upload.html', context)
