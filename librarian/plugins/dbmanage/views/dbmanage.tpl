% rebase('_dashboard_section')

<p>
{{ _('Database size') }}: {{ h.hsize(dbsize) }}
<a href="/p/dbmanage/librarian.sqlite">{{ _('download') }}</a>
</p>
