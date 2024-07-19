import os
from django.core.exceptions import ValidationError

def allow_only_images_validator(value):
    extension = os.path.splitext(value.name)[1]
    valid_extensions = ['.png', '.jpg', '.jpeg']

    if extension.lower() not in valid_extensions:
        raise ValidationError('Unsupported file extension. Allowed extensions: ' + str(valid_extensions))