% if page > 1 and page:
%# Translators, used in the pager
<a href="{{ i18n_path(request.path) }}?p={{ page - 1 }}&c={{ f_per_page }}" class="button prev">{{ _('previous') }}</a>
% end
% if page < total_pages - 1:
%# Translators, used in the pager
<a href="{{ i18n_path(request.path) }}?p={{ page + 1 }}&c={{ f_per_page }}" class="button next">{{ _('next') }}</a>
% end
