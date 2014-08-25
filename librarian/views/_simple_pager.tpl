% if page > 1 and page:
<a href="{{ i18n_path(request.path) }}?p={{ page - 1 }}&c={{ f_per_page }}" class="button prev">previous</a>
% end
% if page < total_pages - 1:
<a href="{{ i18n_path(request.path) }}?p={{ page + 1 }}&c={{ f_per_page }}" class="button next">next</a>
% end
