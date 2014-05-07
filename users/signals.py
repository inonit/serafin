from __future__ import unicode_literals

from django.db.models import signals
from django.dispatch import receiver
from users.models import User


@receiver(signals.post_save, sender=User)
def mirror_user(sender, **kwargs):
    user = kwargs['instance']
    if kwargs['created']:
        user._mirror_user(
            email=user.data.get('email'),
            phone=user.data.get('phone')
        )

    if 'email' in user.data:
        del user.data['email']
    if 'phone' in user.data:
        del user.data['phone']
    User.objects.filter(id=user.id).update(data=user.data)



@receiver(signals.pre_delete, sender=User)
def delete_mirror(sender, **kwargs):
    kwargs['instance']._delete_mirror()
