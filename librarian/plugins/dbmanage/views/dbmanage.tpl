% rebase('_dashboard_section')

<p>
{{ _('Database size') }}: {{ h.hsize(dbsize) }}
<a href="{{ url('plugins:dbmanage:download') }}">{{ _('download') }}</a>
</p>

<div class="inline-form-wrapper">
    <form action="{{ i18n_path(url('plugins:dbmanage:backup')) }}" method="POST" class="inline">
        %# Translators, refers to database backup
        <button>{{ _('Backup') }}</button>
    </form>

    <form action="{{ i18n_path(url('plugins:dbmanage:rebuild')) }}" method="POST" class="inline">
        %# Translators, refers to database rebuild feature
        <button>{{ _('Rebuild') }}</button>
    </form>
</div>

<p class="warning">
    %# Translators, note about database rebuild shown on dashboard
    {{ _("Database rebuild will cause all tags to be lost. It will also put Librarian into maintenance mode and prevent users from accessing content.") }}
</p>
