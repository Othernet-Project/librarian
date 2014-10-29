"""
.. module:: bottle_utils.html
   :synopsis: Functions for use in HTML templates

.. moduleauthor:: Outernet Inc <hello@outernet.is>
"""

from __future__ import unicode_literals

import types
import functools

try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote


from decimal import Decimal
from bottle import request, html_escape
from dateutil.parser import parse

from .common import *


SIZES = 'KMGTP'
FERR_CLS = 'form-errors'
FERR_ONE_CLS = 'form-error'
ERR_CLS = 'field-error'


# DATA FORMATTING


def plur(word, n, plural=lambda n: n != 1,
         convert=lambda w, p: w + 's' if p else w):
    """
    Pluralize word based on number of items. This function provides rudimentary
    pluralization support. It is quite flexible, but not a replacement for
    functions like ``ngettext``.

    This function takes two optional arguments, ``plural()`` and ``convert()``,
    which can be customized to change the way plural form is derived from the
    original string. The default implementation is a naive version of English
    language plural, which uses plural form if number is not 1, and derives the
    plural form by simply adding 's' to the word. While this works in most
    cases, it doesn't always work even for English.

    The ``plural(n)`` function takes the value of the ``n`` argument and its
    return value is fed into the ``convert()`` function. The latter takes the
    source word as first argument, and return value of ``plural()`` call as
    second argument, and returns a string representing the pluralized word.
    Return value of the ``convert(w, p)`` call is returned from this function.

    Here are some simple examples::

        >>> plur('book', 1)
        'book'
        >>> plur('book', 2)
        'books'

        # But it's a bit naive
        >>> plur('box', 2)
        'boxs'

    The latter can be fixed like this::

        >>> exceptions = ['box']
        >>> def pluralize(word, is_plural):
        ...    if not is_plural:
        ...        return word
        ...    if word in exceptions:
        ...        return word + 'es'
        ...    return word + 's'
        >>> plur('book', 2)
        'books'
        >>> plur('box', 2, convert=pluralize)
        'boxes'

    :param word:    string to pluralize
    :param n:       number of items from which to calculate plurals
    :param plural:  function that returns true if the plural form should be
                    used
    :param convert: function that converts the string to plural
    :returns:       word in appropriate form
    """
    return convert(word, plural(n))


def hsize(size, unit='B', step=1024):
    """
    Given size in unit produce size with human-friendly units. This is a simple
    formatting function that takes a value, a unit in which the value is
    expressed, and the size of multiple (kilo, mega, giga, etc).

    This function rounds values to 2 decimal places and does not handle
    fractions. It also uses metric prefixes (K, M, G, etc) and only goes up to
    Peta (P, quadrillion) prefix.

    The size multiple (``step`` parameter) is 1024 by default, suitable for
    expressing values related to size of data on disk.

    Example::

        >>> hsize(12)
        '12.00 B'
        >>> hsize(1030)
        '1.01 KB'
        >>> hsize(1536)
        '1.50 KB'
        >>> hsize(2097152)
        '2.00 MB'

    :param size:    size in base units
    :param unit:    base unit without prefix
    :param step:    size of the multiple
    :returns:       appropriate units
    """
    size = Decimal(size)
    order = -1
    while size > step:
        size /= step
        order += 1
    if order < 0:
        return '%.2f %s' % (round(size, 2), unit)
    return '%.2f %s%s' % (round(size, 2), SIZES[order], unit)


def trunc(s, chars):
    """
    Trucante string at ``n`` characters. This function hard-trucates a string
    at specified number of characters and appends an elipsis to the end.

    The truncating does not take into account words or markup. Elipsis is not
    appended if the string is shorter than the specified number of characters.
    ::

        >>> trunc('foobarbaz', 6)
        'foobar...'

    .. note::

       Keep in mind that the trucated string is always 3 characters longer than
       ``n`` because of the appended elipsis.

    :param s:       input string
    :param chars:   number of characters
    :returns:       truncated string
    """
    if len(s) <= chars:
        return s
    return s[:chars] + '...'


