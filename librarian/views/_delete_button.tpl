<%def name="button(meta)">
<form class="delete-button" action="${i18n_url('content:delete', content_id=meta.md5)}" method="POST">
    <button class="delete small">
        <span class="icon">
            <span class="altlabel"></span> 
            <span class="fulllabel">Delete</span>
        </span>
    </button>
</form>
</%def>
