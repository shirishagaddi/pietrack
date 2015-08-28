from django.shortcuts import render, redirect
from piebase.models import Project, Priority, Severity, TicketStatus
from forms import CreateProjectForm, PriorityIssueForm, PriorityIssueFormEdit, SeverityIssueForm, SeverityIssueFormEdit, TicketStatusForm, TicketStatusFormEdit, RoleAddForm
import json
import random
import string
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse
from piebase.models import User, Project, Organization, Role
from forms import CreateProjectForm, CreateMemberForm, PasswordResetForm
from .tasks import send_mail_old_user


@login_required
def create_project(request):
    template_name = 'project/create_project.html'
    if(request.method == "POST"):
        organization = request.user.organization
        form = CreateProjectForm(request.POST, organization=organization)
        if(form.is_valid()):
            slug = slugify(request.POST['name'])
            project_obj = Project.objects.create(name=request.POST['name'], slug=slug, description=request.POST['description'], modified_date=timezone.now(),organization=organization)
            project_obj.members.add(request.user)
            project_obj.save()
            json_data = {'error': False, 'errors': form.errors, 'slug': slug}
            return HttpResponse(json.dumps(json_data), content_type="application/json")
        else:
            return HttpResponse(json.dumps({'error': True, 'errors': form.errors}), content_type="application/json")
    return render(request, template_name)


@login_required
def list_of_projects(request):
    template_name = 'project/projects_list.html'
    projects_list = Project.objects.filter(members__email=request.user)
    dict_items = {'projects_list': projects_list}
    return render(request, template_name, dict_items)


@login_required
def project_detail(request, slug):
    template_name = 'project/project_description.html'
    project_object = Project.objects.filter(slug=slug)
    project_members = project_object[0].members.all()
    dict_items = {'project_object': project_object[
        0], 'project_members': project_members}
    return render(request, template_name, dict_items)

