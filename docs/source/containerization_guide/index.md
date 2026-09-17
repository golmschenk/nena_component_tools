# Containerization framework overview

You have a component pipeline that's going to run as part of the global fully automated-pipeline in the cloud. The containerization framework is designed to make containerizing your component pipeline as easy as possible. It allows you to build and test your code locally in a way that directly mocks how it will work when running in the cloud infrastructure.

## The bit of the cloud infrastructure you should know

```{image} event_conceptual_overview.png
:width: 800px
```

Within the global pipeline, your component pipeline will be triggered by events. You get to pick which event streams you're subscribed to. For example, the microlensing modeling group will subscribe to new light curve events. That is, each time an upstream component pipeline produces a new light curve, it will emit a new event saying "Hey! There's a new light curve. You can find it here.", and the modeling group's pipeline will trigger based on these new events coming in. Events are passed around in a JSON format. The event content will also usually point to some form of storage (e.g., where the light curve was saved to). Once an event like this pops up, a box will automatically start running your component pipeline. Your component pipeline will get this JSON message, and your code will do whatever it needs to do (e.g., run modeling on the light curve). Then, your pipeline can also save results to storage and emit its own events.

## How the framework allows you to develop locally

The framework allows you to easily mock this event system. When you run your code locally, the framework will read events from a set of JSON files in a local directory, as though these were incoming events. It also gives you a command to send off events, which will be put into JSON files in another directory. When it gets moved to cloud infrastructure, the framework will automatically read from and write to real live event streams instead. This is designed to make it easy for you to test things locally while having it ready for cloud use.

```{image} event_local_vs_cloud_conceptual_overview.png
:width: 800px
```

## Basic usage

We'll go into more detail soon, but the basic use case is relatively simple. In this basic example we assume your component pipeline consists of a Python function. Don't worry, we handle other cases elsewhere, but this makes for a very simple example. First, we import your component pipeline function and a function from the framework that gives us events.

```python
from nena_component_tools.task_iterator import create_task_iterator
from component_pipeline import pipeline_function
```

From here, we just iterate over the incoming events, passing the contents of the JSON as a Python dictionary to our pipeline function.
```python
task_iterator = create_task_iterator()
for task in task_iterator:
    output_dictionary = pipeline_function(task.input_dictionary)
    task.emit_event(output_dictionary=output_dictionary)
```

On your local machine, this will read JSON files from an `input_events` directory and expose them as a Python dictionary using `task.input_dictionary`. That dictionary is passed to your pipeline function. Then, you can take the output of the pipeline and emit your own event. Locally, those events will be saved as JSON files in an `output_events` directory. Once this gets deployed to the cloud infrastructure, it will automatically switch over to using real event streams.

If your pipeline code is just some simple code that reads `a` and `b` from the event, then spits out a new event containing the sum at `c`, it might look like this.
```python
def pipeline_function(input_dictionary):
    a = input_dictionary['a']
    b = input_dictionary['b']
    c = a + b
    output_dictionary = {'c': c}
    return output_dictionary
```

When you run the code locally, if you have a JSON file in your `input_events` directory that looks like
```json
{
  "a": 1,
  "b": 2
}
```
running this code will leave you with a JSON file in your `output_events` directory that looks like
```json
{
  "c": 3
}
```

We still need to containerize the code, but that little task iterator wrapper is the only bit of actual code that needs to be added to make this process loop over incoming events and test such events locally.
