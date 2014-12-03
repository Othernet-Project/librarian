% if meta['images'] > 0:
<span class="badge images"><span class="icon"></span> {{ meta['images'] }}</span>
% end

% if meta.get('archive') == 'core':
<span title="{{ _('This content is part of Outernet core archive') }}"class="badge is-core">
    %# Translators, used as 'content belongs to core archive' badge
    {{ _('core') }}
</span>
% end

% if meta.get('is_partner', False):
<span title="{{ _('This content comes from Outernet\'s content partner') }}" class="badge is-partner">
    %# Translators, used as 'partner content' badge
    {{ _('partner') }}
</span>
% end

% if meta.get('is_sponsored', False):
<span title="{{ _('This content is sponsored') }}" class="badge is-sponsored">
    %# Translators, used as 'sponsored content' badge
    {{ _('sponsored') }}
</span>
% end

%# Translators, used as 'unknown license' badge
%#<abbr class="badge license" title="{{ readable_license(meta.get('license')) }}">{{ meta.get('license') or _('unknown') }}</abbr>

% if meta.get('partner'):
%# Translators, appears next to content title when content is sponsored or is partner content, %s is replaced by person/company name; not part of sentence
<span class="badge attribution">{{ u(_('from %s')) % meta['partner'] }}</span>
% end

