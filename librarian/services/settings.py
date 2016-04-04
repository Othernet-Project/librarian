from bottle_utils import form


class Group(dict):

    @classmethod
    def create(cls, label):
        instance = cls()
        instance.label = label
        return instance


class SettingsManager(object):
    _field_template = '{group}.{name}'
    _select_type = 'select'
    _date_type = 'date'
    _field_types = {
        bool: form.BooleanField,
        int: form.IntegerField,
        str: form.StringField,
        float: form.FloatField,
        # special types
        _select_type: form.SelectField,
        _date_type: form.DateField,
    }

    def __init__(self, supervisor):
        self._supervisor = supervisor
        self._groups = dict()
        self._settings = dict()

    groups = property(lambda self: ((name, group.label)
                                    for (name, group) in self._groups.items()))

    def add_group(self, name, label):
        if name in self._groups:
            raise ValueError("Group already exists.")

        self._groups[name] = Group.create(label)

    def add_field(self, name, group, label, value_type, help_text=None,
                  required=False, default=None, choices=None):
        if group not in self._groups:
            raise ValueError("Group {} not registered.".format(group))

        if value_type not in self._field_types:
            raise TypeError("Unknown type specified for {}".format(name))

        if value_type == self._select_type and choices is None:
            raise TypeError("No choices specified for {}".format(name))

        if name in self._groups[group]:
            raise ValueError("A field is already registered "
                             "by name {}".format(name))

        self._groups[group][name] = dict(label=label,
                                         value_type=value_type,
                                         help_text=help_text,
                                         required=bool(required),
                                         default=default,
                                         choices=choices)

    def get_form(self):
        attrs = dict()
        for (group_name, group) in self._groups.items():
            for (field_name, options) in group.items():
                name = self._field_template.format(group=group_name,
                                                   name=field_name)
                field_cls = self._field_types[options['value_type']]
                validators = ([], [form.Required()])[options['required']]
                # actual value from config overrides default value
                value = self._supervisor.config.get(name, options['default'])
                kwargs = dict(label=options['label'],
                              help_text=options['help_text'],
                              validators=validators)
                if options['value_type'] == self._select_type:
                    kwargs['choices'] = options['choices']

                if options['value_type'] is bool:
                    kwargs['default'] = value
                    kwargs['value'] = name
                else:
                    kwargs['value'] = value

                attrs[name] = field_cls(**kwargs)

        return type('SettingsForm', (form.Form,), attrs)

