from librarian.utils import patch_content as mod


def test_patch_adds_style_link():
    """ HTML should be patched with style link """
    html = """<html>
    <head></head>
    <body>foo</body>
    </html>"""
    size, patched = mod.patch(html)
    assert patched == """<html>
    <head>%s</head>
    <body>foo</body>
    </html>""" % mod.STYLE_LINK
    assert size == len(patched)


def test_add_head_if_missing():
    """ Even if <head> tag is missing, add it """
    html = """<html>
    <body>foo</body>
    </html>"""
    patched = mod.patch(html)[1]
    assert patched == """<html><head>%s</head>
    <body>foo</body>
    </html>""" % mod.STYLE_LINK


def test_add_html_if_missing():
    """ When <html> tag is missing, add it """
    html = "<body>foo</body>"
    patched = mod.patch(html)[1]
    assert patched == "<html><head>%s</head><body>foo</body></html>" % (
        mod.STYLE_LINK)

