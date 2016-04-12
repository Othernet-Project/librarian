from bottle_utils.html import urlquote, urlunquote


def safepath_filter(config):
    regexp = r'.*?'

    def to_python(match):
        return urlunquote(match.group())

    def to_url(path):
        return urlquote(path)

    return (regexp, to_python, to_url)
