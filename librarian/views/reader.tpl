% rebase('base.tpl', title=meta.title)

<div class="reader">
    <div class="reader-frame">
        <iframe id="reader-main" class="reader-main" src="{{ i18n_path(url('content:file', content_id=meta.md5, filename='index.html')) }}"></iframe>
    </div>
    <div class="reader-meta data">
        <div class="inner">
            <p class="date">
            <strong>
                {{ meta.timestamp.strftime('%Y-%m-%d') }}
                % if meta.is_partner:
                / {{ meta.partner }} 
                / <span class="special">{{ _('partner') }}</span>
                % end

                % if meta.is_sponsored:
                / {{ meta.partner }} 
                / <span class="special">{{ _('sponsored') }}</span>
                % end

                % if meta.archive == 'core':
                / <span class="special">{{ _('core') }}</span>
                % end
            </strong>
            <a class="button small" href="{{ i18n_path(url('content:zipball', content_id=meta.md5)) }}">{{ _('Download') }}</a>
            </p>
            <p class="licensing">{{ meta.human_license }}</p>
            % end
            % include('_tags')
        </div>
    </div>
</div>

% include('_tag_js_templates')

<script src="/static/js/reader.js"></script>
