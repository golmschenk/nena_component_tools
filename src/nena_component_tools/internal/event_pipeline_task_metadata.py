from dataclasses import dataclass


@dataclass
class EventPipelineTaskMetadata:
    """
    Metadata for a task in the event-driven pipeline.
    """
    input_message_queue_url: str
    input_message_receipt_handle: str
    input_message_id: str
    output_event_correlation_id: str
    output_event_causation_id: str
