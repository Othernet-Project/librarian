"""
.. module:: bottle_utils.meta
   :synopsis: Social metadata

.. moduleauthor:: Outernet Inc <hello@outernet.is>
"""

from __future__ import unicode_literals

from bottle import request

from .common import *


class MetaBase(object):
    """
    Base class for metadata. This class is a simple placeholder to collect base
    functionality for various subclasses.

    Currently, the only functionality this base class provides is calling
    :py:meth:`~bottle_utils.meta.MetaBase.render` method when ``__str__()``
    magic method is called on the class.
    """

    def render(self):
        """
        Render the meta object into HTML. In the base class this method
        renders to empty string.

        :returns:   HTML representation of the object
        """
        return ''

    def __str__(self):
        return self.render()


class SimpleMetadata(MetaBase):
    """
    The basic (classic) metadata. This class is used to render title tag and
    description meta tag.

    Both title and description are option. If neither is supplied, it is
    rendered into empty string.

    Here is a simple example handler::

        @app.get('/my/shareable/page')
        @bottle.view('page')
        def handler():
            m = SimpleMetadata(title='My page',
                               description='A page about sharing')
            return dict(meta=m)

    In the template, simply render this object in ``<head>`` section where you
    would normally have the ``<title>`` tag.::

        <html>
            <head>
                <meta charset="utf-8">
                {{! meta }}
            </head>
            <body>
            ...
            </body>
        </html>

    :param title:           title
    :param description:     description
    """
    def __init__(self, title='', description=''):
        self.title = title
        self.description = description

    @staticmethod
    def meta(attr, name, value):
        """
        Render a generic ``<meta>`` tag. This function is the basis for
        rendering most of the social meta tags.

        The arguments are rendered like this::

            <meta $attr=$name content=$value>

        :param attr:    attribute name used for tag name
        :param name:    tag name
        :param value:   tag value
        :returns:       HTML markup for the meta tag
        """
        return '<meta %s="%s" content="%s">' % (attr, attr_escape(name),
                                                attr_escape(value))

    def simple(self, name, value):
        """
        Render a simple 'name' meta tag. This function renders a meta tag that
        uses the 'name' attribute.

        The arguments are rendered like this::

            <meta name=$name content=$value>

        :param name:    tag name
        :param value:   tag value
        """
        return self.meta('name', name, value)


    def render(self):
        """
        Render the meta object into HTML.

        :returns:   HTML representation of the object
        """
        s = ''
        if self.title:
            s += '<title>%s</title>' % html_escape(self.title)
        if self.description:
            s += self.simple('description', self.description)
        return super(SimpleMetadata, self).render() + s


