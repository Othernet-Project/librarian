%# Translators, used as page title
% rebase('base.tpl', title=_('Updates'))
%# Translators, used as page heading
<h1>{{ _('Updates') }}</h1>

<div class="inner">
    <div class="controls">
    {{! h.form(method='GET') }}
        <label for="page">{{ _('page') }}</label>
        {{! h.vselect('p', pager.pager_choices, vals, _id='page') }}
        {{! h.vselect('pp', pager.per_page_choices, vals, id='per-page') }}
        <label for="per-page">{{ _('per page') }}</label>
        <button type="submit">{{ _('Reload') }}</button>
    </form>
    </div>
    <form method="POST">
    % if metadata:
    <p class="controls" id="controls">
        %# Translators, used as button label on updates page for marking all content for import
        <a class="sel-all button" href="?sel=1">{{ _('Select all') }}</a>
        %# Translators, used as button label on updates page for unmarking all content for import
        <a class="sel-none button" href="?sel=0">{{ _('Select none') }}</a>
        %# Translators, used as button label on updates page for adding marked content to library
        <button type="submit" name="action" value="add" class="special">{{ _('Add selected to library') }}</button>
        %# Translators, used as button label on updates page for permanently deleting all downloaded content
        <button type="submit" name="action" value="delete" class="danger">{{ _('Delete selected') }}</button>
    </p>
    % end

    <table>
        <thead>
            <tr>
            %# Translators, used as table header, above checkbox for selecting updates for import
            <th>{{ _('select') }}</th>
            %# Translators, used as table header, content title
            <th>{{ _('title') }}</th>
            %# Translators, used as table header, broadcast date
            <th>{{ _('broadcast') }}</th>
            %# Translators, used as table header, download date
            <th>{{ _('downloaded') }}</th>
            </tr>
        </thead>
        <tbody>
            % if metadata:
                % for meta in metadata:
                <tr>
                    <td class="downloads-selection">
                        <input id="check-{{ meta['md5'] }}" type="checkbox" name="selection" value="{{ meta['md5'] }}"{{ selection and ' checked' or ''}}>
                    </td>
                    <td class="downloads-title">
                        <label for="check-{{ meta['md5'] }}">{{ meta['title'] }}</label>
                    </td>
                    <td class="downloads-timestamp">{{ h.strft(meta['timestamp'], '%m-%d') }}</td>
                    <td class="downloads-ftimestamp">{{ meta['ftimestamp'].strftime('%m-%d') }}</td>
                </tr>
                % end
            % else:
                <tr>
                %# Translators, note that appears in table on updates page when there is no new downloaded content
                <td class="empty" colspan="4">{{ _('There is no new content') }}</td>
                </tr>
            % end
        </tbody>
    </table>

    % if metadata:
    <p class="buttons">
    %# Translators, used as button label on updates page for marking all content for import
    <a class="sel-all button" href="?sel=1">{{ _('Select all') }}</a>
    %# Translators, used as button label on updates page for unmarking all content for import
    <a class="sel-none button" href="?sel=0">{{ _('Select none') }}</a>
    %# Translators, used as button label on updates page for adding marked content to library
    <button type="submit" name="action" value="add" class="special">{{ _('Add selected to library') }}</button>
    %# Translators, used as button label on updates page for permanently deleting all downloaded content
    <button type="submit" name="action" value="delete" class="danger">{{ _('Delete selected') }}</button>
    </p>
    % end
    </form>
</div>

<script src="/static/js/jquery.js"></script>
<script src="/static/js/downloads.js"></script>
