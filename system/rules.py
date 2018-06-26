from __future__ import unicode_literals
from __future__ import absolute_import

import rules


@rules.predicate
def has_program_access(user, program):
    if user.program_restrictions.exists() and program:
        return user.program_restrictions.filter(id=program.id).exists()
    return False


@rules.predicate
def has_program_related_access(user, related):
    if user.program_restrictions.exists() and related and related.program:
        return user.program_restrictions.filter(id=related.program.id).exists()
    return False


rules.add_perm('system', rules.always_allow)
rules.add_perm('system.change_program', has_program_access)

rules.add_perm('system.add_variable', has_program_related_access)
rules.add_perm('system.change_variable', has_program_related_access)
rules.add_perm('system.delete_variable', has_program_related_access)

rules.add_perm('system.add_programuseraccess', has_program_related_access)
rules.add_perm('system.change_programuseraccess', has_program_related_access)
rules.add_perm('system.delete_programuseraccess', has_program_related_access)

rules.add_perm('system.add_session', has_program_related_access)
rules.add_perm('system.change_session', has_program_related_access)
rules.add_perm('system.delete_session', has_program_related_access)

rules.add_perm('system.add_content', has_program_related_access)
rules.add_perm('system.change_content', has_program_related_access)
rules.add_perm('system.delete_content', has_program_related_access)

rules.add_perm('users.change_user', has_program_related_access)
rules.add_perm('users.delete_user', has_program_related_access)
