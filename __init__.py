# -*- coding: utf-8 -*-

from . import models
from . import wizards


def post_init_hook(env):
    """Migration des données et configuration initiale TECHPARK CI."""
    env.cr.execute("""
        UPDATE it_equipment SET state = 'draft'
        WHERE state NOT IN ('draft', 'assigned', 'maintenance', 'retired')
    """)
    group = env.ref('it_parc.group_it_manager', raise_if_not_found=False)
    admin = env.ref('base.user_admin', raise_if_not_found=False)
    if group and admin and admin not in group.users:
        group.write({'users': [(4, admin.id)]})

