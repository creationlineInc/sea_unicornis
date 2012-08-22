# -*- coding: utf-8 -*-
import colander
from deform.widget import HiddenWidget
from deform.widget import PasswordWidget
from deform.widget import TextAreaWidget
from deform.widget import TextInputWidget
from deform.widget import SelectWidget
from kotti.events import notify
from kotti.message import email_set_password
from kotti.security import get_principals
from kotti.resources import Content
from kotti.views.edit import generic_edit
from kotti.views.edit import generic_add
from kotti.views.users import UserAddFormView
from kotti.views.users import user_schema
from kotti.views.util import ensure_view_selector
from kotti.views.util import template_api
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from sqlalchemy import asc
from sqlalchemy import desc

from kotti_mapreduce.resources import Bootstrap
from kotti_mapreduce.resources import EMRJobResource
from kotti_mapreduce.resources import JobContainer
from kotti_mapreduce.resources import JobFlow
from kotti_mapreduce.resources import JobService
from kotti_mapreduce.resources import JobStep

from sea_unicornis import _
from sea_unicornis.events import UserAdded
from sea_unicornis.utils import get_home_url


_RESOURCE_VERSIONS = {
    'ami': '2.2',
    'hadoop': '1.0.3',
    'hive': '0.8.1.3',
}

del Content.type_info.edit_links[1]  # disable share operation
JobContainer.type_info.edit_links = []  # disable edit operation


from kotti_mapreduce.views import _SUPPORT_INSTANCE_TYPE

class ContentSchema(colander.MappingSchema):
    title = colander.SchemaNode(
        colander.String(),
        title=_(u'Title'),
    )

class EMRJobResourceSchema(ContentSchema):
    aws_access_key_id = colander.SchemaNode(
        colander.String(),
        title=_(u'AWS access key ID'),
        description=_(u'AWS access key ID to use AWS API.'),
    )
    aws_secret_access_key = colander.SchemaNode(
        colander.String(),
        title=_(u'AWS secret access key'),
        description=_(u'AWS secret access key to use AWS API.'),
        widget=PasswordWidget(),
    )
    region = colander.SchemaNode(
        colander.String(),
        title=_(u'AWS region'),
        description=_(u'AWS region code where a MapReduce job is executed.'),
        default='us-east-1')
    master_instance_type = colander.SchemaNode(
        colander.String(),
        title=_(u'Master instance type'),
        description=_(u'EC2 instance type of the master node.'),
        widget=SelectWidget(values=_SUPPORT_INSTANCE_TYPE),
        default='m1.small',
    )
    slave_instance_type = colander.SchemaNode(
        colander.String(),
        title=_(u'Slave instance type'),
        description=_(u'EC2 instance type of the slave nodes.'),
        widget=SelectWidget(values=_SUPPORT_INSTANCE_TYPE),
        default='m1.small',
    )
    ec2_keyname = colander.SchemaNode(
        colander.String(),
        title=_(u'EC2 key pair name'),
        description=_(u'EC2 key pair filename.'),
        missing=u'',
    )
    ec2_keyfile = colander.SchemaNode(
        colander.String(),
        title=_(u'EC2 key pair private key file'),
        description=_('It is not available now.'),
        widget=HiddenWidget(),
        missing=u'',
    )
    num_instances = colander.SchemaNode(
        colander.Integer(),
        title=_(u'Number of instances'),
        description=_(u'Number of instances in the Hadoop cluster.'),
        default=1,
    )
    action_on_failure = colander.SchemaNode(
        colander.String(),
        title=_(u'Action on failure'),
        description=_(u'Action to take if a step terminates.'),
        widget=HiddenWidget(),
        default=u'TERMINATE_JOB_FLOW',
    )
    keep_alive = colander.SchemaNode(
        colander.Boolean(),
        title=_(u'Keep alive'),
        description=_(u'Denotes whether the cluster '
                      'should stay alive upon completion.'),
        default=False,
    )
    enable_debugging = colander.SchemaNode(
        colander.Boolean(),
        title=_(u'Enable debugging'),
        description=_(u'Denotes whether AWS console debugging '
                      'should be enabled.'),
        widget=HiddenWidget(),
        default=False,
    )
    termination_protection = colander.SchemaNode(
        colander.Boolean(),
        title=_(u'Termination protection'),
        description=_(u'Set termination protection on jobflows.'),
        widget=HiddenWidget(),
        default=False)
    log_uri = colander.SchemaNode(
        colander.String(),
        title=_(u'log URI'),
        description=_(u'URI of the S3 bucket to place logs.'),
    )
    ami_version = colander.SchemaNode(
        colander.String(),
        title=_(u'AMI version'),
        description=_(u'Amazon Machine Image (AMI) version '
                      'to use for instances.'),
        widget=HiddenWidget(),
        default=_RESOURCE_VERSIONS['ami'],
    )
    hadoop_version = colander.SchemaNode(
        colander.String(),
        title=_(u'Hadoop version'),
        description=_(u'Version of Hadoop to use. This no longer.'),
        widget=HiddenWidget(),
        missing=u'',
        default=_RESOURCE_VERSIONS['hadoop'],
    )
    hive_versions = colander.SchemaNode(
        colander.String(),
        title=_(u'Hive version'),
        description=_(u'Version of Hive to use.'),
        widget=HiddenWidget(),
        missing=u'',
        default=_RESOURCE_VERSIONS['hive'],
    )

