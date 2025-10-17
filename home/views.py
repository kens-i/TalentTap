from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Job, Application
from .forms import JobForm, ContactForm

# Create your views here.

def index(request):
    # Redirect to the named job_list URL (keeps the job_list view's auth checks)
    return redirect('job_list')

def job_list(request):
    if request.user.is_authenticated:
        jobs = Job.objects.all()
        return render(request, 'job_list.html', {'jobs': jobs})
    else:
        return HttpResponse('You must be logged in to view job listings.', status=403)

def job_detail(request, job_id):
    """
    Show job details and handle the contact/application form submission.
    On POST: validate ContactForm, create Application, optionally send email,
    flash a success message and redirect back to this detail page.
    """
    job = get_object_or_404(Job, pk=job_id)

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            Application.objects.create(
                job=job,
                applicant_name=name,
                applicant_email=email,
                message=message
            )

            # Try to send an email to the job contact (don't fail the request on email error)
            try:
                send_mail(
                    subject=f'New Application for {job.title}',
                    message=f'You have received a new application from {name} ({email}).\n\nMessage:\n{message}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[job.contact_email],
                    fail_silently=False,
                )
            except Exception as e:
                # Log the error (print for now) but continue
                print(f"Error sending email: {e}")

            messages.success(request, 'Your application has been submitted successfully!')
            return redirect('job_detail', job_id=job.id)
    else:
        form = ContactForm()

    return render(request, 'job_detail.html', {'job': job, 'form': form})

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