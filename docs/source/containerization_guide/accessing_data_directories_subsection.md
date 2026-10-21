## Accessing data directories

You won't want to package the actual data into the container. For the component to be able to access (either read or
write) data outside of the container, this needs to be explicitly specified. This is specified in the `compose.yml`
file. You can see the `input_events` and `output_events` being mapped to directories from the container's point of view
in:
```yaml
    volumes:
      - ./input_events:/workspace/input_events:ro
      - ./output_events:/workspace/output_events
```

For running your code locally, make input and output data directories available in a similar way. By default, the
containerized code will run within the container's `/workspace/` path, so directories within that can be relatively
accessed with just the directory name. Later, we'll see how to map an S3 bucket to a local directory as well.
