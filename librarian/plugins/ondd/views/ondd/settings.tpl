% extra_scripts = '<script src="%s"></script>' % url('plugins:ondd:static', path='ondd.js')

%# Translators, used as page title
% rebase('base', title=_('Tuner settings'), extra_scripts=extra_scripts)

<h1>
%# Translators, used as page heading
{{ _('Tuner settings') }}
</h1>

<div class="inner">
    % include('ondd/_settings_for')
</div>

