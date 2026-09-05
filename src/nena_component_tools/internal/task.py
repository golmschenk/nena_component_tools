import abc
import logging
from dataclasses import dataclass

from nena_component_tools.internal.event_pipeline_task import EventPipelineTaskMetadata
from nena_component_tools.internal.local_task import LocalTaskMetadata

type JsonType = dict[str, 'JsonType'] | list['JsonType'] | str | int | float | bool | None
type JsonDictionary = dict[str, JsonType]

logger = logging.getLogger(__name__)


@dataclass
class Task(abc.ABC):
    """
    A class representing a pipeline task.
    """
    input_dictionary: JsonDictionary
    _metadata: EventPipelineTaskMetadata | LocalTaskMetadata

    @abc.abstractmethod
    def emit_event(self, output_dictionary: JsonDictionary, mark_task_complete: bool = True) -> None:
        """
        Emits an event from the task.

        :param output_dictionary: The content to include in the event.
        :param mark_task_complete: Whether to mark the event as complete.
        """
        pass

    @abc.abstractmethod
    def log_failure(self, dictionary: JsonDictionary) -> None:
        """
        Logs a failure on the task.

        :param dictionary: A dictionary to include in the failure log.
        """
        pass

