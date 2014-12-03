(function (window, $) {
  var win = $(window);
  var doc = $(document.body);
  var contentList = $('#content-list');
  var tagCloud = $('#tag-cloud-container');
  var currentTag = $('#current-tag');

  win.on('listUpdate', resetTagForm);
  doc.on('click', '.tag-button', openTagForm);
  doc.on('click', '.tag-close-button', closeTagForm);
  doc.on('submit', '.tag-form', updateTags);

  initTagUIState.call(doc);

  function resetTagForm(e, newItems) {
    initTagUIState.call(newItems);
  }

  function initTagUIState() {
    var el = $(this);
    var form = el.find('.tag-form');
    form.find('p:first').append(templates.closeTagButton);
    form.hide();
    el.find('.tags').append(templates.tagButton);
  }

  function openTagForm(e) {
    var el = $(this);
    var tags = el.parent();
    tags.hide();
    tags.next('.tag-form').show();
    if (contentList != null && contentList.masonry != null) {
      contentList.masonry();
    }
  }

  function closeTagForm() {
    var el = $(this);
    var form = el.parents('.tag-form');
    var tags = form.prev();
    form.hide();
    tags.show();
    form.find('input').val(getTags(tags));
    if (contentList != null && contentList.masonry != null) {
      contentList.masonry();
    }
  }

  function updateTags(e) {
    var xhr;
    var form = $(this);
    var url = form.attr('action');
    var tags = form.find('input').val();
    var tagList = form.prev();
    var buttons = form.find('button');

    e.preventDefault();
    buttons.prop('disabled', true);

    xhr = $.post(url, {tags: tags});
    xhr.done(function (res) {
      tagList.html(res + templates.tagButton);
      form.data('original', getTags(tagList));
      closeTagForm.call(buttons);
      updateTagCloud();
    });
    xhr.fail(updateError);
    xhr.always(function () { buttons.prop('disabled', false); });
  }

  function updateTagCloud() {
    if (!tagCloud.length) { return; }
    tagCloud.load(tagCloud.data('url') + '?tag=' + tagCloud.data('current'));
  }

  function updateError() {
    alert(templates.tagsUpdateError);
  }

  function getTags(el) {
    return el.find('a').map(function () {
      return $(this).text();
    }).get().join(', ');
  }
}(this, jQuery));
