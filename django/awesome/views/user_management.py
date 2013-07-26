import logging

from awesome.models import Organization, Branch
from awesome.forms import UserRegForm, BranchForm, OrganizationFormRegistration

from django.http import  HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.core.context_processors import csrf
from django.contrib import auth

logger = logging.getLogger(__name__)

try:
    from awesome.local_settings import *
except ImportError, e:
    logger.error('Unable to load local_settings.py:', e)


def process_register(request):
    """Register a new user"""
    c = {}
    c.update(csrf(request))

    if request.method == 'POST':

        reg_key = request.POST.get('reg_key', '')
        
        # We only want folks we know and trust with our key to create new AB accounts
        if not reg_key or reg_key != INTERNAL['REG_KEY']:
            return HttpResponseRedirect(reverse('landing'))
        
        
        user_reg_form = UserRegForm(request.POST, prefix = "a")
        org_form = OrganizationFormRegistration(request.POST, prefix = "b")
        branch_form = BranchForm(request.POST, prefix = "c")
        
        if user_reg_form.is_valid() and org_form.is_valid() and branch_form.is_valid():
            new_user = user_reg_form.save()
            new_org = org_form.save(commit=False)
            new_branch = branch_form.save(commit=False)
        
            new_org.user = new_user
            new_org.save()
            
            new_branch.organization = new_org
            new_branch.save()

            new_user.backend='django.contrib.auth.backends.ModelBackend'
            auth.login(request, new_user)
            
            return HttpResponseRedirect(reverse('landing'))
        
        else:
            c.update({'user_reg_form': user_reg_form,
                      'org_form': org_form,
                      'branch_form': branch_form})
                      
            return render_to_response('register.html', c)
    else:
        user_reg_form = UserRegForm(prefix = "a")
        org_form = OrganizationFormRegistration(prefix = "b")
        branch_form = BranchForm(prefix = "c")
        
        c.update({'user_reg_form': user_reg_form,
                  'org_form': org_form,
                  'branch_form': branch_form})
        return render_to_response("register.html", c)