@login_required
def project_details(request, slug):
    project = Project.objects.get(slug=slug)
    dictionary = {'project': project, 'slug': slug}
    template_name = 'project/Project-Project_Details.html'

    if(request.method == 'POST'):
        organization = request.user.organization
        form = CreateProjectForm(request.POST, organization=organization)

        if(form.is_valid()):
            slug = slugify(request.POST['name'])
            project = Project.objects.get(
                slug=request.POST['oldname'], organization=organization)
            project.name = request.POST['name']
            project.slug = slug
            project.modified_date = timezone.now()
            project.save()
            return HttpResponse(json.dumps({'error': False, 'slug': slug}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({'error': True, 'errors': form.errors}), content_type="application/json")

    return render(request, template_name, dictionary)

@login_required
def delete_project(request, id):
    Project.objects.get(id=id).delete()
    return redirect("project:list_of_projects")

@login_required
def issues_priorities(request, slug):
    template_name = 'settings/priorities.html'
    if(request.method == 'POST'):
        form = PriorityIssueForm(request.POST, project=slug)
        if(form.is_valid()):
            project = Priority.objects.create(name=request.POST['name'], color=request.POST[
                                              'color'], project=Project.objects.get(slug=slug))
            return HttpResponse(json.dumps({'error': False, 'color': request.POST['color'], 'name': request.POST['name'], 'proj_id': project.id}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({'error': True, 'errors': form.errors}), content_type="application/json")
    priority_list = Priority.objects.filter(
        project=Project.objects.get(slug=slug))
    return render(request, template_name, {'slug': slug, 'priority_list': priority_list})

@login_required
def issues_priorities_edit(request, slug):
    if(request.method == 'POST'):
        form = PriorityIssueFormEdit(request.POST)
        if(form.is_valid()):
            priority = Priority.objects.get(
                id=request.POST['old_id'], project=Project.objects.get(slug=slug))
            priority.color = request.POST['color']
            priority.name = request.POST['name']
            priority.save()
            return HttpResponse(json.dumps({'error': False, 'color': request.POST['color'], 'name': request.POST['name'], 'id': request.POST['old_id']}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({'error': True, 'errors': form.errors}), content_type="application/json")

@login_required
def issues_priorities_delete(request, slug):
    Priority.objects.get(name=request.POST['name'], color=request.POST[
                         'color'], project=Project.objects.get(slug=slug)).delete()
    return HttpResponse(json.dumps({'error': False}), content_type="application/json")

@login_required
def issues_severities(request, slug):
    template_name = 'settings/severities.html'
    if(request.method == 'POST'):
        form = SeverityIssueForm(request.POST, project=slug)
        if(form.is_valid()):
            project = Severity.objects.create(name=request.POST['name'], color=request.POST[
                                              'color'], project=Project.objects.get(slug=slug))
            return HttpResponse(json.dumps({'error': False, 'color': request.POST['color'], 'name': request.POST['name'], 'proj_id': project.id}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({'error': True, 'errors': form.errors}), content_type="application/json")
    severity_list = Severity.objects.filter(
        project=Project.objects.get(slug=slug))
    return render(request, template_name, {'slug': slug, 'severity_list': severity_list})

@login_required
def issues_severity_edit(request, slug):
    if(request.method == 'POST'):
        form = SeverityIssueFormEdit(request.POST)
        if(form.is_valid()):
            priority = Severity.objects.get(
                id=request.POST['old_id'], project=Project.objects.get(slug=slug))
            priority.color = request.POST['color']
            priority.name = request.POST['name']
            priority.save()
            return HttpResponse(json.dumps({'error': False, 'color': request.POST['color'], 'name': request.POST['name'], 'id': request.POST['old_id']}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({'error': True, 'errors': form.errors}), content_type="application/json")

@login_required
def issues_severity_delete(request, slug):
    Severity.objects.get(id=request.POST['id'], project=Project.objects.get(slug=slug)).delete()
    return HttpResponse(json.dumps({'error': False}), content_type="application/json")

@login_required
def ticket_status(request, slug):
    template_name = 'settings/ticket_status.html'
    if(request.method == 'POST'):
        form = TicketStatusForm(request.POST, project=slug)
        if(form.is_valid()):
            tslug = slugify(request.POST['name'])
            project = TicketStatus.objects.create(name=request.POST[
                                                  'name'], slug=tslug, color=request.POST['color'], project=Project.objects.get(slug=slug))
            return HttpResponse(json.dumps({'error': False, 'color': request.POST['color'], 'name': request.POST['name'], 'proj_id': project.id}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({'error': True, 'errors': form.errors}), content_type="application/json")
    tstatus_list = TicketStatus.objects.filter(
        project=Project.objects.get(slug=slug))
    return render(request, template_name, {'slug': slug, 'tstatus_list': tstatus_list})

@login_required
def ticket_status_edit(request, slug):
    if(request.method == 'POST'):
        form = TicketStatusFormEdit(request.POST)
        if(form.is_valid()):
            tstatus = TicketStatus.objects.get(
                id=request.POST['old_id'], project=Project.objects.get(slug=slug))
            tstatus.color = request.POST['color']
            tstatus.name = request.POST['name']
            tstatus.slug = slugify(request.POST['name'])
            tstatus.save()
            return HttpResponse(json.dumps({'error': False, 'color': request.POST['color'], 'name': request.POST['name'], 'id': request.POST['old_id']}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({'error': True, 'errors': form.errors}), content_type="application/json")

@login_required
def ticket_status_delete(request, slug):
    TicketStatus.objects.get(name=request.POST['name'], color=request.POST[
                             'color'], project=Project.objects.get(slug=slug)).delete()
    return HttpResponse(json.dumps({'error': False}), content_type="application/json")


def password_reset(request, to_email):
    from_email = 'dineshmcmf@gmail.com'
    to_email_dict = {'email': to_email}
    token_generator = default_token_generator
    email_template_name = 'email/reset_email.html'
    subject_template_name = 'email/reset_subject.txt'
    form = PasswordResetForm(to_email_dict)
    if form.is_valid():
        opts = {
            'use_https': request.is_secure(),
            'from_email': from_email,
            'email_template_name': email_template_name,
            'subject_template_name': subject_template_name,
            'request': request}
        form.save(**opts)

@login_required
def project_team(request, slug):
    template_name = 'settings/team.html'
    project = Project.objects.get(slug=slug)
    mem_details = []
    for member in project.members.exclude(email=request.user.email):
        mem_details.append(
            (member, Role.objects.get(users__email=member.email)))
    dictionary = {'project_id': project.id,
                  'mem_details': mem_details, 'slug': slug}
    return render(request, template_name, dictionary)



@login_required
def create_member(request, slug):
    if request.method == 'POST':
        error_count = 0
        json_data = {}
        json_post_index = 0
        email_list = request.POST.getlist('email')
        designation_list = request.POST.getlist('designation')
        description = request.POST.get('description')
        post_dict = {'description': description}
        post_tuple = zip(email_list, designation_list)
        for email_iter, designation_iter in post_tuple:
            post_dict['email'] = email_iter
            post_dict['designation'] = designation_iter
            create_member_form = CreateMemberForm(post_dict)
            if create_member_form.is_valid():
                email = post_dict['email']
                designation = post_dict['designation']
                description = post_dict['description']
                organization_obj = request.user.organization
                if User.objects.filter(email=email).exists():
                    send_mail_old_user.delay(email)
                    pass
                else:
                    random_password = ''.join(
                        random.choice(string.digits) for _ in xrange(8))
                    new_user_obj = User.objects.create_user(
                        email=email, username=email, password=random_password, organization=organization_obj, pietrack_role='user')
                    password_reset(request, email_iter)
                project_obj = Project.objects.get(slug=slug)
                user_obj = User.objects.get(email=email)
                project_obj.members.add(user_obj)
                project_obj.organization = organization_obj
                project_obj.save()

                random_slug = ''.join(random.choice(string.ascii_letters + string.digits) for _ in xrange(10))
                role_obj = Role.objects.create(name = designation, slug = random_slug, project = project_obj)
                role_obj.users.add(user_obj)
                role_obj.save()
            else:
                error_count += 1
            json_data[json_post_index] = create_member_form.errors
            json_post_index += 1
        if error_count == 0:
            json_data['error'] = False
        else:
            json_data['error'] = True
        return HttpResponse(json.dumps(json_data), content_type='application/json')
    else:
        return render(request, 'settings/create_member.html')

@login_required
def manage_role(request, slug):
    template_name = 'settings/member_roles.html'

    project = Project.objects.get(slug=slug)
    if request.POST:
        form = RoleAddForm(request.POST, project=slug)
        if(form.is_valid()):
            role = Role.objects.create(
                name=request.POST['name'], slug=slugify(request.POST['name']), project=project)
            return HttpResponse(json.dumps({'error': False, 'role_id': role.id, 'role_name': role.name}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({'error': True, 'errors': form.errors}), content_type="application/json")
    list_of_roles = Role.objects.filter(project=project)
    dictionary = {'list_of_roles': list_of_roles, 'slug': slug}
    return render(request, template_name, dictionary)


@login_required
def manage_role_edit(request, slug):
    project = Project.objects.get(slug=slug)
    form = RoleAddForm(request.POST, project=slug)
    if(form.is_valid()):
        role = Role.objects.get(id=request.POST['role_id'], project=project)
        role.name = request.POST['name']
        role.slug = slugify(request.POST['name'])
        role.save()
        return HttpResponse(json.dumps({'error': False, 'role_id': role.id, 'role_name': role.name}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'error': True, 'errors': form.errors}), content_type="application/json")


@login_required
def manage_role_delete(request, slug):
    project = Project.objects.get(slug=slug)
    Role.objects.get(id=request.GET['role_id'], project=project).delete()
    return HttpResponse(json.dumps({'error': False}), content_type="application/json")

