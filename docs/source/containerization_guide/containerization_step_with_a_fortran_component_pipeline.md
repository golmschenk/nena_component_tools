# Containerization step with a Fortran component pipeline

This tutorial will guide you through the containerization step of a simple Python component. This tutorial assumes you 
have already read the [containerization framework overview guide](./index.md). This tutorial uses [the Fortran component template repository code](https://github.com/golmschenk/nena_minimal_fortran_component_template). This repository is a good starting template for a component that is Python based. 

```{include} ./container_platform_subsection.md
```

## Container environment

The container environment is defined in the `Containerfile` file. Here we see
```dockerfile
FROM python:3.14-slim

WORKDIR /workspace
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gfortran \
    && rm -rf /var/lib/apt/lists/*  # Delete the cached apt files for smaller image size.
RUN pip install --no-cache-dir nena_component_tools cmake
COPY *.py .
COPY *.f90 .
COPY CMakeLists.txt .
RUN cmake -S . -B build -DCMAKE_BUILD_TYPE=RelWithDebInfo
RUN cmake --build build --config RelWithDebInfo

CMD ["python", "./container_loop.py"]
```

The first line, `FROM python:3.14-slim` specifies the base container environment you'll be using. I recommend this base container for all uses unless you have a good reason to choose another container.

The next line `WORKDIR /workspace` creates a directory for your code to work in. Again, unless you have a good reason to change it, this should stay as is.

Then, we have
```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gfortran \
    && rm -rf /var/lib/apt/lists/*  # Delete the cached apt files for smaller image size.
RUN pip install --no-cache-dir nena_component_tools cmake
```
This installs Fortran, the small Python-based containerization framework tool, and CMake for building the code. If you want to use a different verison of the Fortran compiler or a different build tool, you would change these specifications here.

Next, we have
```dockerfile
COPY *.py .
COPY *.f90 .
COPY CMakeLists.txt .
```
which copy over the source code files. You should modify the `COPY` lines to move over any source code and build files your program needs. For example, this container expects you are building your code with CMake, hence the `CMakeLists.txt` file. If you using a `Makefile` that would be moved instead.

Next, perform your build. In this case, we're using CMake to perform the build.
```dockerfile
RUN cmake -S . -B build -DCMAKE_BUILD_TYPE=RelWithDebInfo
RUN cmake --build build --config RelWithDebInfo
```

Finally, we run
```dockerfile
CMD ["python", "./container_loop.py"]
```
This runs the Python loop that passes the task information to Fortran. The `container_loop.py` file uses the containerization framework in a loop. Locally, this will process the events in `input_events`. On the cloud, this will run indefinitely waiting for new events to arrive. In this loop, we are just having Python directly call the Fortran executable from the command line. In many cases, using an programmatic interface (e.g., C-style foreign function interfaces) will provide many benefits (e.g., for debugging). But this excluded from this tutorial to keep the code minimal.

```{include} ./running_the_container_subsection.md
```
