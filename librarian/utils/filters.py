from bottle_utils.html import urlquote, urlunquote


def safepath_filter(config):
    regexp = r'.*?'

    def to_python(match):
        return urlunquote(match)

    def to_url(path):
        # return urlquote(path)
        # at the moment bottle-utils performs quoting as well
        # until a flag is implemented there to make quoting optional
        # it must not be performed here.
        return path

    return (regexp, to_python, to_url)