def yesno(val, yes='yes', no='no'):
    """
    Return ``yes`` or ``no`` depending on value. This function takes the value
    and returns either yes or no depending on whether the value evaluates to
    ``True``.

    Examples::

        >>> yesno(True)
        'yes'
        >>> yesno(False)
        'no'
        >>> yesno(True, 'available', 'not available')
        'available'

    :param val:     value to test
    :param yes:     string representation of 'yes'
    :param no:      string representation of 'no'
    :returns:       yes string or no string
    """
    return yes if val else no


def strft(ts, fmt):
    """
    Reformat string datestamp/timestamp. This function parses a string
    representation of a date and/or time and reformats it using specified
    format.

    The format is standard strftime format used in Python's
    ``datetime.datetime.strftime()`` call.

    Actual parsing of the input is delegated to
    `python-dateutil <https://pypi.python.org/pypi/python-dateutil>`_ library.

    :param ts:  input datestamp/timestamp
    :param fmt: output format
    :returns:   reformatted datestamp/timestamp
    """
    return parse(ts).strftime(fmt)


# HTML


def attr(name, value=None):
    """
    Render HTML attribute. This function is used as part of
    :py:func:`~bottle_utils.html.tag` function to render HTML attributes, but
    can be used on its own as well. It converts the value into Unicode string
    and sanitizes it before returning the markup.

    Basic usage may look like this::

        >>> attr('src': '/images?src=foo.png&w=12')
        'src="/images?src=foo.png&amp;w=12"'

    All attribute values are double-quoted and any double quotes found inside
    the value are escaped. User-supplied values can be used reasonably safely.

    If the value is ``None``, only the attribute name is rendered, otherwise a
    normal 'attribute="value"' pair is returned::

        >>> attr('src', None)
        'src'
        >>> attr('src', '')
        'src=""'

    Therefore, to suppress attribute values completely (i.e., not even have the
    ``=""`` part, use ``None`` as the value.

    :param name:    attribute name
    :param value:   optional attribute value
    :returns:       correctly rendered attribute-value pair or attribute name
    """
    if value is not None:
        value = to_unicode(value)
        value = attr_escape(value)
        return '%s="%s"' % (name, value)
    return name


def tag(name, content='', nonclosing=False, **attrs):
    """
    Wraps content in a HTML tag with optional attributes. This function
    provides a Pythonic interface for writing HTML tags with a few bells and
    whistles.

    The basic usage looks like this::

        >>> tag('p', 'content', _class="note", _id="note1")
        '<p class="note" id="note1">content</p>'

    Any attribute names with any number of leading underscores (e.g., '_class')
    will have the underscores strpped away.

    If content is an iterable, the tag will be generated once per each member.

        >>> tag('span', ['a', 'b', 'c'])
        '<span>a</span><span>b</span><span>c</span>'

    It does not sanitize the tag names, though, so it is possible to specify
    invalid tag names::

        >>> tag('not valid')
        '<not valid></not valid>

    Please ensure that ``name`` argument does not come from user-specified
    data, or, if it does, that it is properly sanitized (best way is to use a
    whitelist of allowed names).

    Because attributes are specified using keyword arguments, which are then
    treated as a dictionary, there is no guarantee of attribute order. If
    attribute order is important, don't use this function.

    This module contains a few partially applied aliases for this function.
    These mostly have hard-wired first argument (tag name), and are all
    uppercase:

    - ``A`` - alias for ``<a>`` tag
    - ``BUTTON`` - alias for ``<button>`` tag
    - ``HIDDEN`` - alias for ``<input>`` tag with ``type="hidden"`` attribute
    - ``INPUT`` - alias for ``<input>`` tag with ``nonclosing`` set to ``True``
    - ``LI`` - alias for ``<li>`` tag
    - ``OPTION`` - alias for ``<option>`` tag
    - ``P`` - alias for ``<p>`` tag
    - ``SELECT`` - alias for ``<select>`` tag
    - ``SPAN`` - alias for ``<span>`` tag
    - ``SUBMIT`` - alias for ``<button>`` tag with ``type="submit"`` attribute
    - ``TEXTAREA`` - alias for ``<textarea>`` tag
    - ``UL`` - alias for ``<ul>`` tag

    :param name:    tag name
    :param content: tag content
    :param attrs:   optional tag attributes
    :returns:       HTML of the tag with its content and attributes
    """
    open_tag = '<%s>' % name
    close_tag = '</%s>' % name
    attrs = ' '.join([attr(k.lstrip('_'), to_unicode(v)) for k, v in attrs.items()])
    if attrs:
        open_tag = '<%s %s>' % (name, attrs)
    if nonclosing:
        content = ''
        close_tag = ''
    if not isinstance(content, basestring):
        try:
            return ''.join(['%s%s%s' % (open_tag, to_unicode(c), close_tag)
                            for c in content])
        except TypeError:
            pass
    return '%s%s%s' % (open_tag, to_unicode(content), close_tag)


