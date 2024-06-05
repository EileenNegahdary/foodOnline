from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import User, UserProfile


@receiver(post_save, sender=User)
def post_save_create_profile_receiver(sender, instance, created, **kwargs):
    print(created)
    if created:
        # if a user is created, create a user profile for it
        UserProfile.objects.create(user=instance)
        print('user profile created')
    else:
        # if a user is modified, update the user profile
        try:
            profile = UserProfile.objects.get(user=instance)
            profile.save()
            print('user profile updated')
        except:
            # if user profile doesn't exist, create it
            UserProfile.objects.create(user=instance)
            print('user profile created')
# post_save.connect(post_save_create_profile_receiver, sender=User)

def pre_save_profile(sender, instance, **kwargs):
    print(instance.username, 'this user is being saved')

