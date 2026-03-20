from django.shortcuts import render
from django.contrib.auth.decorators import login_required



def presentation_view(request):
    return render(request, 'wqmap/presentation.html')
