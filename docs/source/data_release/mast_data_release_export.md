# MAST data release export

MAST has specific requirements for data release data. The nena component tools package provides some tooling to make exporting to this data format easier.

More specifically, MAST requires two formats of the data. First, they require a Parquet file with VOTable information embedded in it. Second, they require an AstroPy table export. `nena_component_tools` provides a way to package this data once, and then export this to both formats. MAST does provide a tutorial for manually building both formats yourself, but most of the data is redundant, and much of data will be the same for all RGES products, so `nena_component_tools` handles much of this for you. For reference, links to the manual tutorial, the MAST file naming guide, and the MAST file design guide are provided at the bottom of this page. 

## Building a simple data product file

This section shows how to build a simple data product file. Data products requiring a time and/or reference system are slightly more complex (though not too much so).

`nena_component_tools` provides a `VOTable` class to build the data export format

Use `VOTable.for_rges_data_release()` to add the shared RGES metadata automatically. Supply the six required product-specific metadata fields shown below, plus your data columns. Replace the example metadata values and output filename with those for your product.

```python
from pathlib import Path

import numpy as np
from astropy import units as u

from nena_component_tools.internal.data.votable.column import VOTableColumn
from nena_component_tools.internal.data.votable.metadata_info import VOTableMetadataInfo
from nena_component_tools.internal.data.votable.metadata_param import VOTableMetadataParam
from nena_component_tools.internal.data.votable.table import VOTable

metadata_fields = [
    VOTableMetadataInfo.new(name='ccsp.data_release_id', value='DR1'),
    VOTableMetadataInfo.new(name='file_version', value='v1.0'),
    VOTableMetadataInfo.new(name='target_name', value='example-star'),
    VOTableMetadataInfo.new(name='target_keywords', value='Stars'),
    VOTableMetadataParam.new(name='simulated_flag', value=True, ucd='meta.code', unit=u.dimensionless_unscaled, dtype=boolean),
    VOTableMetadataInfo.new(name='source_observations_id', value='123456789,987654321'),
]
flux = VOTableColumn.new(
    name='flux',
    ucd='phot.flux',
    unit=u.Magnitude,
    array=np.array([1.0, 1.1]),
)
product = VOTable.for_rges_data_release(
    metadata_fields=metadata_fields,
    columns=[flux],
)

product.to_parquet(Path('example.parquet'))
astropy_table = product.to_astropy_table()
```

`VOTableMetadataInfo` stores text metadata, while `VOTableMetadataParam` stores typed values, such as the boolean `simulated_flag`. Each column needs a name, a Unified Content Descriptor (`ucd`) describing its meaning, an Astropy unit, and a NumPy array. The data type is inferred from the array, and all columns must have the same number of rows.

`to_parquet()` writes the data with embedded VOTable XML, Astropy `table_meta_yaml`, and file-level metadata. `to_astropy_table()` returns an `astropy.table.Table` with the file-level metadata in its `.meta` dictionary.

## Building a light curve data product file

This section shows how to build a light curve data product file, including a time system.

Use `VOTableTimeColumn` for observation times so that they reference a time system. Continuing from the example above, reuse `metadata_fields` and `flux` and add a time column:

```python
from astropy.io.votable.tree import TimeSys

from nena_component_tools.internal.data.votable.time_column import VOTableTimeColumn

time_system = TimeSys(
    ID='observation_time',
    timeorigin='MJD-origin',
    timescale='UTC',
    refposition='TOPOCENTER',
    config={'version_1_4_or_later': True},
)
time = VOTableTimeColumn.new(
    name='time',
    ucd='time.epoch',
    unit=u.day,
    time_system=time_system,
    array=np.array([60000.0, 60001.0]),
)
light_curve = VOTable.for_rges_data_release(
    metadata_fields=metadata_fields,
    columns=[time, flux],
)

light_curve.to_parquet(Path('light_curve.parquet'))
astropy_table = light_curve.to_astropy_table()
```

Here the times are Modified Julian Dates in days, on the UTC scale, referenced to the observing location (`TOPOCENTER`). Set the origin, scale, and reference position to match your data. The `config` argument enables Astropy's VOTable 1.4 time-system support. The exporter adds the time system to the VOTable metadata and links the time column to it automatically.

## Reference links

* [Manual MAST data product file creation tutorial](https://github.com/spacetelescope/ccsp_supplement/blob/main/notebooks/workflow_demo2/workflow_demo2_rendered.ipynb) (You shouldn't need to do this manual version. If something is missing from the `nena_component_tools` export, please open an issue.)
* [MAST data product file naming guide](https://outerspace.stsci.edu/pages/viewpage.action?pageId=356669709&spaceKey=ISWG&title=File%2BNaming%2Bfor%2BPITs)
* [MAST data product file design guide](https://outerspace.stsci.edu/pages/viewpage.action?pageId=356669707&spaceKey=ISWG&title=File%2BDesign%2Bfor%2BPITs)
