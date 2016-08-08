((window, $, templates) ->

  BUNDLE_EXT = ".bundle"

  section = $ '#dashboard-ondd'
  templateIds = [
    'onddTransferTemplate',
    'onddUnknownTransfer',
    'onddNoTransfersTemplate', 
  ]
  reProgress = new RegExp '\{progress\}', 'g'


  roundedPercentage = (src) ->
    rounded = Math.floor(src / 5) * 5
    Math.min (Math.max rounded, 0), 100


  truncateName = (name, maxSize=50, separator='...') ->
    # Strip out bundle extension
    bExtIdx = name.indexOf BUNDLE_EXT
    if bExtIdx == name.length - BUNDLE_EXT.length
      name = name.substring(0, bExtIdx)

    if name.length <= maxSize
      return name

    usableChars = maxSize - separator.length
    firstLen = Math.ceil (usableChars / 2)
    secondLen = Math.floor (usableChars / 2)
    if usableChars % 2 != 0
      secondLen += 1
    name.substring(0, firstLen) + separator + name.substring(name.length - secondLen, name.length)


  transfersOSD = (data) ->
    if data.transfers.length == 0
      return templates.onddNoTransfersTemplate

    html = ''
    for transfer in data.transfers
      if not transfer.filename
        info = templates.onddUnknownTransfer
      else
        filename = truncateName transfer.filename
        info = "#{filename} (#{transfer.percentage}%)"

      html += templates.onddTransferTemplate
        .replace('{transfer-info}', info)
        .replace('{percentage}', transfer.percentage)
        .replace('{progress}', roundedPercentage transfer.percentage)

    html = "<ul>#{html}</ul>"
    return html


  initPlugin = (e) ->
    for tmplId in templateIds
      $("##{tmplId}").loadTemplate()

    provider = window.state.provider 'ondd'
    provider.postprocessor transfersOSD, ['transfersOSD']


  section.on 'dashboard-plugin-loaded', initPlugin

) this, this.jQuery, this.templates
