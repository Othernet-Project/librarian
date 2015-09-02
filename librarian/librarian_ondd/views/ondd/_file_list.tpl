<%namespace name="widgets" file="../_widgets.tpl"/>

% if not files:
## Translators, shown on dashboard when no files are currently being downloaded
<p>${_('No files are being downloaded')}</p>
% else:
    ## Translators, used as title of a subsection in dashboard that lists files that are currently being downloaded
    <p>${_('Downloads in progress')}</p>
    % for f in files:
        ${widgets.progress(f['filename'], f['percentage'], value='{0}%'.format(f['percentage']))}
    % endfor
% endif
