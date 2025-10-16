from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Job, Application
from .forms import JobForm, ContactForm

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
    
    # Handle contact form submission for job application
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Get form data
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            
            # Save application to database
            Application.objects.create(
                job=job,
                applicant_name=name,
                applicant_email=email,
                message=message
            )
            
            # Send email to employer
            try:
                send_mail(
                    subject=f'New Application for {job.title}',
                    message=f'You have received a new application from {name} ({email}).\n\nMessage:\n{message}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[job.contact_email],
                    fail_silently=False,
                )
            except Exception as e:
                # Log the error but don't fail the application submission
                print(f"Error sending email: {e}")
            
            # Display success message
            messages.success(request, 'Your application has been submitted successfully!')
            return redirect('job_details', job_id=job.id)
    else:
        form = ContactForm()
    
    return render(request, 'job_detail.html', {'job': job, 'form': form})
