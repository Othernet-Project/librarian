%# Translators, used as page title
% rebase('base.tpl', title=_('Files'))

<h1>
%# Translators, used as page heading
{{ _('Files') }}
</h1>

<div class="file-list">
    {{! h.form('get') }}
        <p class="path">
        <input type="text" value="{{ path if path != '.' else '' }}">
        %# Translators, used as button in file view address bar
        <button type="submit">{{ _('go') }}</button>
        </p>
    </form>

    <ul class="file-list-dirs">
        % if path != '.':
        <li class="up"><a href="{{ i18n_path('/files/') + up }}">..</a></li>
        % end
        % for d in dirs:
        <li class="dir"><a href="{{ i18n_path('/files/') + d.path }}">{{ d.name }}</a></li>
        % end
    </ul>

    <ul class="file-list-files">
        % for f in files:
        <li class="file"><a href="{{ i18n_path('/files/') + f.path }}">{{ f.name }}</a></li>
        % end
    </ul>
</div>
