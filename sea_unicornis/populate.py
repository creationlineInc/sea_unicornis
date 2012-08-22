# -*- coding: utf-8 -*-
from kotti.populate import populate_users
from kotti.resources import DBSession
from kotti.resources import Document
from kotti.resources import Node
from kotti.security import set_groups
from kotti.workflow import get_workflow

from sea_unicornis.consts import JOB_CONTAINERS
from sea_unicornis.consts import SITE_ACL

def populate_root_document():
    if DBSession.query(Node).count() == 0:
        root = Document(name=u'', title=u'Front Page')
        root.__acl__ = SITE_ACL
        root.default_view = 'front-page'
        DBSession.add(root)
        url = JOB_CONTAINERS['url']
        root[url] = Document(title=u'Job Containers', owner=u'admin')
        set_groups(u'admin', root[url], set([u'role:owner']))

        wf = get_workflow(root)
        if wf is not None:
            DBSession.flush()  # Initializes workflow
            wf.transition_to_state(root, None, u'public')

def populate():
    populate_users()
    populate_root_document()
    print 'Sea Unicornis site is initialized'
