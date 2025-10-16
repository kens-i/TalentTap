from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Job
from .forms import JobForm

# Create your views here.


def index(request):
    return HttpResponse("Hello, World!")

def job_list(request):
    if request.user.is_authenticated:
        jobs = Job.objects.all()
        return render(request, 'job_list.html', {'jobs': jobs})
    else:
        return HttpResponse('You must be logged in to view job listings.', status=403)

def create_job(request):
    if not request.user.is_authenticated:
        return HttpResponse('You must be logged in to create a job.', status=403)
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.owner = request.user
            job.status = 'OPEN'
            job.save()
            return HttpResponse('Job created successfully!')
    else:
        form = JobForm()
    return render(request, 'home/create_job.html', {'form': form})

def job_detail(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    return render(request, 'job_detail.html', {'job': job})