SPAN = functools.partial(tag, 'span')
UL = functools.partial(tag, 'ul')
LI = functools.partial(tag, 'li')
P = functools.partial(tag, 'p')
A = functools.partial(tag, 'a')
INPUT = functools.partial(tag, 'input', nonclosing=True)
BUTTON = functools.partial(tag, 'button')
SUBMIT = functools.partial(BUTTON, _type='submit')
HIDDEN = lambda n, v: INPUT(_name=n, value=v, _type='hidden')
TEXTAREA = functools.partial(tag, 'textarea')
BUTTON = functools.partial(tag, 'button')
OPTION = functools.partial(tag, 'option')
SELECT = functools.partial(tag, 'select')


def vinput(name, values, **attrs):
    """
    Render input with bound value. This function can be used to bind values to
    form inputs. By default it will result in HTML markup for a generic input.
    The generated input has a ``name`` attribute set to specified name, and
    an ``id`` attribute that has the same value.
    ::
        >>> vinput('foo', {})
        '<input name="foo" id="foo">'

    If the supplied dictionary of field values contains a key that matches the
    specified name (case-sensitive), the value of that key will be used as the
    value of the input::

        >>> vinput('foo', {'foo': 'bar'})
        '<input name="foo" id="foo" value="bar">'

    All values are properly sanitized before they are added to the markup.

    Any additional keyword arguments that are passed to this function are
    passed on the the :py:func:`~bottle_utils.html.tag` function. Since the
    generated input markup is for generic text input, some of the other usual
    input types can be specified using ``_type`` parameter::

        >>> input('foo', {}, _type='email')
        '<input name="foo" id="foo" type="email">'

    :param name:    field name
    :param values:  dictionary or dictionary-like object containing field
                    values
    :returns:       HTML markup for the field with bound value
    """
    attrs.setdefault('_id', name)
    value = values.get(name)
    if value is None:
        return INPUT(_name=name, **attrs)
    return INPUT(_name=name, value=value, **attrs)


def varea(name, values, **attrs):
    """
    Render textarea with bound value. Textareas use a somewhat different markup
    to that of regular inputs, so a separate function is used for binding
    values to this form control.::

        >>> varea('foo', {'foo': 'bar'})
        '<textarea name="foo" id="foo">bar</textarea>'

    This function works the same way as :py:func:`~bottle_utils.html.vinput`
    function, so please look at it for more information. The primary difference
    is in the generated markup.

    :param name:    field name
    :param values:  dictionary or dictionary-like object containing field
                    values
    :returns:       HTML markup for the textarea with bound value
    """
    attrs.setdefault('_id', name)
    value = values.get(name)
    if value is None:
        return TEXTAREA(_name=name, **attrs)
    return TEXTAREA(value, _name=name, **attrs)


