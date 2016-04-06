((window, $) ->
  doc = $ document
  notificationAlertSelector = '.unread-notifications'
  notificationListSelector = '#notification-list'
  notificationSelector = '.notification'
  separatorSelector = '.separator'
  countDisplaySelector = '.unread-notification-count'
  formSelector = '.notification form'

  updateNotificationCount = () ->
    remaining = $(notificationListSelector).find(notificationSelector).length
    notificationAlertEl = $ notificationAlertSelector
    countEl = notificationAlertEl.find countDisplaySelector
    countEl.text remaining
    if remaining is 0
      notificationAlertEl.hide()
      notificationAlertEl.prev(separatorSelector).hide()

  deleteNotification = (e) ->
    elem = $ @
    form = elem.parents formSelector
    url = form.attr 'action'
    res = $.post url, form.serialize()
    res.done () ->
      form.parent().remove()
      updateNotificationCount()

    e.preventDefault()

  doc.on 'tab-opened', (e) ->
    notificationList = $ notificationListSelector
    notificationList.on 'click', '.notification-delete', deleteNotification

) this, this.jQuery
