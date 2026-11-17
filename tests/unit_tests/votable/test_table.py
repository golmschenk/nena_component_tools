from io import BytesIO

import numpy as np
import pytest
from astropy import units as u
from astropy.io.votable import parse
from astropy.io.votable.tree import TimeSys
from astropy.time import Time

from nena_component_tools.internal.data.votable.column import VOTableColumn
from nena_component_tools.internal.data.votable.metadata_field import VOTableMetadataField
from nena_component_tools.internal.data.votable.metadata_info import VOTableMetadataInfo
from nena_component_tools.internal.data.votable.metadata_param import VOTableMetadataParam
from nena_component_tools.internal.data.votable.table import VOTable
from nena_component_tools.internal.data.votable.time_column import VOTableTimeColumn


RGES_REQUIRED_METADATA = {
    'ccsp.data_release_id': 'DR0',
    'file_version': 'v0.1',
    'target_name': 'alpha',
    'target_keywords': 'Stars',
    'simulated_flag': 'TRUE',
    'source_observations_id': '123456789',
}


def round_trip(votable):
    output = BytesIO()
    votable.to_xml(output)
    output.seek(0)
    return parse(output, verify='exception').get_first_table()


def test_columns_and_metadata_survive_xml_round_trip():
    flux = np.ma.array([1.25, 2.5], mask=[False, True])
    columns = [
        VOTableColumn.new('flux', 'phot.flux', u.Jy, flux, dtype=np.float32),
        VOTableColumn.new('target', 'meta.id', u.dimensionless_unscaled, np.array(['alpha', 'beta'])),
    ]
    metadata: list[VOTableMetadataField] = [
        VOTableMetadataInfo.new('telescope', 'ROMAN'),
        VOTableMetadataParam.new('exposure', 30.0, 'time.duration', u.s, dtype=np.float32),
        VOTableMetadataInfo.new('target_name', 'α Centauri'),
        VOTableMetadataParam.new('ids', np.array([12, 34], dtype=np.int32), 'meta.id', u.dimensionless_unscaled),
        VOTableMetadataParam.new('label', np.str_('observation'), 'meta.id', u.dimensionless_unscaled),
    ]

    votable = VOTable.new(metadata, columns)

    assert isinstance(votable, VOTable)
    table = round_trip(votable)
    assert [field.name for field in table.fields] == ['flux', 'target']
    assert table.fields[0].datatype == 'float'
    assert table.fields[0].ucd == 'phot.flux'
    assert table.fields[0].unit == u.Jy
    np.testing.assert_array_equal(table.array['flux'].mask, flux.mask)
    assert table.array['flux'][0] == flux[0]
    np.testing.assert_array_equal(table.array['target'], columns[1].array)
    assert [param.name for param in table.params] == ['exposure', 'ids', 'label']
    assert table.params[0].datatype == 'float'
    assert table.params[0].value == 30.0
    assert table.params[0].ucd == 'time.duration'
    assert table.params[0].unit == u.s
    np.testing.assert_array_equal(table.params[1].value, [12, 34])
    assert table.params[2].value == 'observation'
    assert [(info.name, info.value) for info in table.infos] == [
        ('telescope', 'ROMAN'), ('target_name', 'α Centauri'),
    ]
    astropy_table = table.to_table()
    assert astropy_table.colnames == ['flux', 'target']
    assert astropy_table['flux'].unit == u.Jy


def test_time_columns_reference_deduplicated_time_systems():
    columns = [
        VOTableTimeColumn.new(
            name, 'time.epoch', u.day,
            TimeSys(ID=name, timeorigin=origin, timescale=scale, refposition='TOPOCENTER',
                    config={'version_1_4_or_later': True}),
            np.array([1.0, 2.0]),
        )
        for name, origin, scale in [
            ('utc', 'MJD-origin', 'UTC'),
            ('utc_copy', 2400000.5, 'UTC'),
            ('tdb', 2400000.5, 'TDB'),
        ]
    ]

    votable = VOTable.new([], columns)
    output = BytesIO()
    votable.to_xml(output)
    output.seek(0)
    parsed = parse(output, verify='exception')
    table = parsed.get_first_table()
    time_systems = parsed.resources[0].time_systems

    assert len(time_systems) == 2
    assert columns[0].time_system is columns[1].time_system
    assert [field.ref for field in table.fields] == [
        'ref.votable.timesys0', 'ref.votable.timesys0', 'ref.votable.timesys1',
    ]
    assert {field.ref for field in table.fields} == {system.ID for system in time_systems}


def test_array_cells_preserve_shape_and_row_count():
    values = np.arange(12, dtype=np.float64).reshape(2, 2, 3)
    columns = [
        VOTableColumn.new('flux', 'phot.flux', u.Jy, values),
        VOTableColumn.new('id', 'meta.id', u.dimensionless_unscaled, np.array([1, 2])),
    ]
    metadata = [VOTableMetadataParam.new('offsets', values[0], 'phot.flux', u.Jy)]

    table = round_trip(VOTable.new(metadata, columns))

    assert len(table.array) == 2
    np.testing.assert_array_equal(table.array['flux'], values)
    np.testing.assert_array_equal(table.params[0].value, values[0])


def test_mismatched_row_counts_are_rejected():
    columns = [
        VOTableColumn.new('first', 'phot.flux', u.Jy, np.ones((2, 3))),
        VOTableColumn.new('second', 'phot.flux', u.Jy, np.ones(6)),
    ]

    with pytest.raises(ValueError, match='Column `second` length does not match `first`'):
        VOTable.new([], columns)


