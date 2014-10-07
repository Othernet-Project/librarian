%# Translators, used as page title
% rebase('base.tpl', title=_('Files'))

<h1>
%# Translators, used as page heading
{{ _('Files') }}
</h1>

<div class="file-list">
    {{! h.form('get', _class='location-bar') }}
        <p class="path">
        <input type="text" value="{{ path if path != '.' else '' }}">
        %# Translators, used as button in file view address bar
        <button type="submit">{{ _('go') }}</button>
        </p>
    </form>

    <table class="file-list-listing">
        % if path != '.':
        <tr class="up">
            <td class="icon"><a href="{{ i18n_path('/files/') + up }}"><span class="icon"></span></a></td>
            %# Translators, used as label for link that leads to parent directory in file listing
            <td colspan="4"><a href="{{ i18n_path('/files/') + up }}">{{ _('(go up one level)') }}<a></td>
        </tr>
        % end
        % for d in dirs:
        <tr class="dir">
            <td class="icon"><a href="{{ i18n_path('/files/') + d.path }}"><span class="icon"></span></td>
            <td colspan="2"><a href="{{ i18n_path('/files/') + d.path }}">{{ d.name }}</a></td>
            <td class="rename">
                {{! h.form('post', action=i18n_path('/files/') + d.path) }}
                    <input type="text" name="name" value="{{ d.name }}">
                    <button class="small" name="action" value="rename" type="submit">{{ _('Rename') }}
                </form>
            </td>
            <td class="delete">
                {{! h.form('post', action=i18n_path('/files/') + d.path) }}
                    <button class="small danger" name="action" value="delete" type="submit">{{ _('Delete') }}
                </form>
            </td>
        </tr>
        % end
        % for f in files:
        <tr class="file">
            <td class="icon"><a href="{{ i18n_path('/files/') + f.path }}"><span class="icon"></span></a>
            <td><a href="{{ i18n_path('/files/') + f.path }}">{{ f.name }}</a></td>
            <td class="size">{{ h.hsize(f.size) }}</td>
            <td class="rename">
                {{! h.form('post', action=i18n_path('/files/') + f.path) }}
                    <input type="text" name="name" value="{{ f.name }}">
                    <button class="small" name="action" value="rename" type="submit">{{ _('Rename') }}
                </form>
            </td>
            <td class="delete">
                {{! h.form('post', action=i18n_path('/files/') + f.path) }}
                    <button class="small danger" name="action" value="delete" type="submit">{{ _('Delete') }}
                </form>
            </td>
        </tr>
        % end
    </table>

    % if readme:
    <h2>{{ _('About this folder') }}</h2>
    <pre class="readme">{{ readme }}</pre>
    % end
</div>
