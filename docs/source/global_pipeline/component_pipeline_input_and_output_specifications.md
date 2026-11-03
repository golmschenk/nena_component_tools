# Component pipeline input and output specifications

_If you have any questions, others probably do as well. Ask working group 14 to clarify with additional documentation._

## Summary

If you are creating a component pipeline that will run in the global pipeline, this document explains how you should 
provide the specifications of the inputs and outputs to your pipeline. For any component pipeline that will be run 
during season 1, these specifications are required by November 13.

## Overview of required specifications

As noted in [the containerization guide](../containerization_guide/containerization_framework_overview.md), your
component pipeline should expect a JSON input and access to a directory to read other input data files from. It should
also spit out a JSON output and will have access to a directory to write other data files output to. The 
containerization framework will give and take Python dictionaries instead of you directly writing the JSON, but it's
worth thinking in terms of JSON, as the framework locally will still read from and write to JSON files on your machine. 
Your inputs will come from another component pipeline, so you won't be defining these files. That said, we still want 
ensure all the inputs for each component pipeline are being produced by another pipeline. So you need to at least state 
what you are expecting.

## Creating a component pipeline entry

Go to [the component pipeline input/output confluence page](https://rgespit.atlassian.net/wiki/x/A4DYT) and copy either the "blank" example or the 
"example_pipeline_name" example. And fill in the entries for your own component pipeline. The remainder of document 
hopes to clarify questions regarding this.

## Output file considerations

The output files can be anything as long as the downstream groups that use your data are okay with the format. That 
said, we have general recommendations for these files. For choice of format, typically, a more restrictive format is 
better. Ones where the structure of the data inside the file is determined by the file type are usually ideal. For 
example, in a Parquet file, there's very little question about the structure of the main data. That means there's less 
users need to learn about your data and less ways they can make mistakes. Parquet is being widely used throughout 
Roman products, is efficient both in terms of IO and file size. For high dimensional data or multiple data arrays with 
shared coordinates, Zarr (possibly through Xarray) can be an excellent choice. ASDF and FITS is bit more 
flexible, meaning that more documentation is needed to explain what's inside of it, but they are still perfectly 
acceptable. Avoid making up your own format. Arbitrary text formats that you have created are among the worst options. 
They're both inefficient in terms of IO and filesize, but they also do not have an ecosystem of readers and writers that 
prevent malformed data and handle edge cases. There are data format developers that have spent their lives making 
great formats and all the necessary tooling around them. Except in extremely rare circumstances, you will likely not 
create something better than them for your purposes.

## Output JSON EventBridge message

Whenever you're producing something that can be used by a downstream group, you should produce an EventBridge message. 
This will let downstream groups know that new data is available that they can start running their component pipeline 
on. This can be as simple as the paths to the data files you produced. But it can also include more information. This 
is particularly if it's useful for downstream groups to filter whether they want to do something with that specific 
output without needing to go look for a large data file. The EventBridge message should be in the form of a JSON 
dictionary. The containerization framework can will be used to go from Python dictionaries to JSON, though. You can
include any information here you want, with the limitation that it should be a small amount of data per message. 
You should not make messages larger than 100KB. 
