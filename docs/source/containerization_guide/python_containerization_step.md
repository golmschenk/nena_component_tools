# Python containerization step

This tutorial will guide you through the containerization step of a simple Python component. This tutorial assumes you 
have already read the [containerization framework overview guide](./index.md). This tutorial uses [the Python component template repository code](https://github.com/golmschenk/nena_minimal_python_component_template). This repository is a good starting template for a component that is Python based. 

```{include} ./container_platform_subsection.md
```

## Container environment

The container environment is defined in the `Containerfile` file. Here we see
```dockerfile
FROM python:3.14-slim

WORKDIR /workspace
COPY pyproject.toml .
COPY *.py .
RUN pip install --no-cache-dir .

CMD ["python", "./container_loop.py"]
```

The first line, `FROM python:3.14-slim` specifies the base container environment you'll be using. I recommend this base container for all uses unless you have a good reason to choose another container.

The next line `WORKDIR /workspace` creates a directory for your code to work in. Again, unless you have a good reason to change it, this should stay as is.

Next we have
```dockerfile
COPY pyproject.toml .
COPY *.py .
```
which copy over the source code files. `pyproject.toml` and `pylock.toml` are the modern versions of `requirements.txt`. You should modify the `COPY` lines to move over any source code your program needs. For example, if you more properly structure your Python code in [a `src`-based file structure](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/), you should include `COPY src ./src`.

Next, with
```dockerfile
RUN pip install --no-cache-dir .
```
we are installing our package along with its dependencies. While I would recommend setting up your Python code as an installable package, this is not required. You can instead run the `pip install` for your dependencies and move over the source files to be called directly.

Finally, we run
```dockerfile
CMD ["python", "./container_loop.py"]
```
This runs the main program loop. The `container_loop.py` file uses the containerization framework in a loop. Locally, this will process the events in `input_events`. On the cloud, this will run indefinitely waiting for new events to arrive.

## Running the container locally

To run this container on your local machine, first be certain your container platform is running (e.g., Docker Desktop). Then, from the root directory of the project, run
```shell
docker compose up --build --force-recreate
```
This will run through the mock JSON events in `input_events` and output JSON files to the `output_events` directory.