def vcheckbox(name, value, values, default=False, **attrs):
    """
    Render checkbox with bound value. This function renders a checkbox which is
    checked or unchecked depending on whether its own name-value combination
    appears in the provided form values dictionary.

    Because there are many ways to think about checkboxes in general, this
    particular function may or may not work for you. It treats checkboxes as a
    list of alues which are all named the same.

    Let's say we have markup that looks like this::

        <input type="checkbox" name="foo" value="1">
        <input type="checkbox" name="foo" value="2">
        <input type="checkbox" name="foo" value="3">

    If user checks all of them, we consider it a list ``foo=['1', '2', '3']``.
    If user checks only the first and last, we have ``foo=['1', '3']``. And so
    on.

    This function assumes that you are using  this pattern.

    The ``values`` map can either map the checkbox name to a single value, or a
    list of multiple values. In the former case, if the single value matches
    the value of the checkbox, the checkbox is checked. In the latter case, if
    value of the checkbox is found in the list of values, the checkbox is
    checked.::

        >>> vcheckbox('foo', 'bar', {'foo': 'bar'})
        '<input type="checkbox" name="foo" id="foo" value="bar" checked>'
        >>> vcheckbox('foo', 'bar', {'foo': ['foo', 'bar', 'baz']})
        '<input type="checkbox" name="foo" id="foo" value="bar" checked>'
        >>> vcheckbox('foo', 'bar', {'foo': ['foo', 'baz']})
        '<input type="checkbox" name="foo" id="foo" value="bar">'

    When the field values dictionary doesn't contain a key that matches the
    checkbox name, the value of ``default`` keyword argument determines whether
    the checkbox should be checked::

        >>> vcheckbox('foo', 'bar', {}, default=True)
        '<input type="checkbox" name="foo" id="foo" value="bar" checked>'

    :param name:    field name
    :param value:   value of the checkbox
    :param values:  dictionary or dictionary-like object containing field
    :param default: default state when input is not bound (``True`` for
                    checked)
    :returns:       HTML markup for the checkbox with bound value
    """
    attrs.setdefault('_id', name)
    if name in values:
        try:
            values = values.getall(name)
        except AttributeError:
            values = values.get(name, [])
        if isinstance(values, basestring):
            if unicode(value) == unicode(values):
                attrs['checked'] = None
        elif unicode(value) in [unicode(v) for v in values]:
            attrs['checked'] = None
    elif default:
        if default:
            attrs['checked'] = None
    elif 'checked' in attrs:
        del attrs['checked']
    return INPUT(_type='checkbox', _name=name, value=value, **attrs)


def vselect(name, choices, values, empty=None, **attrs):
    """
    Render select list with bound value. This function renders the select list
    with option elements with appropriate element selected based on field
    values that are passed.

    The values and labels for option elemnets are specified using an iterable
    of two-tuples::

        >>> vselect('foo', ((1, 'one'), (2, 'two'),), {})
        '<select name="foo" id="foo"><option value="1">one</option><option...'

    There is no mechanism for default value past what browsers support, so you
    should generally assume that most browsers will render the select with
    frist value preselected. Using an empty string or ``None`` as option value
    will render an option element without value::

        >>> vselect('foo', ((None, '---'), (1, 'one'),), {})
        '<select name="foo" id="foo"><option value>---</option><option val...'
        >>> vselect('foo', (('', '---'), (1, 'one'),), {})
        '<select name="foo" id="foo"><option value="">---</option><option ...'

    When specifying values, keep in mind that only ``None`` is special, in that
    it will crete a ``value`` attribute without any value. All other Python
    types become strings in the HTML markup, and are submitted as such. You
    will need to convert the values back to their appropriate Python type
    manually.

    If the choices iterable does not contain an element representing the empty
    value (``None``), you can specify it using the ``empty`` parameter. The
    argument for ``empty`` should be a label, and the matching value is
    ``None``. The emtpy value is always inseted at the beginning of the list.

    :param name:    field name
    :param choices: iterable of select list choices
    :param values:  dictionary or dictionary-like object containing field
    :param empty:   label for empty value
    :returns:       HTML markup for the select list with bound value
    """
    attrs.setdefault('_id', name)
    value = values.get(name)
    options = []
    for val, label in choices:
        if unicode(val) == unicode(value):
            options.append(OPTION(label, value=val, selected=None))
        else:
            options.append(OPTION(label, value=val))
    if empty:
        options.insert(0, OPTION(empty, value=None))
    return SELECT(''.join(options), _name=name, **attrs)


