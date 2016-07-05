((window, $, templates) ->
  selectors = {
    container: '.dashboard-sections',
    button: '.o-collapsible-section-title',
    collapsibleSection: '.o-collapsible-section',
    collapsibleArea: '.o-collapsible-section-panel',
  }

  onclick = (e) ->
    clicked = $ e.target
    section = clicked.parents selectors.collapsibleSection
    panel = section.find selectors.collapsibleArea
    # already populated, don't fetch again
    if $.trim(panel.html())
      return

    url = clicked.attr 'href'
    res = $.get url
    res.done (data) ->
      panel.html data
      section.trigger 'remax'
    res.fail () ->
      panel.html templates.dashboardLoadError
      section.trigger 'remax'
    return res

  container = $(selectors.container)
  container.collapsible()
  container.on 'click', selectors.button, onclick
) this, this.jQuery, this.templates
