<table class="ondd-file-list">
    <tbody>
        % if not files:
        ## Translators, shown on dashboard when no files are currently being downloaded
        <tr><td>${_('No files are being downloaded')}</td></tr>
        % else:
            % for f in files:
            <tr>
                <td class="ondd-file-path">${f['path']}</td>
                <td class="ondd-file-size">${h.hsize(f['size'])}</td>
                <td class="ondd-file-progress">
                    <span class="ondd-progress-bar">
                        <span class="ondd-progress-bar-inner" style="width: ${f['progress']}%">
                            <span class="ondd-progress-bar-label">${f['progress']}%</span>
                        </span>
                    </span>
                </td>
            </tr>
            % endfor
        % endif
    </tbody>
</table>
