<p>
    ## Translators, used as label for language
    <label for="language">${_('Language:')}</label>
    ${h.vselect('language', UI_LANGS, language)}
    ${h.field_error('language', errors)}
</p>
