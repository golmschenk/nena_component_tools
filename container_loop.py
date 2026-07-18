# TODO: This is just a prototyping template code. Remove it.
from nena_component_tools.internal.task_iterator import get_task_iterator


def main():
    task_iterator = get_task_iterator()
    for task in task_iterator:
        was_successful, output_dictionary = call_sub_pipeline(task.input_dictionary)
        if was_successful:
            task.emit_completion_event(output_dictionary=output_dictionary)
        else:
            task.log_failure(dictionary={'error_message': 'There was a problem.', 'line_number': 42})


if __name__ == '__main__':
    main()
