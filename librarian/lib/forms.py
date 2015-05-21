"""
forms.py: Form validation and processing

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from bottle_utils import html
from bottle_utils.common import basestring, unicode
from bottle_utils.i18n import lazy_gettext as _


class FieldUnboundError(Exception):
    """Exception raised when a form field has no name assigned to it"""
    pass


class ValidationError(Exception):

    def __init__(self, message, params):
        self.message = message
        self.params = params
        super(ValidationError, self).__init__(message)

    def __str__(self):
        """Calls renderer function"""
        return self.render()

    def __unicode__(self):
        """Calls renderer function"""
        return self.render()

    def render(self):
        msg = self.message.format(**self.params)
        return html.SPAN(html.html_escape(msg), _class=html.ERR_CLS)


class Validator(object):

    def __call__(self, data):
        self.validate(data)

    def validate(self, data):
        """Perform actual validation over data. Should raise `ValidationError`
        if data does not pass the validation."""
        raise NotImplementedError()


class Required(Validator):

    def validate(self, data):
        if not data or isinstance(data, basestring) and not data.strip():
            raise ValidationError(_("This field is required."), {})


class Field(object):
    _id_prefix = 'id_'

    def __init__(self, label, validators=None, value=None, **kwargs):
        self.label = label
        self.validators = validators or []
        self.error = None
        self.value = value
        self.processed_value = None
        self._name = None

    def __str__(self):
        """Calls renderer function"""
        return self.render()

    def __unicode__(self):
        """Calls renderer function"""
        return self.render()

    @property
    def name(self):
        if self._name is None:
            raise FieldUnboundError()
        return self._name

    def bind(self, field_name):
        attrs = {}
        for attr_name in dir(self):
            if not attr_name.startswith('__') and attr_name != 'name':
                value = getattr(self, attr_name)
                if not callable(value):
                    attrs[attr_name] = value

        instance = self.__class__(**attrs)
        instance._name = field_name
        instance.is_value_bound = False
        return instance

    def bind_value(self, value):
        self.value = value
        self.is_value_bound = True

    def is_valid(self):
        try:
            self.processed_value = self.parse(self.value)
        except ValueError as exc:
            self.error = ValidationError(str(exc), {'value': self.value})
            return False

        for validate in self.validators:
            try:
                validate(self.processed_value)
            except ValidationError as exc:
                self.error = exc
                return False

        return True

    def parse(self, value):
        """Subclasses should return the value in it's correct type. In case the
        passed in value cannot be cast into it's correct type, the method
        should raise a `ValueError` exception with an appropriate error
        message."""
        raise NotImplementedError()

    def render(self):
        """Subclasses should return the string html representation of the
        concrete field."""
        raise NotImplementedError()


class StringField(Field):

    def parse(self, value):
        if value is None:
            return ''
        return unicode(value)

    def render(self):
        return html.vinput(self.name,
                           {self.name: self.value},
                           _type='text',
                           _id=self._id_prefix + self.name)


class TextAreaField(StringField):

    def render(self):
        return html.varea(self.name,
                          {self.name: self.value},
                          _id=self._id_prefix + self.name)


class IntegerField(Field):

    def parse(self, value):
        try:
            return int(value)
        except Exception:
            raise ValueError(_("Invalid value for an integer."))

    def render(self):
        return html.vinput(self.name,
                           {self.name: self.value},
                           _type='text',
                           _id=self._id_prefix + self.name)


class FloatField(Field):

    def parse(self, value):
        try:
            return float(value)
        except Exception:
            raise ValueError(_("Invalid value for a float."))

    def render(self):
        return html.vinput(self.name,
                           {self.name: self.value},
                           _type='text',
                           _id=self._id_prefix + self.name)


class BooleanField(Field):

    def __init__(self, label, validators=None, value=None, default=False,
                 **kwargs):
        self.default = default
        self.expected_value = value
        super(BooleanField, self).__init__(label,
                                           validators=validators,
                                           value=value,
                                           **kwargs)

    def parse(self, value):
        if not value or isinstance(value, basestring):
            return self.expected_value == value
        return self.expected_value in value

    def render(self):
        data = {self.name: self.value} if self.is_value_bound else {}
        return html.vcheckbox(self.name,
                              self.expected_value,
                              data,
                              default=self.default,
                              _id=self._id_prefix + self.name)


class SelectField(Field):

    def __init__(self, label, validators=None, value=None, choices=None,
                 **kwargs):
        self.choices = choices or tuple()
        super(SelectField, self).__init__(label,
                                          validators=validators,
                                          value=value,
                                          **kwargs)

    def parse(self, value):
        chosen = unicode(value)
        for (candidate, label) in self.choices:
            if unicode(candidate) == chosen:
                return chosen if value is not None else value

        raise ValueError(_("This is not a valid choice."))

    def render(self):
        return html.vselect(self.name,
                            self.choices,
                            {self.name: self.value})


class Form(object):
    """Base form class to be subclassed. Definition of new forms:

    class NewForm(Form):
        field1 = Field('Field 1')
        field2 = Field('Field 2', [Required])

        def preprocess_field1(self, value):
            return value.replace('this', 'that')

        def postprocess_field1(self, value):
            return value + 'done'

    Preprocessors can be defined for individual fields, and are ran before any
    validation happens over the field's data. Preprocessors are also allowed
    to raise `ValidationError`, though their actual purpose is to perform some
    manipulation over the incoming data, before it is passed over to the
    validators. The return value of the preprocessor is the value that is going
    to be validated further.

    Postprocessors perform a similar purpose as preprocessors, only they are
    invoked after and if the field-level validation passed. Their return value
    is the value that is going to be the stored as cleaned / validated data.
    """
    _pre_processor_prefix = 'preprocess_'
    _post_processor_prefix = 'postprocess_'
    _form_name = '_'

    def __init__(self, data=None):
        """Initialize forms.

        :param data:     Dict-like object containing the form data to be
                         validated, or the initial values of a new form
        """
        self.errors = {}
        self.processed_data = {}

        self._bind(data)

    def _bind(self, data):
        """Binds field names and values to the field instances."""
        for field_name, field in self.fields.items():
            field_instance = field.bind(field_name)
            setattr(self, field_name, field_instance)
            if data is not None:
                field_instance.bind_value(data.get(field_name))

    @property
    def fields(self):
        """Returns a dictionary of all the fields found on the form instance.
        The return value is never cached so dynamically adding new fields to
        the form is allowed."""
        is_form_field = lambda name: isinstance(getattr(self, name), Field)
        return dict((name, getattr(self, name)) for name in dir(self)
                    if name != 'fields' and is_form_field(name))

    def _add_error(self, field_name, error):
        # if the error is from one of the processors, bind it to the field too
        if field_name != self._form_name:
            self.fields[field_name].error = error
        self.errors[field_name] = error

    def _run_processor(self, prefix, field_name, value):
        processor_name = prefix + field_name
        processor = getattr(self, processor_name, None)
        if callable(processor):
            return processor(value)
        return value

    def is_valid(self):
        """Perform full form validation over the initialized form. The method
        has the following side-effects:
          - in case errors are found, the form's `errors` container is going to
            be populated accordingly.
          - validated and processed values are going to be put into the
            `processed_data` dictionary.

        :returns:  boolean indication whether the form is valid or not
        """
        for field_name, field in self.fields.items():
            # run pre-processor on value, if defined
            try:
                field.processed_value = self._run_processor(
                    self._pre_processor_prefix,
                    field_name,
                    field.value
                )
            except ValidationError as exc:
                self._add_error(field_name, exc)
                continue
            # perform individual field validation
            if not field.is_valid():
                self._add_error(field_name, field.error)
                continue
            # run post-processor on processed value, if defined
            try:
                field.processed_value = self._run_processor(
                    self._post_processor_prefix,
                    field_name,
                    field.processed_value
                )
            except ValidationError as exc:
                self._add_error(field_name, exc)
                continue
            # if field level validations passed, add the value to a dictionary
            # holding validated / processed data
            self.processed_data[field_name] = field.processed_value

        # run form level validation
        try:
            self.validate()
        except ValidationError as exc:
            self._add_error(self._form_name, exc)

        return not self.errors

    def validate(self):
        """Perform form-level validation, which can check fields dependent on
        each other. The function is expected to be overridden by implementors
        in case form-level validation is needed, but it's optional. In case an
        error is found, a `ValidationError` exception should be raised by the
        function."""
        pass
