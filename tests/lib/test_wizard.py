import mock
import pytest

import librarian.lib.wizard as mod


@pytest.fixture
def wizard():
    return mod.Wizard('test')


@pytest.fixture
def subclassed_wizard():
    class TestWizard(mod.Wizard):
        pass
    return TestWizard('test')


@pytest.fixture
def backable_wizard():
    class TestWizard(mod.Wizard):
        allow_override = True
    return TestWizard('test')


@mock.patch.object(mod.Wizard, 'create_wizard')
def test_call(create_wizard, wizard):
    mocked_instance = mock.Mock()
    create_wizard.return_value = mocked_instance
    wizard.test_attr = 1
    wizard()
    wiz_dict = {'name': 'test', 'steps': {}, 'test_attr': 1, 'state': None}
    create_wizard.assert_called_once_with('test', wiz_dict)
    mocked_instance.dispatch.assert_called_once_with()


def test_wizard_name(subclassed_wizard):
    assert subclassed_wizard.__name__ == 'TestWizard'


@mock.patch.object(mod.Wizard, 'process_current_step')
@mock.patch.object(mod.Wizard, 'start_next_step')
@mock.patch.object(mod.Wizard, 'override_next_step')
@mock.patch.object(mod.Wizard, 'remove_gaps')
@mock.patch.object(mod.Wizard, 'skip_needless_steps')
@mock.patch.object(mod.Wizard, 'get_needed_steps')
@mock.patch.object(mod.Wizard, 'load_state')
@mock.patch.object(mod, 'request')
def test_dispatch_get(request, load_state, get_needed_steps,
                      skip_needless_steps, remove_gaps, override_next_step,
                      start_next_step, process_current_step, wizard):
    request.method = 'GET'
    load_state.return_value = True
    get_needed_steps.return_value = [1, 4, 5]
    wizard.state = {}
    wizard.dispatch()

    get_needed_steps.assert_called_once_with()
    load_state.assert_called_once_with()
    skip_needless_steps.assert_called_once_with([1, 4, 5])
    remove_gaps.assert_called_once_with()
    override_next_step.assert_called_once_with()
    start_next_step.assert_called_once_with()
    assert not process_current_step.called


@mock.patch.object(mod.Wizard, 'process_current_step')
@mock.patch.object(mod.Wizard, 'start_next_step')
@mock.patch.object(mod.Wizard, 'override_next_step')
@mock.patch.object(mod.Wizard, 'remove_gaps')
@mock.patch.object(mod.Wizard, 'skip_needless_steps')
@mock.patch.object(mod.Wizard, 'get_needed_steps')
@mock.patch.object(mod.Wizard, 'load_state')
@mock.patch.object(mod, 'request')
def test_dispatch_post(request, load_state, get_needed_steps,
                       skip_needless_steps, remove_gaps, override_next_step,
                       start_next_step, process_current_step, wizard):
    request.method = 'POST'
    load_state.return_value = False
    wizard.state = {'needed_steps': [1, 2]}
    wizard.dispatch()

    load_state.assert_called_once_with()
    skip_needless_steps.assert_called_once_with([1, 2])
    remove_gaps.assert_called_once_with()
    override_next_step.assert_called_once_with()
    process_current_step.assert_called_once_with()
    assert not start_next_step.called


def test_id(wizard):
    assert wizard.id == 'wizard_test'


@mock.patch.object(mod, 'request')
def test_load_state_found(request, wizard):
    request.session.get.return_value = {'custom': 'data'}
    created = wizard.load_state()
    assert not created
    assert wizard.state == {'custom': 'data'}


@mock.patch.object(mod, 'request')
def test_load_state_not_found(request, wizard):
    request.session.get.return_value = None
    created = wizard.load_state()
    assert created
    assert wizard.state == {'step': 0, 'data': {}}


@mock.patch.object(mod, 'request')
def test_load_state_not_found_custom_start_index(request):
    class CustomWizard(mod.Wizard):
        start_index = 4

    custom_wizard = CustomWizard('custom')
    request.session.get.return_value = None
    created = custom_wizard.load_state()
    assert created
    assert custom_wizard.state == {'step': 4, 'data': {}}


@mock.patch.object(mod, 'request')
def test_save_state(request, wizard):
    test_state = {'custom': 'state'}
    wizard.state = test_state
    wizard.save_state()
    request.session.__setitem__.assert_called_once_with(wizard.id, test_state)


