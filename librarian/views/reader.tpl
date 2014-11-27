% rebase('base.tpl', title=meta.title)

<div class="reader">
    <div class="reader-frame">
        <iframe id="reader-main" class="reader-main" src="/pages/{{ meta.md5 }}/index.html"></iframe>
    </div>
    <div class="reader-meta">
        <div class="inner">
            <p class="date">
            <strong>
                {{ meta.timestamp.strftime('%Y-%m-%d') }}
                % if meta.is_partner or meta.is_sponsored:
                / {{ meta.partner }}
                % end
                % if meta.archive == 'core':
                / {{ _('Outernet core archive') }}
                % end
                % if meta.is_sponsored:
                / <span class="sponsored">{{ _('sponsored content') }}</span>
                % end
            </strong>
            </p>
            % if meta.free_license:
            <p class="licensing">{{ str(_('This content was published under %s license')) % meta.human_license }}</p>
            % end
        </div>
    </div>
</div>

