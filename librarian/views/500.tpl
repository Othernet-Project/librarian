%# Translators, used as page title
% rebase('base', title=_('Error'))

<h1>
%# Translators, used as error page heading
500: {{ _('Error') }}
</h1>

<div class="inner">
    <p>{{ _('Librarian has failed to fulfill your request due to unexpected error in the program. Details are provided below.') }}</p>

    <pre class="trace"><code>{{ trace }}</code></pre>

    <p>
    <a class="button" href="{{ url('sys:logs') }}">{{ _('Download application log') }}</a>
    </p>
</div>
