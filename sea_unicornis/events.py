# -*- coding: utf-8 -*-
from kotti.events import ObjectEvent
from kotti.events import objectevent_listeners
from kotti.resources import get_root
from kotti.security import Principal
from kotti.security import set_groups
from kotti_mapreduce.resources import JobContainer

from sea_unicornis.consts import JOB_CONTAINERS


class UserAdded(ObjectEvent):
    pass

def initialize_user_home(event):
    user_name = event.object.name
    job_url = JOB_CONTAINERS['url']
    root = get_root()
    root[job_url][user_name] = JobContainer(title=u'home', owner=user_name)
    set_groups(user_name, root[job_url][user_name], set([u'role:owner']))

def includeme(config):
    objectevent_listeners[(UserAdded, Principal)].append(initialize_user_home)