def test_next_success(wizard):
    wizard.state = {'step': 1}
    wizard.steps = {1: {'GET': 'get_handler'}}
    step = next(wizard)
    assert step == 'get_handler'


def test_next_no_more_steps(wizard):
    wizard.state = {'step': 1}
    with pytest.raises(StopIteration):
        next(wizard)


def test_next_missing_get_handler(wizard):
    wizard.state = {'step': 1}
    wizard.steps = {1: {}}
    with pytest.raises(mod.MissingStepHandler):
        next(wizard)


@mock.patch.object(mod, 'request')
def test_override_next_step_not_allowed(request, wizard):
    request.params = {wizard.step_param: 1}
    wizard.steps = {1: {}, 2: {}}
    wizard.state = {'step': 2}
    assert wizard.allow_override is False
    wizard.override_next_step()
    assert wizard.state['step'] == 2


@mock.patch.object(mod, 'request')
def test_override_next_step_no_param_sent(request, backable_wizard):
    request.params = {}
    backable_wizard.steps = {1: {}, 2: {}}
    backable_wizard.state = {'step': 2}
    assert backable_wizard.allow_override is True
    backable_wizard.override_next_step()
    assert backable_wizard.state['step'] == 2


@mock.patch.object(mod, 'request')
def test_override_next_step_invalid_param_sent(request, backable_wizard):
    request.params = {backable_wizard.step_param: 'aa'}
    backable_wizard.steps = {1: {}, 2: {}}
    backable_wizard.state = {'step': 2}
    assert backable_wizard.allow_override is True
    backable_wizard.override_next_step()
    assert backable_wizard.state['step'] == 2


@mock.patch.object(mod, 'request')
def test_override_next_step_not_existing_step(request, backable_wizard):
    request.params = {backable_wizard.step_param: 10}
    backable_wizard.steps = {1: {}, 2: {}}
    backable_wizard.state = {'step': 2}
    assert backable_wizard.allow_override is True
    backable_wizard.override_next_step()
    assert backable_wizard.state['step'] == 2


@mock.patch.object(mod, 'request')
def test_override_next_step_invalid_step(request, backable_wizard):
    request.params = {backable_wizard.step_param: 3}
    backable_wizard.steps = {1: {}, 2: {}, 3: {}}
    backable_wizard.state = {'step': 2}
    assert backable_wizard.allow_override is True
    backable_wizard.override_next_step()
    assert backable_wizard.state['step'] == 2


@mock.patch.object(mod, 'request')
def test_override_next_step_ok(request, backable_wizard):
    request.params = {backable_wizard.step_param: 1}
    backable_wizard.steps = {1: {}, 2: {}, 3: {}}
    backable_wizard.state = {'step': 2}
    assert backable_wizard.allow_override is True
    backable_wizard.override_next_step()
    assert backable_wizard.state['step'] == 1


@mock.patch.object(mod, 'request')
@mock.patch.object(mod.Wizard, 'wizard_finished')
@mock.patch.object(mod.Wizard, 'next')
def test_start_next_step_wizard_finished(w_next, wizard_finished, request,
                                         wizard):
    request.params = {'step': 1}
    wizard.state = {'data': 'state'}
    w_next.side_effect = StopIteration()
    wizard.start_next_step()
    wizard_finished.assert_called_once_with('state')


@mock.patch.object(mod, 'request')
@mock.patch.object(mod.Wizard, 'template_func')
@mock.patch.object(mod.Wizard, 'next')
def test_start_next_step_has_result(w_next, template, request, wizard):
    request.params = {'step': 1}
    mocked_step = mock.Mock()
    mocked_step.return_value = {'some': 'param'}
    wizard.state = {'step': 1}
    wizard.steps[1] = {'name': 'test', 'GET': {'handler': mocked_step}}
    w_next.return_value = {'handler': mocked_step, 'template': 'step_tmp.tpl'}
    wizard.start_next_step()
    mocked_step.assert_called_once_with()
    template.assert_called_once_with('step_tmp.tpl',
                                     some='param',
                                     step_index=1,
                                     step_count=1,
                                     step_param='step',
                                     step_name='test',
                                     start_index=0)


