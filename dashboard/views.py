from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings




def dashboard_home(request):
        return render(request, 'dashboard/partials/content_dashboard.html')