class Metadata(SimpleMetadata):
    """
    Complete set of social meta tags. This class renders a complete set of
    social meta tags including `schema.org <http://schema.org/>`_ properties,
    `OpenGraph tags <https://developers.facebook.com/docs/opengraph>`, and
    `Twitter Cards markup
    <https://dev.twitter.com/docs/cards/markup-reference>`.

    The meta tags are only rendered for the property that is specified (i.e.,
    one or more of the title, description, thumbnail, url). The properties have
    following meanings:

    - title: page title
    - description: page description (usually used as message shown next to the
      post on a social network)
    - thumbnail: (also known as 'image') appears as a thumbnail or banner
      alongside the post on a social network
    - url: canonical URL of the page (usually an URL that does not include any
      query parameters that change it's appearance or generate unnecessary
      data, such as Google Analytics campaign tags, etc), which is used instead
      of the URL that was shared

    To render social tags, simply instantiate an object using meta data of your
    choosing and render the object in template.

    Here is an example of what it may look like in a handler function::

        @app.get('/my/shareable/page')
        @bottle.view('page')
        def handler():
            m = Metadata(title='My page',
                         description='A page about sharing',
                         thumbnail='/static/images/awesome.png',
                         url=bottle.request.path)
            return dict(meta=m)

    And here is a template::

        <html>
            <head>
                <meta charset="utf-8">
                {{! meta }}
            </head>
            <body>
            ....
            </body>
        </html>

    Don't forget to prevent escaping of the rendered HTML by using ``{{! }}``
    syntax instead of ``{{ }}``.

    This class does not render any of the other numerous tags (authorship tags,
    for instance). However, the instance methods it provides can be used to
    render them.

    For example, to render a Twitter creator tag in a template that has access
    to any instance of this class::

        {{! meta.twitterprop('creator', '@OuternetForAll') }}

    When it comes to thumbnails and canonical URLs, the social networks usually
    expect to see a full URL (including scheme and hostname). However, it may
    not feel right to hard-code these things. This class automatically converts
    paths to full URLs based on request data, so passing paths is fine.

    :param title:           page title
    :param description:     page description
    :param thumbnail:       path or full URL to thumbnail image
    :param url:             path or full canonical URL of the page
    """
    def __init__(self, title='', description='', thumbnail='', url=''):
        super(Metadata, self).__init__(title, description)
        if (not thumbnail) or thumbnail.startswith('http'):
            self.thumbnail = thumbnail
        self.thumbnail = thumbnail and self.make_full(thumbnail) or ''
        self.url = url and self.make_full(url) or ''

    @staticmethod
    def make_full(url):
        """
        Convert an input to full URL if not already a full URL. This static
        method will ensure that the specified url is a full URL.

        This method only checks if the provided URL starts with 'http', though,
        so it is possible to trick it using a path that looks like 'httpfoo':
        it is clearly not a full URL, but will be treated as one. If the input
        value is user-supplied, please perform a more through check.

        Under the hood, this method uses
        :py:func:`bottle_utils.common.full_url` to convert paths to full URLs.

        :param url:     path or full URL
        :returns:       full URL as per request data
        """
        if (not url) or url.startswith('http'):
            return url
        return full_url(url)

    def prop(self, namespace, name, value):
        """
        Render a generic property meta tag. This method renders a generic
        property meta tags that uses ``property`` attribute to designate the
        tag name.

        Each tag name consists of two parts: namespace and name. Most notably,
        OpenGraph uses this form with 'og' namespace.

        The arguments are rendered like this::

            <meta property=$namespace:$name content=$value>

        :param namespace:   property namespace
        :param name:        property name
        :param value:       tag value
        """
        prop_name = '%s:%s' % (attr_escape(namespace), attr_escape(name))
        return self.meta('property', prop_name, value)

    def nameprop(self, namespace, name, value):
        """
        Render a generic name property. This method renders a generic name
        property meta tag that uses ``name`` attribute to designate the tag
        name.

        Each tag name consist of namespace and name parts. Most notably,
        Twitter Card markup uses this form.

        The arguments are rendered like this::

            <meta name=$namespace:$name content=$value>

        :param namespace:   property namespace
        :param name:        property name
        :param value:       tag value
        """
        prop_name = '%s:%s' % (attr_escape(namespace), attr_escape(name))
        return self.meta('name', prop_name, value)

    def itemprop(self, name, value):
        """
        Render schema.org itemprop meta tag. This method renders a schema.org
        itemprop meta tag which uses the ``itemprop`` attribute to designate
        the name of the tag.

        This form is used by Google, but it's otherwise an open standard for
        semantic markup. This method only renders meta tags, and not every
        other kind of markup that schema.org uses.

        The arguments are rendered into the following markup::

            <meta itemprop=$name content=$value>

        :param name:    tag name
        :param value:   tag value
        """
        return self.meta('itemprop', name, value)

    def twitterprop(self, name, value):
        """
        Renders Twitter Card markup. This method renders Twitter Card markup
        meta data. That is a name property meta tag with 'twitter' namespace.

        The arguments are rendered like so::

            <meta name=twitter:$name content=$value>

        :param name:    property name
        :param value:   tag value
        """
        return self.nameprop('twitter', name, value)

    def ogprop(self, name, value):
        """
        Renders OpenGraph meta tag. This method renders a property meta tag
        that uses 'og' namespace.

        The arguments are rendered like this::

            <meta property=og:$name content=$value>

        :param name:    property name
        :param value:   tag value
        """
        return self.prop('og', name, value)

    def render(self):
        """
        Render the meta object into HTML.

        :returns:   HTML representation of the object
        """
        s = ''
        if self.title:
            s += self.ogprop('title', self.title)
            s += self.twitterprop('title', self.title)
            s += self.itemprop('name', self.title)
        if self.description:
            s += self.ogprop('description', self.description)
            s += self.twitterprop('description', self.description)
            s += self.itemprop('description', self.description)
        if self.thumbnail:
            s += self.ogprop('image', self.thumbnail)
            s += self.twitterprop('image', self.thumbnail)
            s += self.itemprop('image', self.thumbnail)
        if self.url:
            s += self.ogprop('url', self.url)
            s += self.twitterprop('url', self.url)
            s += self.itemprop('url', self.url)
        return super(Metadata, self).render() + s