@mock.patch.object(mod, 'request')
@mock.patch.object(mod, 'redirect')
@mock.patch.object(mod.Wizard, 'next')
def test_start_next_step_has_result_no_step(w_next, redirect, request, wizard):
    request.params = {}
    request.fullpath = '/wizard/'
    wizard.state = {'step': 1}
    wizard.start_next_step()
    redirect.assert_called_once_with('/wizard/?step=1')


@mock.patch.object(mod, 'redirect')
@mock.patch.object(mod, 'request')
@mock.patch.object(mod.Wizard, 'save_state')
def test_process_current_step_success(save_state, request, redirect):
    class TestWizard(mod.Wizard):
        allow_override = True

    wizard = TestWizard('testw')
    mocked_handler = mock.Mock()
    mocked_handler.return_value = {'some': 'data', 'successful': True}
    wizard.state = {'step': 1, 'data': {}}
    wizard.steps = {1: {'POST': {'handler': mocked_handler,
                                 'template': 'step_tmp.tpl'}}}
    redirect.return_value = 302
    request.fullpath = '/path/to/wizard/'

    result = wizard.process_current_step()

    assert result == 302
    assert wizard.state['step'] == 2
    assert wizard.state['data'][1] == {'some': 'data'}
    redirect.assert_called_once_with('/path/to/wizard/?step=2')
    save_state.assert_called_once_with()


@mock.patch.object(mod.Wizard, 'template_func')
def test_process_current_step_has_error(template, wizard):
    mocked_handler = mock.Mock()
    mocked_handler.return_value = {'successful': False, 'errors': {'_': '1'}}
    wizard.state = {'step': 1, 'data': {}}
    wizard.steps = {1: {'name': 'test',
                        'POST': {'handler': mocked_handler,
                                 'template': 'step_tmp.tpl'}}}
    template.return_value = 'whole html with error'

    result = wizard.process_current_step()

    assert result == 'whole html with error'
    template.assert_called_once_with('step_tmp.tpl',
                                     errors={'_': '1'},
                                     step_index=1,
                                     step_count=1,
                                     step_param='step',
                                     step_name='test',
                                     start_index=0)


def test_process_current_step_missing_post_handler(wizard):
    wizard.state = {'step': 1, 'data': {}}
    wizard.steps = {1: {}}
    with pytest.raises(mod.MissingStepHandler):
        wizard.process_current_step()


def test_register_step_autoindex(wizard):
    mocked_step = mock.Mock()
    test_func = lambda: True
    decorator = wizard.register_step('test_step',
                                     'step_tmp.tpl',
                                     test=test_func)
    decorator(mocked_step)
    assert len(wizard.steps) == 1
    assert wizard.steps[0] == {'name': 'test_step',
                               'test': test_func,
                               'GET': {'handler': mocked_step,
                                       'template': 'step_tmp.tpl'},
                               'POST': {'handler': mocked_step,
                                        'template': 'step_tmp.tpl'}}


def test_register_step_autoindex_separate_handlers(wizard):
    mocked_step_get = mock.Mock()
    mocked_step_post = mock.Mock()
    test_func = lambda: True
    decor = wizard.register_step('test_step',
                                 'step_tmp1.tpl',
                                 method='GET',
                                 test=test_func)
    decor(mocked_step_get)
    decor = wizard.register_step('test_step',
                                 'step_tmp2.tpl',
                                 method='POST',
                                 test=test_func)
    decor(mocked_step_post)
    assert len(wizard.steps) == 1
    assert wizard.steps[0] == {'name': 'test_step',
                               'test': test_func,
                               'GET': {'handler': mocked_step_get,
                                       'template': 'step_tmp1.tpl'},
                               'POST': {'handler': mocked_step_post,
                                        'template': 'step_tmp2.tpl'}}


def test_register_step_manualindex(wizard):
    mocked_step = mock.Mock()
    test_func = lambda: True
    decorator = wizard.register_step('test_step',
                                     'step_tmp.tpl',
                                     index=3,
                                     test=test_func)
    decorator(mocked_step)
    assert len(wizard.steps) == 1
    assert wizard.steps[3] == {'name': 'test_step',
                               'test': test_func,
                               'GET': {'handler': mocked_step,
                                       'template': 'step_tmp.tpl'},
                               'POST': {'handler': mocked_step,
                                        'template': 'step_tmp.tpl'}}


