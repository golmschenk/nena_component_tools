# Python containerization step

This tutorial will guide you through the containerization step of a simple Python component. This tutorial assumes you 
have already read the [containerization framework overview guide](./index.md).

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