def form(method=None, action=None, csrf=False, multipart=False, **attrs):
    """
    Render open form tag. This function renders the open form tag with
    additional features, such as faux HTTP methods, CSRF token, and multipart
    support.

    All parameters are optional. Using this function without any argument has
    the same effect as naked form tag without any attributes.

    Method names can be either lowercase or uppercase.

    The methods other than GET and POST are faked using a hidden input with
    ``_method`` name and uppercase name of the HTTP method. The form will use
    POST method in this case. Server-side support is required for this feature
    to work.

    Any additional keyword arguments will be used as attributes for the form
    tag.

    :param method:      HTTP method (GET, POST, PUT, DELETE, PATCH, etc)
    :param action:      action attribute
    :param csrf:        include CSRF protection token
    :param multipart:   make the form multipart
    """
    method = method and method.upper()
    if not method:
        faux_method = False
    elif method in ['GET', 'POST']:
        attrs['method'] = method
        faux_method = False
    else:
        attrs['method'] = 'POST'
        faux_method = True
    if multipart:
        attrs['enctype'] = 'multipart/form-data'
    if action is not None:
        attrs['action'] = action
    s = tag('form', nonclosing=True, **attrs)
    if faux_method:
        s += HIDDEN('_method', method)
    if csrf:
        # Import csrf_tag here to avoid circular dependency, since the csrf
        # module uses functions from this module
        from .csrf import csrf_tag
        s += csrf_tag()
    return s


def link_other(label, url, path, wrapper=SPAN, **kwargs):
    """
    Only wrap label in anchor if given URL is not the path. Given a label, this
    function will match the page URL against the path to which the label should
    point, and generate the anchor element markup as necessary.

    Any additional keyword arguments are passed to the function that generates
    the anchor markup, which is ``A`` alias for
    :py:func:`~bottle_utils.html.tag` function.

    If the URLs match (meaning the page URL matches the target path), the label
    will be passed to the wrapper function. The default wrapper function is
    :py:func:`~bottle_utils.html.SPAN`, so the label is wrapped in SPAN tag
    when the URLs matches.::

        >>> link_other('foo', '/here', '/there')
        '<a href="/target">foo</a>'
        >>> link_other('foo', '/there', '/there')
        '<span>foo</span>'

    You can customize the appearance of the label in the case URLs match by
    customizing the wrapper::

        >>> link_other('foo', '/there', '/there',
        ...            wrapper=lambda l, **kw: l + 'bar')
        'foobar'

    Note that the wrapper lambda function has wild-card keyword arguments. The
    wrapper function accepts the same extra keyword arguments that the anchor
    function does, so if you have common classes and similar attributes, you
    can specify them as extra keyword arguments and use any of the helper
    functions in this module.::

        >>> link_other('foo', '/here', '/there', wrapper=BUTTON, _class='cls')
        '<a class="cls" href="/target">foo</a>'
        >>> link_other('foo', '/there', '/there', wrapper=BUTTON, _class='cls')
        '<button class="cls">foo</button>'

    :param label:   label of the link
    :param url:     URL to which label should be linked
    :param path:    path to test URL against
    :param wrapper: function that should be used to wrap the label if URL
                    matches the path (i.e., anchor is not being rendered)
    """
    if url == path:
        return wrapper(label, **kwargs)
    return A(label, href=url, **kwargs)


