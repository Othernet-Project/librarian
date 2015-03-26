% extra_scripts = '<script src="/static/js/content.js"></script>'

%# Translators, used as page title
% rebase('base.tpl', title=_('Login'))
<h1>
%# Translators, used as page heading
{{ _('Login') }}
</h1>

<div class="inner login">
    {{! h.form('post') }}
        <p>
            <input type="text" name="username" placeholder="{{ _('Username') }}" value="{{ username }}" />
        </p>
        <p>
            <input type="password" placeholder="{{ _('Password') }}" name="password" />
        </p>
        % if error:
        <p class="error">{{ error }}</p>
        % end
        <p>
            <input type="hidden" name="next" value="{{ next }}" />
            <button type="submit"><span class="icon">{{ _('Login') }}</span></button>
        </p>
    </form>
</div>
