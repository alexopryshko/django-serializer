from django import forms
from django.core.exceptions import ValidationError
import json


class ObjectField(forms.Field):
    default_error_messages = {
        'invalid_type': 'Object is incorrect'
    }

    @staticmethod
    def get_field_problems(form):
        field_problems = []
        for field, error in form.errors.items():
            for data_item in error.data:
                for message in data_item.messages:
                    field_problems.append('{}: {}'.format(field, message))
        return field_problems

    def form_validator(self, value):
        if self.multiple:
            for item in value:
                form = self.form_class(data=item)
                if not form.is_valid():
                    raise ValidationError(self.get_field_problems(form), code='invalid_form')
                else:
                    self._validate_forms.append(form)
        else:
            form = self.form_class(data=value)
            if not form.is_valid():
                raise ValidationError(self.get_field_problems(form), code='invalid_form')
            self._validate_forms.append(form)

    def __init__(self, form_class, multiple=False, *args, **kwargs):
        validators = kwargs.pop('validators', [])
        if isinstance(validators, tuple):
            validators += (self.form_validator,)
        else:
            validators.append(self.form_validator)
        self.form_class = form_class
        self.multiple = multiple
        self._validate_forms = []
        super().__init__(*args, validators=validators, **kwargs)

    def to_python(self, value):
        value = super().to_python(value)
        self._validate_forms.clear()
        if isinstance(value, dict):
            return value
        elif isinstance(value, str):
            return json.loads(value)
        else:
            return value

    def validate(self, value):
        super().validate(value)

        if value is None:
            return

        if self.multiple:
            if not isinstance(value, list):
                raise ValidationError(self.error_messages['invalid_type'], code='invalid_type')
            if any([not isinstance(item, dict) for item in value]):
                raise ValidationError(self.error_messages['invalid_type'], code='invalid_type')
        else:
            if not isinstance(value, dict):
                raise ValidationError(self.error_messages['invalid_type'], code='invalid_type')

    def clean(self, value):
        super().clean(value)
        if self.multiple:
            return [form.cleaned_data for form in self._validate_forms]
        if len(self._validate_forms) > 0:
            return self._validate_forms[0].cleaned_data
