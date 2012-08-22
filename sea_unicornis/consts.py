# -*- coding: utf-8 -*-

JOB_CONTAINERS = {
    'url': 'j',
}

SITE_ACL = [
    ['Allow', 'role:editor', ['view', 'add', 'edit', 'state_change']],
    ['Allow', 'role:owner', ['view', 'add', 'edit', 'manage', 'state_change']],
]