def field_error(name, errors):
    """
    Renders error message for single form field. This function renders a
    standardized markup for individual form field errors.

    .. note::

       This is not a generic helper function like the other ones. It's more of
       an opinion on how error messages should be rendered, and it has no
       particular rationale behind it rather than 'This is how I do things'.
       The reason it is included here is that having consistent markup for form
       errors tends to increase the speed at which we are able to implement
       interfaces.

    For the error messages the render, the error dictionary must contain a key
    that matches the specified key. The key may map to a single string value or
    an iterable containing strings. Depending on how many error messages there
    are, one or more of span elements will be rendered. Every span will have
    'field-error' class.

    :param name:    name of the field to look up in the dict
    :param errors:  dict-like object containing field-name-message mappings
    :returns:       HTML of the error message if one is found, otherwise empty
                    string
    """
    try:
        return SPAN(html_escape(errors[name]), _class=ERR_CLS)
    except KeyError:
        return ''


def form_errors(errors):
    """
    Renders a form error. This function renders a standardized markup for form
    errors in your template.

    Please see notes for :py:func:`~bottle_utils.html.field_error` for the
    reasoning behind this helper function.

    Input dictionary must contain a special key '_' which is treated as key for
    form-wide errors that are not specific to any field. The value can either
    be a single string or an iterable of strings.

    Errors are always rendered as unordered list with each error message as
    list item, even when there is only one error. The list items always have
    the 'form-error' class, and the unordered list has the 'form-errors' class.

    For example::

        >>> form_errors({'_': 'Ouch!'})
        '<ul class="form-errors"><li class="form-error">Ouch!</li></ul>'
        >>> form_errors({'_': ['Ouf!', 'Pain!']})
        '<ul class="form-errors"><li class="form-error">Ouf!</li><li clas...'

    :param errors:  dictionary or dictionary-like object containing field
                    name-error mappings
    """
    try:
        return UL(LI(html_escape(errors['_']), _class=FERR_ONE_CLS),
                  _class=FERR_CLS)
    except KeyError:
        return ''
    except TypeError:
        return P(SPAN(html_escape(errors['_']), _class=FERR_ONE_CLS),
                 _class=FERR_CLS)


def to_qs(mapping):
    """
    Convert a mapping object to query string appended to current path. This
    function takes a ``bottle.MultiDict`` object or a ``dict``-like object that
    supports ``items()`` call, and converts it to a query string appeneded to
    the path in the current request context.

    The values for each parameter is encoded as UTF-8 and escaped.

    :param mapping:     ``bottle.MultiDict`` or ``dict``-like object
    :returns:           current path with query string built from given mapping
    """
    try:
        pairs = mapping.allitems()
    except AttributeError:
        pairs = mapping.items()
    return request.path + '?' + '&'.join(
        ['%s=%s' % (k, quote(v.encode('utf8'))) for k, v in pairs])


def add_qparam(param, value):
    """
    Add query string parameter on current path in request context.

    The return value of this function is current request path with parameter
    appended.

    :param param:   parameter name
    :param value:   value for the parameter
    :returns:       path with query string parameter added
    """
    params = request.query.decode()
    params.append(param, unicode(value))
    return to_qs(params)


def set_qparam(param, value):
    """
    Replace query string parameter on current path in request context.

    The return value of this function is current request path with parameter
    replaced.

    :param param:   parameter name
    :param value:   value for the parameter
    :returns:       path with query string parameter replaced
    """
    params = request.query.decode()
    params.replace(param, unicode(value))
    return to_qs(params)


def del_qparam(param):
    """
    Remove query string parameter on current path in request context.

    The return value of this function is current request path with parameter
    appended.

    :param param:   parameter name
    :returns:       path with query string parameter removed
    """
    params = request.query.decode()
    try:
        del params[param]
    except KeyError:
        pass
    return to_qs(params)

