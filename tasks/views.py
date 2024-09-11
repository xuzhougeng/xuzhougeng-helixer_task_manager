import subprocess
import os
import uuid
import threading

from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Task
from .forms import TaskForm, TaskSubmissionForm
from .models import Task

def run_annotation_command(file_path, use_demo_file, lineage, gff_label, email, task_id):
    # 构建命令
    gff_filename = f"{uuid.uuid4()}.gff"
    gff_dir = os.path.join(settings.MEDIA_ROOT, 'gff_files')
    os.makedirs(gff_dir, exist_ok=True)
    
    fasta_file_name = os.path.basename(file_path)

    # 使用任务ID创建唯一的容器名称
    container_name = f"helixer_task_{task_id}"

    docker_command = [
        "docker", "run", "--runtime=nvidia", "--rm", 
        "--name", container_name,  # 使用唯一的容器名称
        "--mount", f"type=bind,source={os.getcwd()}/media,target=/home/helixer_user/shared",
        "--mount", f"type=bind,source={os.getcwd()}/Helixer,target=/home/helixer_user/.local/share/Helixer",
        "gglyptodon/helixer-docker:helixer_v0.3.2_cuda_11.8.0-cudnn8",
        "sh", "-c",
        f"Helixer.py --fasta-path /home/helixer_user/shared/uploads/{fasta_file_name} --lineage {lineage} --gff-output-path /home/helixer_user/shared/gff_files/{gff_filename} --batch-size 32 --species {gff_label}"
    ]

    # command = f"annotate --file {file_path} --lineage {lineage} --label {gff_label} --output {gff_filepath}"
    # if use_demo_file:
    #     command += " --use-demo-file"
    #command = f"sleep 5 && touch {gff_filepath}"
    # 执行命令
    result = subprocess.run(docker_command)

    # 更新任务状态
    task = Task.objects.get(id=task_id)
    if result.returncode == 0:
        task.status = 'completed'
        task.gff_file = gff_filename
    else:
        task.status = 'failed'
    task.save()


def task_list(request):
    tasks = Task.objects.all()
    return render(request, 'tasks/task_list.html', {'tasks': tasks})

def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'tasks/task_detail.html', {'task': task, 'MEDIA_URL': settings.MEDIA_URL})

def task_create(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            return redirect('task_detail', pk=task.pk)
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form})

def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            return redirect('task_detail', pk=task.pk)
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_form.html', {'form': form})

def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.delete()
    return redirect('task_list')


from django.db.models import F

def task_submit(request):
    if request.method == "POST":
        # Check if there is any running task
        running_task = Task.objects.filter(status='running').first()
        if running_task:
            # If there is a running task, set the new task to pending
            form = TaskSubmissionForm(request.POST, request.FILES)
            if form.is_valid():
                file = form.cleaned_data['file']
                use_demo_file = form.cleaned_data['use_demo_file']
                lineage = form.cleaned_data['lineage']
                gff_label = form.cleaned_data['gff_label']
                email = form.cleaned_data['email']
                
                task = Task.objects.create(
                    name=file.name,
                    description='',
                    status='pending',
                    file=file,
                    use_demo_file=use_demo_file,
                    lineage=lineage,
                    gff_label=gff_label,
                    email=email
                )
                
                return redirect('task_list')
        else:
            # If no running task, start the new task
            form = TaskSubmissionForm(request.POST, request.FILES)
            if form.is_valid():
                file = form.cleaned_data['file']
                use_demo_file = form.cleaned_data['use_demo_file']
                lineage = form.cleaned_data['lineage']
                gff_label = form.cleaned_data['gff_label']
                email = form.cleaned_data['email']
                
                task = Task.objects.create(
                    name=file.name,
                    description='',
                    status='running',
                    file=file,
                    use_demo_file=use_demo_file,
                    lineage=lineage,
                    gff_label=gff_label,
                    email=email
                )
                
                thread = threading.Thread(target=run_annotation_command, args=(task.file.path, use_demo_file, lineage, gff_label, email, task.id))
                thread.start()
                
                return redirect('task_list')
    else:
        form = TaskSubmissionForm()
    return render(request, 'tasks/task_submit.html', {'form': form})

def running_tasks(request):
    tasks = Task.objects.filter(status='running')
    return render(request, 'tasks/running_tasks.html', {'tasks': tasks})

def start_pending_task():
    pending_task = Task.objects.filter(status='pending').first()
    if pending_task:
        pending_task.status = 'running'
        pending_task.save()
        thread = threading.Thread(target=run_annotation_command, args=(
            pending_task.file.path,
            pending_task.use_demo_file,
            pending_task.lineage,
            pending_task.gff_label,
            pending_task.email,
            pending_task.id
        ))
        thread.start()