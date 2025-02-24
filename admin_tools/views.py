from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

# Create your views here.

@staff_member_required
def home(request):
    return render(request, 'admin_tools/home.html')

@staff_member_required
def user_list(request):
    return render(request, 'admin_tools/user_list.html')

@staff_member_required
def user_add(request):
    return render(request, 'admin_tools/user_form.html')

@staff_member_required
def user_detail(request, pk):
    return render(request, 'admin_tools/user_detail.html')

@staff_member_required
def user_edit(request, pk):
    return render(request, 'admin_tools/user_form.html')

@staff_member_required
def audit_logs(request):
    return render(request, 'admin_tools/audit_logs.html')

@staff_member_required
def system_settings(request):
    return render(request, 'admin_tools/system_settings.html')

@staff_member_required
def quickbooks_settings(request):
    return render(request, 'admin_tools/quickbooks_settings.html')
