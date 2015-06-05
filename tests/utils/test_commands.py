import mock

from librarian.utils import commands as mod


@mock.patch.object(mod, 'sys')
def test_get_config_path(sys):
    samples = {
        '--conf=test.ini': 'test.ini',
        "--conf='test.ini'": 'test.ini',
        '--conf="test.ini"': 'test.ini',
        '--conf test.ini': 'test.ini',
        '--conf /path/to/file-test.ini': '/path/to/file-test.ini',
        '--conf=/path/to/file-test.ini': '/path/to/file-test.ini',
        "--conf='/path/to/file-test.ini'": '/path/to/file-test.ini',
        '--conf="/path/to/file-test.ini"': '/path/to/file-test.ini',
        '--conf c:\path\\to\mis leading': 'c:\path\\to\mis',
    }
    for (value, expected) in samples.items():
        sys.argv = ['cmd', '-t', '--flag', '--var="te st"', value, '--var2=3']
        result = mod.get_config_path()
        assert result == expected
