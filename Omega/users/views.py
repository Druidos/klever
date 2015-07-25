import pytz
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.forms import ValidationError
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.utils.translation import activate
from users.forms import UserExtendedForm, UserForm, EditUserForm
from Omega.vars import LANGUAGES
from django.shortcuts import get_object_or_404
from jobs.job_functions import JobAccess
from django.template import Template, RequestContext


def user_signin(request):
    activate(request.LANGUAGE_CODE)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('jobs:tree'))
            else:
                login_error = _("Account has been disabled")
        else:
            login_error = _("Incorrect username or password")
        return render(request, 'users/login.html',
                      {'login_errors': login_error})
    else:
        return render(request, 'users/login.html')


def user_signout(request):
    logout(request)
    return HttpResponseRedirect(reverse('users:login'))


def register(request):
    activate(request.LANGUAGE_CODE)

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserExtendedForm(data=request.POST)
        user_tz = request.POST.get('timezone', None)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            profile = profile_form.save(commit=False)
            profile.user = user
            if user_tz:
                profile.timezone = user_tz
            try:
                profile.save()
            except:
                raise ValidationError("Can't save user to the database!")
            user.save()
            return HttpResponseRedirect(reverse('users:login'))
    else:
        user_form = UserForm()
        profile_form = UserExtendedForm()

    return render(request, 'users/register.html',
                  {
                      'user_form': user_form,
                      'profile_form': profile_form,
                      'timezones': pytz.common_timezones,
                  })


@login_required
def edit_profile(request):
    activate(request.user.extended.language)

    if request.method == 'POST':
        user_form = EditUserForm(data=request.POST, request=request,
                                 instance=request.user)
        profile_form = UserExtendedForm(
            data=request.POST,
            instance=request.user.extended
        )
        user_tz = request.POST.get('timezone')
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            new_pass = request.POST.get('new_password')
            do_redirect = False
            if len(new_pass):
                user.set_password(new_pass)
                do_redirect = True
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            if user_tz:
                profile.timezone = user_tz
            profile.save()

            if do_redirect:
                return HttpResponseRedirect(reverse('users:login'))
            else:
                return HttpResponseRedirect(reverse('users:edit_profile'))
    else:
        user_form = EditUserForm(instance=request.user)
        profile_form = UserExtendedForm(instance=request.user.extended)

    return render(
        request,
        'users/edit-profile.html',
        {
            'user_form': user_form,
            'profile_form': profile_form,
            'timezones': pytz.common_timezones,
            'LANGUAGES': LANGUAGES
        })


def index_page(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('jobs:tree'))
    return HttpResponseRedirect(reverse('users:login'))


@login_required
def show_profile(request, user_id=None):
    activate(request.user.extended.language)
    if len(user_id) == 0:
        return HttpResponseRedirect(reverse('jobs:tree'))
    target = get_object_or_404(User, pk=int(user_id))
    user_activity = target.jobhistory.all().order_by('-change_date')[:18]
    activity = []
    for act in user_activity:
        act_comment = act.comment
        small_comment = act_comment
        if len(act_comment) > 47:
            small_comment = act_comment[:50] + '...'
        new_act = {
            'date': act.change_date,
            'comment': act_comment,
            'small_comment': small_comment,
            'version': act.version,
            'job_name': act.name
        }
        if JobAccess(request.user, act.job).can_view():
            new_act['href'] = reverse('jobs:job', args=[act.job_id])
        activity.append(new_act)
    user_tz = request.user.extended.timezone
    return render(request, 'users/showProfile.html', {
        'target': target,
        'activity': activity,
        'user_tz': user_tz
    })


def psi_signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                template = Template('')
                return HttpResponse(
                    template.render(RequestContext(request, {}))
                )
            else:
                return JsonResponse({'error': 306})
        return JsonResponse({'error': 307})
    return JsonResponse({'error': 500})


def psi_signout(request):
    if not request.user.is_authenticated():
        return JsonResponse({'error': 305})
    logout(request)
    return JsonResponse({'error': 0})