def add_emrjob_resource(context, request):
    return generic_add(context, request, SeaUnicornisResourceSchema(),
                       EMRJobResource, EMRJobResource.type_info.title)

from kotti_mapreduce.views import deferred_resource_data

class JobServiceSchema(ContentSchema):
    resource_id = colander.SchemaNode(
        colander.Integer(),
        title=_(u'Resource'),
        description=_(u'Resource name.'),
        widget=deferred_resource_data,
    )

def add_jobservice(context, request):
    return generic_add(context, request, JobServiceSchema(),
                       JobService, JobService.type_info.title)

from kotti_mapreduce.views import deferred_bootstrap_data

class JobFlowSchema(ContentSchema):
    jobtype = colander.SchemaNode(
        colander.String(),
        title=_(u'Job type'),
        description=_(u'Application type for job flow.'),
        widget=HiddenWidget(),
        default=u'hive',
    )
    hive_site = colander.SchemaNode(
        colander.String(),
        title=_(u'Hive site'),
        description=_(u'Use metastore located outside of the cluster.'),
        missing=u'',
    )
    # FIXME: implement one to many relation
    bootstrap1_id = colander.SchemaNode(
        colander.String(),
        title=_(u'Bootstrap #1'),
        widget=deferred_bootstrap_data,
        default=u'',
        missing=u'',
    )
    bootstrap2_id = colander.SchemaNode(
        colander.String(),
        title=_(u'Bootstrap #2'),
        widget=deferred_bootstrap_data,
        default=u'',
        missing=u'',
    )
    bootstrap3_id = colander.SchemaNode(
        colander.String(),
        title=_(u'Bootstrap #3'),
        widget=deferred_bootstrap_data,
        default=u'',
        missing=u'',
    )
    bootstrap4_id = colander.SchemaNode(
        colander.String(),
        title=_(u'Bootstrap #4'),
        widget=deferred_bootstrap_data,
        default=u'',
        missing=u'',
    )
    bootstrap5_id = colander.SchemaNode(
        colander.String(),
        title=_(u'Bootstrap #5'),
        widget=deferred_bootstrap_data,
        default=u'',
        missing=u'',
    )
    bootstrap6_id = colander.SchemaNode(
        colander.String(),
        title=_(u'Bootstrap #6'),
        widget=deferred_bootstrap_data,
        default=u'',
        missing=u'',
    )
    bootstrap7_id = colander.SchemaNode(
        colander.String(),
        title=_(u'Bootstrap #7'),
        widget=deferred_bootstrap_data,
        default=u'',
        missing=u'',
    )
    bootstrap8_id = colander.SchemaNode(
        colander.String(),
        title=_(u'Bootstrap #8'),
        widget=deferred_bootstrap_data,
        default=u'',
        missing=u'',
    )
    bootstrap9_id = colander.SchemaNode(
        colander.String(),
        title=_(u'Bootstrap #9'),
        widget=deferred_bootstrap_data,
        default=u'',
        missing=u'',
    )
    bootstrap10_id = colander.SchemaNode(
        colander.String(),
        title=_(u'Bootstrap #10'),
        widget=deferred_bootstrap_data,
        default=u'',
        missing=u'',
    )
    bootstrap11_id = colander.SchemaNode(
        colander.String(),
        title=_(u'Bootstrap #11'),
        widget=deferred_bootstrap_data,
        default=u'',
        missing=u'',
    )
    bootstrap12_id = colander.SchemaNode(
        colander.String(),
        title=_(u'Bootstrap #12'),
        widget=deferred_bootstrap_data,
        default=u'',
        missing=u'',
    )
    bootstrap13_id = colander.SchemaNode(
        colander.String(),
        title=_(u'Bootstrap #13'),
        widget=deferred_bootstrap_data,
        default=u'',
        missing=u'',
    )
    bootstrap14_id = colander.SchemaNode(
        colander.String(),
        title=_(u'Bootstrap #14'),
        widget=deferred_bootstrap_data,
        default=u'',
        missing=u'',
    )
    bootstrap15_id = colander.SchemaNode(
        colander.String(),
        title=_(u'Bootstrap #15'),
        widget=deferred_bootstrap_data,
        default=u'',
        missing=u'',
    )
    bootstrap16_id = colander.SchemaNode(
        colander.String(),
        title=_(u'Bootstrap #16'),
        widget=deferred_bootstrap_data,
        default=u'',
        missing=u'',
    )

