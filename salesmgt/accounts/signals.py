from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Profile

# Get the active user model, which is best practice for referencing the User model.
User = get_user_model() 


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler function executed after a User instance is saved.

    Args:
        sender (Model Class): The model class that sent the signal (User).
        instance (User): The actual User instance that was just saved.
        created (bool): True if a new record was created, False if an existing 
                        record was updated.
        **kwargs: Additional keyword arguments.
    """

    if created:
        Profile.objects.create(user=instance)
        print(f'Profile for user {instance.username} created successfully.')
        
    else:
        try:
            instance.profile.save()
            print(f'Profile for user {instance.username} updated.')
        except Profile.DoesNotExist:
            Profile.objects.create(user=instance)
            print(f'ALERT: Missing Profile for user {instance.username} recreated.')