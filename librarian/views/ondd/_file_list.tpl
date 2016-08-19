<%namespace name="widgets" file="/ui/widgets.tpl"/>

<%!
import math


BUNDLE_EXT = ".bundle"


def truncate_name(name, max_size=50, separator='...'):
    # Strip out bundle extension
    if name.endswith(BUNDLE_EXT):
        name = name[:-len(BUNDLE_EXT)]
    name_len = len(name)
    if name_len <= max_size:
        return name

    sep_len = len(separator)
    usable_chars_len = max_size - sep_len
    first_len = int(math.ceil(usable_chars_len / 2))
    second_len = int(math.floor(usable_chars_len /2))
    if usable_chars_len % 2 != 0:
        second_len += 1
    return name[0:first_len] + separator + name[(name_len - second_len):]
%>

<%
files = th.state.ondd['transfers']

## Translators, shown on dashboard when no files are currently being
## downloaded
no_transfers = _('No files are being downloaded')

## Translators, shown in downloads list when no file data is
## incoming.
waiting_for_data = _('waiting for data...')
%>

<div data-bind="html: ondd.transfersOSD">
% if not files:
    <p>${no_transfers}</p>
% else:
    <ul>
        % for f in files:
            <li>
            ${widgets.progress_mini(f['percentage'], icon='download-bar')}
            % if f['filename']:
                ${truncate_name(f['filename'])} (${f['percentage']}%)
            % else:
                ${waiting_for_data}
            % endif
            </li>
        % endfor
    </ul>
% endif
</div>

<script type="text/template" id="onddUnknownTransfer">${waiting_for_data}</script>

<script type="text/template" id="onddTransferTemplate">
    <li>
    <span class="o-progress-mini">
        <span class="o-progress-indicator o-progress-percentage-{progress}">
            <span class="o-progress-icon">
                <span class="icon icon-download-bar"></span>
            </span>
        </span>
    </span>
    {transfer-info}
    </li>
</script>

<script type="text/template" id="onddNoTransfersTemplate">
    <p>${no_transfers}</p>
</script>