def add_jobflow(context, request):
    return generic_add(context, request, JobFlowSchema(),
                       JobFlow, JobFlow.type_info.title)

from kotti_mapreduce.views import deferred_jobstep_widget
from kotti_mapreduce.views import step_args_validator
from kotti_mapreduce.views import deferred_default_step_args

class JobStepSchema(ContentSchema):
    step_args = colander.SchemaNode(
        colander.String(),
        title=_(u'Step arguments'),
        description=_(u'Arguments to pass to the step.'),
        widget=deferred_jobstep_widget,
        validator=step_args_validator,
        default=deferred_default_step_args,
        missing=u'',
    )

def add_jobstep(context, request):
    return generic_add(context, request, JobStepSchema(),
                       JobStep, JobStep.type_info.title)

def includeme_edit(config):
    config.add_view(
        add_emrjob_resource,
        name=EMRJobResource.type_info.add_view,
        permission='add',
        renderer='kotti:templates/edit/node.pt',
    )

    config.add_view(
        add_jobservice,
        name=JobService.type_info.add_view,
        permission='add',
        renderer='kotti:templates/edit/node.pt',
    )

    config.add_view(
        add_jobflow,
        name=JobFlow.type_info.add_view,
        permission='add',
        renderer='kotti_mapreduce:templates/jobflow-edit.pt',
    )

    config.add_view(
        add_jobstep,
        name=JobStep.type_info.add_view,
        permission='add',
        renderer='kotti:templates/edit/node.pt',
    )

def view_front_page(context, request):
    home_url = get_home_url(request.user)
    if home_url and not request.user.groups:
        return HTTPFound(location=home_url)
    return {
        'api': template_api(context, request),
    }


class SeaUnicornisUserAddFormView(UserAddFormView):
    def schema_factory(self):
        schema = user_schema()
        del schema['active']
        del schema['groups']
        del schema['roles']
        del schema['password']
        return schema

    def add_user_success(self, appstruct):
        appstruct.pop('csrf_token', None)
        name = appstruct['name'] = appstruct['name'].lower()
        appstruct['email'] = appstruct['email'] and appstruct['email'].lower()
        get_principals()[name] = appstruct
        email_set_password(get_principals()[name], self.request)
        self.request.session.flash(
            _(u'The registration mail sent to ${email}.',
            mapping=dict(email=appstruct['email'])), 'success')
        return HTTPFound(location='/')

def view_signup(context, request):
    user_addform = SeaUnicornisUserAddFormView(context, request)()
    if request.is_response(user_addform):
        principal = get_principals().get(request.params[u'name'])
        notify(UserAdded(principal, request))
        return user_addform
    return {
        'api': template_api(context, request),
        'user_addform': user_addform['form'],
    }

def includeme_view(config):
    config.add_view(
        view_front_page,
        name=u'front-page',
        renderer='templates/front-page.pt',
    )

    config.add_view(
        view_signup,
        name=u'signup',
        renderer='templates/signup.pt',
    )

    config.add_static_view('static-sea_unicornis', 'sea_unicornis:static')


def includeme(config):
    config.scan('kotti_mapreduce')
    config.commit()  # for override view functions
    includeme_edit(config)
    includeme_view(config)
    config.add_translation_dirs('sea_unicornis:locale/')
