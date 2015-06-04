from librarian.utils import lang as mod


def test_rtl_property(*ignored):
    """ RTL property returns True for RTL languages """
    assert not mod.is_rtl('en')
    assert mod.is_rtl('ar')