def test_register_step_index_conflict(wizard):
    wizard.steps[3] = {'name': 'intruder'}
    mocked_step = mock.Mock()
    test_func = lambda: True
    assert len(wizard.steps) == 1
    decorator = wizard.register_step('test_step',
                                     'step_tmp.tpl',
                                     index=3,
                                     test=test_func)
    decorator(mocked_step)
    assert len(wizard.steps) == 2
    assert wizard.steps[4] == {'name': 'intruder'}
    assert wizard.steps[3] == {'name': 'test_step',
                               'test': test_func,
                               'GET': {'handler': mocked_step,
                                       'template': 'step_tmp.tpl'},
                               'POST': {'handler': mocked_step,
                                        'template': 'step_tmp.tpl'}}


def test_register_step_invalid_index(wizard):
    mocked_step = mock.Mock()
    decorator = wizard.register_step('test_step', 'step_tmp.tpl', index='idx')
    with pytest.raises(ValueError):
        decorator(mocked_step)

    decorator = wizard.register_step('test_step', 'step_tmp.tpl', index=-3)
    with pytest.raises(ValueError):
        decorator(mocked_step)

    assert len(wizard.steps) == 0


def test_register_step_invalid_method(wizard):
    mocked_step = mock.Mock()
    decorator = wizard.register_step('test_step', 'step_tmp.tpl', method='PUT')
    with pytest.raises(ValueError):
        decorator(mocked_step)

    assert len(wizard.steps) == 0


def test_register_step_invalid_test(wizard):
    mocked_step = mock.Mock()
    decorator = wizard.register_step('test_step', 'step_tmp.tpl', test='fake')
    with pytest.raises(TypeError):
        decorator(mocked_step)


def test_remove_gaps(wizard):
    wizard.steps = {1: 'first', 3: 'second', 8: 'third'}
    wizard.remove_gaps()
    assert wizard.steps == {0: 'first', 1: 'second', 2: 'third'}


def test_remove_gaps_custom_start_index():
    class CustomWizard(mod.Wizard):
        start_index = 3

    custom_wizard = CustomWizard('custom')
    custom_wizard.steps = {1: 'first', 3: 'second', 8: 'third'}
    custom_wizard.remove_gaps()
    assert custom_wizard.steps == {3: 'first', 4: 'second', 5: 'third'}


def test_get_needed_steps(wizard):
    fails = lambda: False
    passes = lambda: True
    wizard.steps = {0: {'name': 'first'},
                    1: {'test': fails},
                    2: {'name': 'ok'},
                    3: {'test': passes}}
    steps = wizard.get_needed_steps()
    assert steps == [0, 2, 3]


def test_skip_needless_steps(wizard):
    wizard.steps = {0: {'name': 'first'},
                    1: {'test': 'second'},
                    2: {'name': 'ok'},
                    3: {'test': 'fourth'}}
    wizard.skip_needless_steps(needed_steps=[1, 2])
    assert wizard.steps == {1: {'test': 'second'},
                            2: {'name': 'ok'}}


def test_create_wizard():
    wizard = mod.Wizard.create_wizard('test', {'attr': 1})
    assert wizard.name == 'test'
    assert wizard.attr == 1


def test_create_wizard_class_attrs():
    class WizardA(mod.Wizard):
        step_param = 'steppa'
        allow_override = True
        start_index = 1

    class WizardB(mod.Wizard):
        step_param = 'current'
        allow_override = True
        start_index = 2

    wiz_a = WizardA.create_wizard('testa', {'attr': 1})
    wiz_b = WizardB.create_wizard('testb', {'attr': 1})

    assert wiz_a.step_param == 'steppa'
    assert wiz_a.allow_override is True
    assert wiz_a.start_index == 1

    assert wiz_b.step_param == 'current'
    assert wiz_b.allow_override is True
    assert wiz_b.start_index == 2


def test_attr_inheritance():
    class WizardA(mod.Wizard):
        allow_override = True
        start_index = 1

    class WizardB(mod.Wizard):
        allow_override = True
        start_index = 2

    w = mod.Wizard('base')
    wa = WizardA('a')
    wb = WizardB('b')

    assert w.allow_override is False
    assert w.start_index == 0

    assert wa.allow_override is True
    assert wa.start_index == 1

    assert wb.allow_override is True
    assert wb.start_index == 2
