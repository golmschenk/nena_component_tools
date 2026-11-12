import numpy as np
from astropy import units as u

from nena_component_tools.internal.data.votable.column import VOTableColumn
from nena_component_tools.internal.data.votable.metadata_field import VOTableMetadataField
from nena_component_tools.internal.data.votable.table import VOTable


def test_create_votable():
    flux = np.array([1.25, 2.5, 3.75], dtype=np.float64)
    column = VOTableColumn.new(name='flux', ucd='phot.flux', unit=u.Jy, array=flux)
    metadata = VOTableMetadataField.new(
        name='exposure', ucd='time.duration', unit=u.s, value=30.0,
    )

    votable = VOTable.new(metadata_fields=[metadata], columns=[column])

    assert isinstance(votable, VOTable)
    assert len(votable.resources) == 1
    assert len(votable.resources[0].tables) == 1
    table = votable.get_first_table()
    assert len(table.fields) == 1
    field = table.fields[0]
    assert field.name == 'flux'
    assert field.datatype == 'double'
    assert field.ucd == 'phot.flux'
    assert field.unit == u.Jy
    np.testing.assert_array_equal(table.array[field.ID], flux)
    assert len(table.params) == 1
    param = table.params[0]
    assert param.name == 'exposure'
    assert param.value == 30.0
    assert param.ucd == 'time.duration'
    assert param.unit == u.s

    astropy_table = table.to_table()
    assert astropy_table.colnames == ['flux']
    np.testing.assert_array_equal(astropy_table['flux'], flux)
    assert astropy_table['flux'].unit == u.Jy
