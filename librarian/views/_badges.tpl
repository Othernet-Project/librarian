% if meta.images > 0:
<span class="badge images"><span class="icon"></span> {{ meta['images'] }}</span>
% end

%# Translators, used as 'unknown license' badge
%#<abbr class="badge license" title="{{ readable_license(meta.get('license')) }}">{{ meta.get('license') or _('unknown') }}</abbr>

