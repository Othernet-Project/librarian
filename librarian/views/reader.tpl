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
                % if meta.is_partner:
                / {{ meta.partner }} 
                / <span class="partner">{{ _('content partner') }}</span>
                % end

                % if meta.is_sponsored:
                / {{ meta.partner }} 
                / <span class="sponsored">{{ _('sponsored content') }}</span>
                % end

                % if meta.archive == 'core':
                / {{ _('Outernet core archive') }}
                % end
            </strong>
            </p>
            <p class="licensing">{{ meta.human_license }}</p>
            % end
        </div>
    </div>
</div>

