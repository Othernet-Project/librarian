((window, $, templates) ->
  langSelect = $ '#language-select-field'
  langSelect.on('change', ->
    lang = langSelect.val()
    location.replace "#{location.origin}/#{lang}#{location.pathname.slice(3)}#{location.search}"
  )
) this, this.jQuery, this.templates
