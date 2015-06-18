<%def name="button(meta)">
<form class="delete-button" action="${i18n_url('content:delete', content_id=meta.md5)}" method="POST">
    <button>
        ${_('Delete')}
    </button>
</form>
</%def>
