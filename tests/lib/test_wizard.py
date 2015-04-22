import mock
import pytest

import librarian.lib.wizard as mod


@pytest.fixture
def wizard():
    return mod.Wizard('test', 'template.tpl')


@pytest.fixture
def subclassed_wizard():
    class TestWizard(mod.Wizard):
        pass
    return TestWizard('test', 'template.tpl')


@mock.patch.object(mod.Wizard, 'create_wizard')
def test_call(create_wizard, wizard):
    mocked_instance = mock.Mock()
    create_wizard.return_value = mocked_instance
    wizard.test_attr = 1
    wizard()
    wiz_dict = {'name': 'test',
                'template': 'template.tpl',
                'steps': {},
                'test_attr': 1}
    create_wizard.assert_called_once_with('test', 'template.tpl', wiz_dict)
    mocked_instance.dispatch.assert_called_once_with()


def test_wizard_name(subclassed_wizard):
    assert subclassed_wizard.__name__ == 'TestWizard'


@mock.patch.object(mod.Wizard, 'process_current_step')
@mock.patch.object(mod.Wizard, 'start_next_step')
@mock.patch.object(mod.Wizard, 'load_state')
@mock.patch.object(mod, 'request')
def test_dispatch_get(request, load_state, start_next_step,
                      process_current_step, wizard):
    request.method = 'GET'
    wizard.dispatch()

    load_state.assert_called_once_with()
    start_next_step.assert_called_once_with()
    assert not process_current_step.called


@mock.patch.object(mod.Wizard, 'process_current_step')
@mock.patch.object(mod.Wizard, 'start_next_step')
@mock.patch.object(mod.Wizard, 'load_state')
@mock.patch.object(mod, 'request')
def test_dispatch_post(request, load_state, start_next_step,
                       process_current_step, wizard):
    request.method = 'POST'
    wizard.dispatch()

    load_state.assert_called_once_with()
    process_current_step.assert_called_once_with()
    assert not start_next_step.called


def test_id(wizard):
    assert wizard.id == 'wizard_test'


@mock.patch.object(mod, 'request')
def test_load_state_found(request, wizard):
    request.session.get.return_value = {'custom': 'data'}
    wizard.load_state()
    assert wizard.state == {'custom': 'data'}


@mock.patch.object(mod, 'request')
def test_load_state_not_found(request, wizard):
    request.session.get.return_value = None
    wizard.load_state()
    assert wizard.state == {'step': 0, 'data': {}}


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


@mock.patch.object(mod.Wizard, 'wizard_finished')
@mock.patch.object(mod.Wizard, 'next')
def test_start_next_step_wizard_finished(w_next, wizard_finished, wizard):
    wizard.state = {'data': 'state'}
    w_next.side_effect = StopIteration()
    wizard.start_next_step()
    wizard_finished.assert_called_once_with('state')


@mock.patch.object(mod, 'template')
@mock.patch.object(mod.Wizard, 'next')
def test_start_next_step_has_result(w_next, template, wizard):
    mocked_step = mock.Mock()
    mocked_step.return_value = 'partial html'
    w_next.return_value = mocked_step
    wizard.start_next_step()
    mocked_step.assert_called_once_with()
    template.assert_called_once_with('template.tpl', step='partial html')


@mock.patch.object(mod.Wizard, 'start_next_step')
@mock.patch.object(mod.Wizard, 'save_state')
def test_process_current_step_success(save_state, start_next_step, wizard):
    mocked_handler = mock.Mock()
    mocked_handler.return_value = {'some': 'data'}
    wizard.state = {'step': 1, 'data': {}}
    wizard.steps = {1: {'POST': mocked_handler}}
    start_next_step.return_value = 'next step html'

    result = wizard.process_current_step()

    assert result == 'next step html'
    assert wizard.state['step'] == 2
    assert wizard.state['data'][1] == {'some': 'data'}
    start_next_step.assert_called_once_with()
    save_state.assert_called_once_with()


@mock.patch.object(mod, 'template')
def test_process_current_step_has_error(template, wizard):
    partial_html = 'same step partial html with error'
    mocked_handler = mock.Mock()
    mocked_handler.return_value = partial_html
    wizard.state = {'step': 1, 'data': {}}
    wizard.steps = {1: {'POST': mocked_handler}}
    template.return_value = 'whole html with error'

    result = wizard.process_current_step()

    assert result == 'whole html with error'
    template.assert_called_once_with('template.tpl', step=partial_html)


def test_process_current_step_missing_post_handler(wizard):
    wizard.state = {'step': 1, 'data': {}}
    wizard.steps = {1: {}}
    with pytest.raises(mod.MissingStepHandler):
        wizard.process_current_step()


def test_register_step_autoindex(wizard):
    mocked_step = mock.Mock()
    decorator = wizard.register_step('test_step')
    decorator(mocked_step)
    assert len(wizard.steps) == 1
    assert wizard.steps[0] == {'name': 'test_step',
                               'GET': mocked_step,
                               'POST': mocked_step}


def test_register_step_manualindex(wizard):
    mocked_step = mock.Mock()
    decorator = wizard.register_step('test_step', index=3)
    decorator(mocked_step)
    assert len(wizard.steps) == 1
    assert wizard.steps[3] == {'name': 'test_step',
                               'GET': mocked_step,
                               'POST': mocked_step}


def test_register_step_index_conflict(wizard):
    wizard.steps[3] = {'name': 'intruder'}
    mocked_step = mock.Mock()
    assert len(wizard.steps) == 1
    decorator = wizard.register_step('test_step', index=3)
    decorator(mocked_step)
    assert len(wizard.steps) == 2
    assert wizard.steps[4] == {'name': 'intruder'}
    assert wizard.steps[3] == {'name': 'test_step',
                               'GET': mocked_step,
                               'POST': mocked_step}


def test_register_step_invalid_index(wizard):
    mocked_step = mock.Mock()
    decorator = wizard.register_step('test_step', index='idx')
    with pytest.raises(ValueError):
        decorator(mocked_step)

    assert len(wizard.steps) == 0


def test_register_step_invalid_method(wizard):
    mocked_step = mock.Mock()
    decorator = wizard.register_step('test_step', method='PUT')
    with pytest.raises(ValueError):
        decorator(mocked_step)

    assert len(wizard.steps) == 0


def test_create_wizard():
    wizard = mod.Wizard.create_wizard('test', 'template.tpl', {'attr': 1})
    assert wizard.name == 'test'
    assert wizard.template == 'template.tpl'
    assert wizard.attr == 1
