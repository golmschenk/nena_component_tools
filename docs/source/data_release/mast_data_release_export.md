# MAST data release export

MAST has specific requirements for data release data. The nena component tools package provides some tooling to make exporting to this data format easier.

More specifically, MAST requires two formats of the metadata included in the Parquet footer data. First, they require a VOTable version of the metadata. Second, they require an AstroPy table YAML version. `nena_component_tools` provides a way to package this data once, and then export this to both formats. MAST does provide a tutorial for manually building both formats yourself, but most of the data is redundant, and much of data will be the same for all RGES products, so `nena_component_tools` handles much of this for you. For reference, links to the manual tutorial, the MAST file naming guide, and the MAST file design guide are provided at the bottom of this page. 

## Building a simple data product file

This section shows how to build a simple data product file. Data products requiring a time and/or reference system are slightly more complex (though not too much so).

`nena_component_tools` provides a `VOTable` class and a `for_rges_data_release` method to build the data export format. There are a few required fields you must add (in addition to anything you *want* to add). 

Below is a minimal example adding the required fields and a data column.

```python
from pathlib import Path

import numpy as np
from astropy import units
from nena_component_tools.votable import VOTable, VOTableMetadataInfo, VOTableMetadataParam, VOTableColumn

metadata_fields = [
    VOTableMetadataInfo.new(name='ccsp.data_release_id', value='DR1'),
    VOTableMetadataInfo.new(name='file_version', value='v1.0'),
    VOTableMetadataInfo.new(name='target_name', value='111111111'),
    VOTableMetadataParam.new(name='simulated_flag', value=True, ucd='meta.code',
                             unit=units.dimensionless_unscaled, dtype=bool),
    VOTableMetadataInfo.new(name='source_observations_id', value='123456789,987654321'),
]
masses = VOTableColumn.new(name='mass', ucd='phys.mass', unit=units.kg,
                           array=np.array([1.0, 1.1, 1.0]))
votable = VOTable.for_rges_data_release(
    metadata_fields=metadata_fields,
    columns=[masses],
)

output_path = Path('example.parquet')
votable.to_parquet(output_path)
```

## Building a light curve data product file

This section shows how to build a light curve data product file, including a time system, RA, and Dec.

Any data that requires epoch-based time should include a time system object. This will be built with AstroPy's votable
tree `TimeSys` class. This is then passed to a special `VOTableTimeColumn`. This ensures the column in the table is 
automatically linked to the time system saved in the metadata. Don't worry much about the `ID` field of the time system,
it will automatically be renamed by `VOTable`. Multiple time systems are allowed. `timeorigin` is the offset in JD
the  time values will be considered from (e.g., `2400000.5` enable MJD times). `timescale` can be set to [any of the
values listed here](https://www.ivoa.net/rdf/timescale/2019-03-15/timescale.html). `refposition` to 
[any of the values listed here](https://www.ivoa.net/rdf/refposition/2019-03-15/refposition.html).

MAST only allows a single VOTable coordinate system option. Specifically, ICRS (as 
`CooSys(ID='ref.votable.coosys', system='ICRS', epoch=None, equinox=None)`). As such, you do not need to add this 
yourself. If you include a RA or Dec entry (marked with the appropriate UCD), VOTable will automatically link this
with a coordinate system.

```python
from pathlib import Path

import numpy as np
from astropy import units
from astropy.io.votable.tree import TimeSys
from nena_component_tools.votable import (VOTable, VOTableMetadataInfo, VOTableMetadataParam,
                                          VOTableColumn, VOTableTimeColumn)

metadata_fields = [
    VOTableMetadataInfo.new(name='ccsp.data_release_id', value='DR1'),
    VOTableMetadataInfo.new(name='file_version', value='v1.0'),
    VOTableMetadataInfo.new(name='target_name', value='111111111'),
    VOTableMetadataParam.new(name='simulated_flag', value=True, ucd='meta.code',
                             unit=units.dimensionless_unscaled, dtype=bool),
    VOTableMetadataInfo.new(name='source_observations_id', value='123456789,987654321'),
    VOTableMetadataParam.new(name='target_coordinates.ra', value=270.0,
                             ucd='pos.eq.ra', unit=units.deg, dtype=float),
    VOTableMetadataParam.new(name='target_coordinates.dec', value=-30.0,
                             ucd='pos.eq.dec', unit=units.deg, dtype=float),
]
time_system = TimeSys(ID='ref.votable.timesys', timeorigin='2400000.5',
                      timescale='UTC', refposition='TOPOCENTER')
times = VOTableTimeColumn.new(name='time', ucd='time.epoch', unit=units.day,
                              time_system=time_system, array=np.array([100.0, 101.0, 102.]))
fluxes = VOTableColumn.new(name='flux', ucd='phot.mag', unit=units.mag,
                           array=np.array([20.0, 20.1, 20.0]))
votable = VOTable.for_rges_data_release(metadata_fields=metadata_fields,
                                        columns=[times, fluxes])

output_path = Path('example.parquet')
votable.to_parquet(output_path)
```

## Listing metadata formats included in a parquet file

As a sanity check, the tools include a simple function to print the metadata types included in a created parquet file.

```python
from pathlib import Path
from nena_component_tools.votable import show_mast_parquet_file_metadata

output_path = Path('example.parquet')
show_mast_parquet_file_metadata(output_path)
```


## Reference links

* [Manual MAST data product file creation tutorial](https://github.com/spacetelescope/ccsp_supplement/blob/main/notebooks/workflow_demo2/workflow_demo2_rendered.ipynb) (You shouldn't need to do this manual version. If something is missing from the `nena_component_tools` export, please open an issue.)
* [MAST data product file naming guide](https://outerspace.stsci.edu/pages/viewpage.action?pageId=356669709&spaceKey=ISWG&title=File%2BNaming%2Bfor%2BPITs)
* [MAST data product file design guide](https://outerspace.stsci.edu/pages/viewpage.action?pageId=356669707&spaceKey=ISWG&title=File%2BDesign%2Bfor%2BPITs)
