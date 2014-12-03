%# Translators, used as page title
% rebase('base', title=_('Content could not be removed'))

%# Translators, used as page heading
<h1>{{ _('Content could not be removed') }}</h1>

<div class="inner">
    %# Translators, message displayed when content cannot be deleted
    <p>{{ _('Please make sure the storage device is not write-protected and try again.') }}</p>

    <form method="POST">
        %# Translators, used as label on button for retrying content removal
        <button type="submit">{{ _('Retry') }}</button>
    </form>
</div>
