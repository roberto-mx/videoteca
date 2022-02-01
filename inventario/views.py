from django.http import HttpResponseRedirect

from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.views import generic

from .forms import Login

from .models import MaestroCintas

class AdminLogin(LoginView):
    template_name = 'login.html'

class Inventario(generic.ListView):
    #template_name = 'inventario.html'
    context_object_name = 'mcintas_list'

    def get_queryset(self):
        """Return material videograbado."""
        return MaestroCintas.objects.all()[:10]

def login(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = Login(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = Login()

    return render(request, 'name.html', {'form': form})