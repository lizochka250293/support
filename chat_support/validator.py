from django.core.exceptions import ValidationError


def username_validator(username):
    conditions = [
        not username.isdigit()
    ]
    if any(conditions):
        raise ValidationError('Поле должно состоять только из цифр')
