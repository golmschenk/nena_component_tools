# Python containerization step

This tutorial will guide you through the containerization step of a simple Python component. This tutorial assumes you 
have already read the [containerization framework overview guide](./index.md). This tutorial uses [the Python component template repository code](https://github.com/golmschenk/nena_minimal_python_component_template). This repository is a good starting template for a component that is Python based. 

## Understanding containers and the container platform

A container is mostly just an isolated environment for your code to run in. The main point is that you're creating a
fully defined environment, separate from your local system environment, so the container will run the same when you 
move it to some other system.

To run the containers on your local machine, we'll need container platform software. We'll be using Docker for this.
The containers will run in small Linux environments. For this to work, you need a Linux container engine. If your
local OS is already Linux, you don't need to do anything here. On macOS and Windows, we'll need a piece of software for
this part. Most RGES users should use [Docker Desktop](https://www.docker.com/products/docker-desktop/) for this. The
major exception is those running on a government machine. If you are running on a government machine, instead, you
should use [Rancher Desktop](https://rancherdesktop.io). The reasoning is that Docker Desktop is the most stable and
polished option, and the free license is usable for academic or open-source work. But Docker Desktop has a special
exception that a license must be purchased for government work (including any work on a government machine).
Regardless of the choice between Docker Desktop and Rancher Desktop, we're never going to interact with these directly.
They are just going to run the container platform in the background. We'll be using the Docker CLI (which has no
license restrictions). So choose the appropriate option of the two above, install it, and make sure it's running
whenever you run Docker CLI commands.

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