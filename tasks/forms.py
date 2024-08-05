from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'description', 'status']

class TaskSubmissionForm(forms.Form):
    file = forms.FileField(label='Upload nucleotide sequence file (FASTA format)')
    use_demo_file = forms.BooleanField(label='Use demo file - Arabidopsis_lyrata.v.1.0.dna.chromosome.8.fa.gz', required=False)
    # vertebrate', 'land_plant', 'fungi', 'invertebrate'
    lineage = forms.ChoiceField(choices=[
        ('land_plant', 'Land plant'),
        ('vertebrate', 'Vertebrates'),
        ('invertebrate', 'Invertebrates'),
        ('fungi', 'Fungi')
    ], label='Select Lineage-specific mode')
    gff_label = forms.CharField(max_length=255, label='Enter label for GFF feature naming')
    email = forms.EmailField(label='Email address')