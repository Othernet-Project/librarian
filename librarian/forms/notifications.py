from bottle_utils import form


class NotificationForm(form.Form):
    MARK_READ = 'mark_read'
    MARK_READ_ALL = 'mark_read_all'
    ACTIONS = (
        (MARK_READ, MARK_READ),
        (MARK_READ_ALL, MARK_READ_ALL),
    )
    notification_id = form.StringField()
    action = form.SelectField(choices=ACTIONS)

    def should_mark_all(self):
        return self.processed_data['action'] == self.MARK_READ_ALL
