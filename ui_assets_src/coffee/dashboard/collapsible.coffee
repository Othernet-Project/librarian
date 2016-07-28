((window, $, templates) ->
  selectors = {
    container: '.dashboard-sections',
    button: '.o-collapsible-section-title',
    collapsibleSection: '.o-collapsible-section',
    collapsibleArea: '.o-collapsible-section-panel',
  }
  spinnerIcon = window.templates.spinnerIcon


  onclick = (e) ->
    clicked = $ e.target
    section = clicked.parents selectors.collapsibleSection
    panel = section.find selectors.collapsibleArea
    # already populated, don't fetch again
    if $.trim(panel.html())
      return

    panel.html spinnerIcon
    section.trigger 'remax'
    url = clicked.attr 'href'
    res = $.get url
    res.done (data) ->
      panel.html data
      section.trigger 'dashboard-plugin-loaded'
      section.trigger 'remax'
      $(document).trigger 'data-bind'
    res.fail () ->
      panel.html templates.dashboardLoadError
      section.trigger 'remax'
    return res


  container = $(selectors.container)
  container.collapsible()
  container.on 'click', selectors.button, onclick

) this, this.jQuery, this.templates
