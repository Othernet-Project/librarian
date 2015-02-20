% rebase('_dashboard_section')

<p>
{{ _('Database size') }}: {{ h.hsize(dbsize) }}
<a href="/p/dbmanage/librarian.sqlite">{{ _('download') }}</a>
</p>

<form action="{{ i18n_path('/p/dbmanage/backup') }}" method="POST" class="inline">
    %# Translators, refers to database backup
    <button>{{ _('Backup') }}</button>
</form>
