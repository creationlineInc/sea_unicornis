# -*- coding: utf-8 -*-
from sea_unicornis.consts import JOB_CONTAINERS

def get_home_url(principal):
    home_url = None
    if principal:
        home_url = '/{0}/{1}/'.format(JOB_CONTAINERS['url'], principal.name)
    return home_url
