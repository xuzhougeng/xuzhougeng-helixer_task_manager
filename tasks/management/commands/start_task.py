from django.core.management.base import BaseCommand
from tasks.models import Task
from tasks.views import run_annotation_command
import threading

class Command(BaseCommand):
    help = 'Starts a pending task if no task is currently running'

    def handle(self, *args, **options):
        running_task = Task.objects.filter(status='running').first()
        if not running_task:
            pending_task = Task.objects.filter(status='pending').first()
            if pending_task:
                pending_task.status = 'running'
                pending_task.save()
                self.stdout.write(self.style.SUCCESS(f'Starting task {pending_task.id}'))
                thread = threading.Thread(target=run_annotation_command, args=(
                    pending_task.file.path,
                    pending_task.use_demo_file,
                    pending_task.lineage,
                    pending_task.gff_label,
                    pending_task.email,
                    pending_task.id
                ))
                thread.start()
            else:
                self.stdout.write(self.style.WARNING('No pending tasks found'))
        else:
            self.stdout.write(self.style.WARNING(f'Task {running_task.id} is already running'))