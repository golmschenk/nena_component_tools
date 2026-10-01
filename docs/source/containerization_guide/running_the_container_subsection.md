## Running the container locally

To run this container on your local machine, first be certain your container platform is running (e.g., Docker Desktop). Then, from the root directory of the project, run
```shell
docker compose up --build --force-recreate
```
This will run through the mock JSON events in `input_events` and output JSON files to the `output_events` directory.