def test_empty_columns():
    assert len(VOTable.new([], []).get_first_table().array) == 0
    column = VOTableColumn.new('flux', 'phot.flux', u.Jy, np.array([], dtype=np.float64))
    table = round_trip(VOTable.new([], [column]))
    assert len(table.fields) == 1
    assert len(table.array) == 0


@pytest.mark.parametrize(('first_kind', 'second_kind'), [
    ('info', 'info'), ('param', 'param'), ('column', 'column'),
    ('info', 'param'), ('info', 'column'), ('param', 'column'),
])
def test_duplicate_field_names_are_rejected(first_kind, second_kind):
    def make_field(kind):
        if kind == 'info':
            return VOTableMetadataInfo.new('shared_name', 'value')
        if kind == 'param':
            return VOTableMetadataParam.new('shared_name', 1.0, 'phot.flux', u.Jy)
        return VOTableColumn.new('shared_name', 'phot.flux', u.Jy, np.array([1.0]))

    fields = [make_field(first_kind), make_field(second_kind)]
    metadata = [field for field in fields if isinstance(field, VOTableMetadataField)]
    columns = [field for field in fields if isinstance(field, VOTableColumn)]

    with pytest.raises(ValueError, match='Duplicate field name: `shared_name`'):
        VOTable.new(metadata, columns)


def test_for_rges_adds_constant_metadata():
    metadata = [
        *[VOTableMetadataInfo.new(name, value) for name, value in RGES_REQUIRED_METADATA.items()],
        VOTableMetadataParam.new('exposure', 30.0, 'time.duration', u.s),
    ]
    columns = [VOTableColumn.new('flux', 'phot.flux', u.Jy, np.array([1.0, 2.0]))]

    votable = VOTable.for_rges_data_release(metadata, columns)

    assert isinstance(votable, VOTable)
    table = round_trip(votable)
    infos = {info.name: info.value for info in table.infos}
    assert Time(infos.pop('file_date'), format='isot').isot
    assert infos == {
        'ccsp.name': 'RGES',
        'ccsp.archive_lead': 'Greg Olmschenk',
        'ccsp.investigator': 'Scott Gaudi',
        'ccsp.doi': '11.11111/xxxx-xxxx',
        'license': 'CC BY 4.0',
        'license_url': 'https://creativecommons.org/licenses/by/4.0/',
        'telescope': 'ROMAN',
        'instrument.name': 'WFI',
        'instrument.optical_element': 'F146,F087,F213',
        'wavelength.band': 'OPTICAL',
        'ccsp.intent': 'SCIENCE',
        'wavelength.minimum': '869',
        'wavelength.maximum': '2125',
        **RGES_REQUIRED_METADATA,
    }
    assert [(param.name, param.value) for param in table.params] == [('exposure', 30.0)]
    np.testing.assert_array_equal(table.array['flux'], columns[0].array)
    assert [field.name for field in metadata] == [*RGES_REQUIRED_METADATA, 'exposure']


@pytest.mark.parametrize('name', ['ccsp.name', 'ccsp.archive_lead', 'ccsp.investigator', 'ccsp.doi', 'file_date'])
@pytest.mark.parametrize('kind', ['info', 'param', 'column'])
def test_for_rges_rejects_constant_name_collisions(name, kind):
    metadata = []
    columns = []
    if kind == 'info':
        metadata.append(VOTableMetadataInfo.new(name, 'custom'))
    elif kind == 'param':
        metadata.append(VOTableMetadataParam.new(name, 1.0, 'phot.flux', u.Jy))
    else:
        columns.append(VOTableColumn.new(name, 'phot.flux', u.Jy, np.array([1.0])))

    with pytest.raises(ValueError, match=f'Field name `{name}` is reserved for RGES constant metadata'):
        VOTable.for_rges_data_release(metadata, columns)


@pytest.mark.parametrize('provided_names', [[], ['target_name'], ['exposure']])
def test_for_rges_reports_missing_required_metadata(provided_names):
    metadata = [VOTableMetadataInfo.new(name, 'value') for name in provided_names]
    missing_names = [name for name in RGES_REQUIRED_METADATA if name not in provided_names]

    with pytest.raises(ValueError) as exc_info:
        VOTable.for_rges_data_release(metadata, [])

    assert str(exc_info.value) == (
        'Missing required RGES metadata fields: ' + ', '.join(f'`{name}`' for name in missing_names) + '.'
    )


@pytest.mark.parametrize('name', RGES_REQUIRED_METADATA)
def test_for_rges_columns_do_not_satisfy_required_metadata(name):
    metadata = [
        VOTableMetadataInfo.new(other_name, 'value')
        for other_name in RGES_REQUIRED_METADATA if other_name != name
    ]
    column = VOTableColumn.new(name, 'phot.flux', u.Jy, np.array([1.0]))

    with pytest.raises(ValueError, match=f'Missing required RGES metadata fields: `{name}`'):
        VOTable.for_rges_data_release(metadata, [column])


def test_for_rges_required_metadata_accepts_info_fields():
    metadata = [
        VOTableMetadataInfo.new(name, value) for name, value in RGES_REQUIRED_METADATA.items()
    ]

    table = VOTable.for_rges_data_release(metadata, []).get_first_table()

    assert [(info.name, info.value) for info in table.infos[-len(metadata):]] == list(RGES_REQUIRED_METADATA.items())
