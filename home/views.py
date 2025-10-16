from django.shortcuts import render, get_object_or_404, redirect
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
    
def job_detail(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    return render(request, 'job_detail.html', {'job': job})


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


def edit_job(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    if not request.user.is_authenticated:
        return HttpResponse('You must be logged in to edit a job.', status=403)
    if job.owner != request.user:
        return HttpResponse('You do not have permission to edit this job.', status=403)
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            return redirect('job_detail', job_id=job.id)
    else:
        form = JobForm(instance=job)
    return render(request, 'home/edit_job.html', {'form': form, 'job': job})


def delete_job(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    if not request.user.is_authenticated:
        return HttpResponse('You must be logged in to delete a job.', status=403)
    if job.owner != request.user:
        return HttpResponse('You do not have permission to delete this job.', status=403)
    if request.method == 'POST':
        job.delete()
        return redirect('job_list')
    return render(request, 'home/delete_job.html', {'job': job})
