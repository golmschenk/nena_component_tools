# TODO: This was an auto generated test file. It's gross. It needs to be significantly reworked.

import json
import logging
from pathlib import Path

import pytest

from nena_component_tools.internal.environment_constants import DeploymentType
from nena_component_tools.task_iterator import create_task_iterator


def add_numbers(input_dictionary):
    try:
        return True, {'sum': input_dictionary['a'] + input_dictionary['b']}
    except KeyError as error:
        return False, {'error_message': f'Missing input: {error.args[0]}'}


def run_component_pipeline():
    for task in create_task_iterator():
        was_successful, output_dictionary = add_numbers(task.input_dictionary)
        if was_successful:
            task.emit_event(output_dictionary=output_dictionary)
        else:
            task.log_failure(dictionary=output_dictionary)


@pytest.fixture
def input_events_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr('nena_component_tools.internal.task_iterator.DEPLOYMENT_TYPE', DeploymentType.LOCAL)
    input_directory = tmp_path / 'input_events'
    input_directory.mkdir()
    return input_directory


def test_task_iterator_processes_two_json_inputs(input_events_directory: Path):
    (input_events_directory / 'first.json').write_text(json.dumps({'a': 2, 'b': 3}))
    (input_events_directory / 'second.json').write_text(json.dumps({'a': -4, 'b': 10}))

    run_component_pipeline()

    output_directory = input_events_directory.parent / 'output_events'
    assert len(list(output_directory.glob('*.json'))) == 2
    for input_stem, expected_sum in [('first', 5), ('second', 6)]:
        output_paths = list(output_directory.glob(f'*_from_{input_stem}.json'))
        assert len(output_paths) == 1
        assert json.loads(output_paths[0].read_text()) == {'sum': expected_sum}


def test_task_iterator_outputs_error_message(
    input_events_directory: Path, caplog: pytest.LogCaptureFixture,
):
    input_dictionary = {'a': 2}
    (input_events_directory / 'missing_number.json').write_text(json.dumps(input_dictionary))

    with caplog.at_level(logging.ERROR, logger='nena_component_tools.internal.local_task'):
        run_component_pipeline()

    failure_records = [
        record for record in caplog.records
        if record.name == 'nena_component_tools.internal.local_task'
        and record.levelno == logging.ERROR
    ]
    assert len(failure_records) == 1
    assert json.loads(failure_records[0].getMessage()) == {
        'input_event_path': str(Path('input_events') / 'missing_number.json'),
        'input_dictionary': input_dictionary,
        'component_report_dictionary': {'error_message': 'Missing input: b'},
    }
    assert not list((input_events_directory.parent / 'output_events').glob('*.json'))
