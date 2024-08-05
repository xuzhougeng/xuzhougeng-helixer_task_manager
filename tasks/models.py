from django.db import models

class Task(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ])
    file = models.FileField(upload_to='uploads/', blank=True, null=True)
    use_demo_file = models.BooleanField(default=False)
    lineage = models.CharField(max_length=50, choices=[
        ('land_plants', 'Land plant'),
        ('vertebrates', 'Vertebrates'),
        ('invertebrates', 'Invertebrates'),
        ('fungi', 'Fungi')
    ])
    gff_label = models.CharField(max_length=255, default='default_label')
    email = models.EmailField()
    gff_file = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name
