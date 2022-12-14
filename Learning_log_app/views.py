from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .models import Topic, Entry
from .forms import TopicForm, EntryForm

# Create your views here.


def index(request):
    """The home page for the learning log app"""
    return render(request, 'index.html')


def homepage(request):
    """Return Parent Homepage"""

    return render(request, 'base.html')


@login_required
def topics(request):
    """Return Topics on the home page"""
    # topics = Topic.objects.order_by("date_added")  # Topic.objects.all
    # Return topics under logged in user
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics': topics}
    return render(request, 'topics.html', context)


@login_required
def topic(request, topic_id):
    """Return single topic details"""
    topic = Topic.objects.get(id=topic_id)
    # Make sure topic belongd to the current user
    if topic.owner != request.user:
        raise Http404
    entries = topic.entry_set.order_by('-date_added')
    context = {'topic': topic, 'entries': entries}
    return render(request, 'topic.html', context)


@login_required
def new_topic(request):
    """Return new form to submit the topic to the data base"""
    if request.method != 'POST':
        # No data submitted, create a blank page.
        form = TopicForm()
    else:
        # POST submitted, process data.
        form = TopicForm(data=request.POST)
        if form.is_valid():
            # Saving user topic
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            # form.save()
            return redirect('Learning_log_app:topics')

    # Display a blank or invalid form
    context = {'form': form}
    return render(request, 'new_topic.html', context)


@login_required
def new_entry(request, topic_id):
    """Adding a new entry form"""
    topic = Topic.objects.get(id=topic_id)
    if request.method != 'POST':
        # No data return empty form with a blank page
        form = EntryForm()
    else:
        # POST request submitted, process data
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return redirect('Learning_log_app:topic', topic_id=topic_id)

    context = {'topic': topic, 'form': form}
    return render(request, 'new_entry.html', context)


@login_required
def edit_entry(request, entry_id):
    """Edit An existing entry value."""
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic

    # Raise 404 error
    if topic.owner != request.user:
        return Http404

    if request.method != "POST":
        # Initial request; pre-fill form wth the current entry
        form = EntryForm(instance=entry)
    else:
        # POST data submitted; process data.
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('Learning_log_app:topic', topic_id=topic.id)
    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, 'edit_entry.html', context)
