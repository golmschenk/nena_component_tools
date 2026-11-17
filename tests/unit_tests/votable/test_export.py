from io import BytesIO
from xml.etree import ElementTree

import numpy as np
import pyarrow.parquet as pq
import pytest
from astropy import units as u
from astropy.io.votable import parse
from astropy.io.votable.tree import Info, Param, TimeSys
from astropy.table import Table
from astropy.table.meta import get_header_from_yaml

from nena_component_tools.internal.data.votable.column import VOTableColumn
from nena_component_tools.internal.data.votable.metadata_info import VOTableMetadataInfo
from nena_component_tools.internal.data.votable.metadata_param import VOTableMetadataParam
from nena_component_tools.internal.data.votable.table import VOTable
from nena_component_tools.internal.data.votable.time_column import VOTableTimeColumn


@pytest.fixture
def release():
    metadata = [
        VOTableMetadataInfo.new('ccsp.data_release_id', 'DR0'),
        VOTableMetadataInfo.new('file_version', 'v0.1'),
        VOTableMetadataInfo.new('target_name', 'α Centauri'),
        VOTableMetadataInfo.new('target_keywords', 'Stars,Variable stars'),
        VOTableMetadataParam.new('simulated_flag', True, 'meta.code', u.one),
        VOTableMetadataInfo.new('source_observations_id', '123,456'),
        VOTableMetadataParam.new('target_keywords_id', np.array([1674, 1636]), 'meta.id', u.one),
        VOTableMetadataParam.new('exposure_time', 30.0, 'time.duration', u.s),
        VOTableMetadataParam.new('target_coordinates.ra', 10.0, 'pos.eq.ra', u.deg),
        VOTableMetadataParam.new('target_coordinates.dec', -30.0, 'pos.eq.dec', u.deg),
    ]
    columns = [
        VOTableTimeColumn.new(
            'time', 'time.epoch', u.day,
            TimeSys(ID='time', timeorigin='MJD-origin', timescale='UTC', refposition='TOPOCENTER',
                    config={'version_1_4_or_later': True}),
            np.array([60000.0, 60001.0]),
        ),
        VOTableColumn.new('flux', 'phot.flux', u.Jy, np.ma.array([1.25, 2.5], mask=[False, True]),
                          dtype=np.float32),
        VOTableColumn.new('target name', 'meta.id', u.one, np.array(['α', 'β'])),
        VOTableColumn.new('position', 'pos.eq.ra', u.deg, np.array([10.0, 11.0])),
    ]
    votable = VOTable.for_rges_data_release(metadata, columns)
    votable.infos.append(Info(name='origin', value='root'))
    resource = votable.resources[0]
    resource.params.append(Param(votable, name='start_time', value=60000.0, unit=u.day,
                                 ref=columns[0].time_system.ID, datatype='double'))
    table = votable.get_first_table()
    table.fields[1].description = 'Flux density'
    return votable


def test_astropy_export_preserves_columns_and_typed_metadata(release):
    result = release.to_astropy_table()

    assert isinstance(result, Table)
    assert result.colnames == ['time', 'flux', 'target_name', 'position']
    np.testing.assert_array_equal(result['time'], [60000.0, 60001.0])
    np.testing.assert_array_equal(result['flux'].mask, [False, True])
    assert result['flux'][0] == 1.25
    assert result['flux'].dtype == np.float32
    assert result['flux'].unit == u.Jy
    assert result['flux'].description == 'Flux density'
    assert result['flux'].meta['ucd'] == 'phot.flux'
    assert result['time'].meta['ref'] == 'ref.votable.timesys'
    assert result['position'].meta['ref'] == 'ref.votable.coosys'
    np.testing.assert_array_equal(result['target_name'], ['α', 'β'])
    assert result.meta['origin'] == 'root'
    assert result.meta['ccsp.name'] == 'RGES'
    assert result.meta['target_name'] == 'α Centauri'
    assert result.meta['exposure_time'] == 30.0
    assert result.meta['simulated_flag']
    np.testing.assert_array_equal(result.meta['target_keywords_id'], [1674, 1636])

    result['flux'][0] = 99
    result['flux'].mask[1] = False
    result.meta['target_keywords_id'][0] = 0
    original = release.get_first_table()
    assert original.array['flux'][0] == 1.25
    assert original.array['flux'].mask[1]
    np.testing.assert_array_equal(original.params[1].value, [1674, 1636])


def test_parquet_export_includes_both_metadata_formats_and_leaves_source_unchanged(release, tmp_path):
    output = tmp_path / 'release.parquet'
    before = BytesIO()
    release.to_xml(before)

    release.to_parquet(output)

    parquet = pq.ParquetFile(output)
    arrow = parquet.read()
    assert arrow.column_names == ['time', 'flux', 'target_name', 'position']
    assert arrow['flux'].to_pylist() == [1.25, None]
    assert arrow['time'].to_pylist() == [60000.0, 60001.0]
    assert arrow['target_name'].to_pylist() == ['α', 'β']
    assert parquet.metadata.row_group(0).column(0).compression == 'UNCOMPRESSED'
    footer = parquet.metadata.metadata
    assert footer[b'IVOA.VOTable-Parquet.version'] == b'1.0'
    assert footer[b'ccsp.name'] == b'RGES'
    assert footer[b'file_date'].decode() == release.to_astropy_table().meta['file_date']
    assert footer[b'origin'] == b'root'
    assert footer[b'target_name'].decode() == 'α Centauri'
    assert footer[b'exposure_time'] == b'30.0'
    assert footer[b'target_coordinates.ra'] == b'10.0'
    assert footer[b'target_coordinates.dec'] == b'-30.0'
    assert footer[b'start_time'] == b'60000.0'
    assert footer[b'simulated_flag'] == b'TRUE'
    assert footer[b'target_keywords_id'] == b'1674,1636'
    assert footer[b'source_observations_id'] == b'123,456'

    yaml = get_header_from_yaml(footer[b'table_meta_yaml'].decode().splitlines())
    assert [column['name'] for column in yaml['datatype']] == arrow.column_names
    flux = yaml['datatype'][1]
    assert flux['description'] == 'Flux density'
    assert flux['unit'] == 'Jy'
    assert flux['datatype'] == 'float32'
    assert flux['meta']['ucd'] == 'phot.flux'
    assert yaml['datatype'][0]['meta']['ref'] == 'ref.votable.timesys'
    assert yaml['datatype'][3]['meta']['ref'] == 'ref.votable.coosys'
    assert yaml['meta']['target_name'] == 'α Centauri'
    assert yaml['meta']['target_coordinates.ra'] == 10.0
    assert yaml['meta']['target_coordinates.dec'] == -30.0
    assert yaml['meta']['simulated_flag']

    xml = footer[b'IVOA.VOTable-Parquet.content']
    assert ElementTree.fromstring(xml).find('.//{*}DATA') is None
    embedded = parse(BytesIO(xml), verify='exception')
    table = embedded.get_first_table()
    assert len(table.array) == 0
    assert [field.ID for field in table.fields] == arrow.column_names
    assert table.fields[0].ref == embedded.resources[0].time_systems[0].ID
    assert table.fields[1].description == 'Flux density'
    assert table.fields[1].unit == u.Jy
    assert table.fields[1].datatype == 'float'
    assert table.fields[1].ucd == 'phot.flux'
    assert embedded.resources[0].time_systems[0].timeorigin == 'MJD-origin'
    assert embedded.resources[0].time_systems[0].timescale == 'UTC'
    assert table.fields[3].ref == embedded.resources[0].coordinate_systems[0].ID
    assert len(embedded.resources[0].coordinate_systems) == 1
    assert embedded.resources[0].coordinate_systems[0].system == 'ICRS'
    params = {param.name: param for param in table.params}
    assert params['target_coordinates.ra'].ref == table.fields[3].ref
    assert params['target_coordinates.dec'].ref == table.fields[3].ref
    assert params['exposure_time'].ref is None
    assert table.fields[1].ref is None
    assert params['exposure_time'].unit == u.s
    np.testing.assert_array_equal(params['target_keywords_id'].value, [1674, 1636])
    assert dict((info.name, info.value) for info in table.infos)['ccsp.name'] == 'RGES'

    after = BytesIO()
    release.to_xml(after)
    assert before.getvalue() == after.getvalue()


def test_parquet_overwrites_existing_file(release, tmp_path):
    output = tmp_path / 'release.parquet'
    output.write_bytes(b'original')
    release.to_parquet(output)
    assert pq.read_metadata(output).num_rows == 2


@pytest.mark.parametrize('rows', [0, 2])
def test_exports_preserve_array_columns_and_empty_tables(rows, tmp_path):
    values = np.arange(rows * 6, dtype=np.float64).reshape(rows, 2, 3)
    votable = VOTable.new([], [VOTableColumn.new('flux', 'phot.flux', u.Jy, values)])
    np.testing.assert_array_equal(votable.to_astropy_table()['flux'], values)

    output = tmp_path / 'array.parquet'
    votable.to_parquet(output)

    arrow = pq.read_table(output)
    assert arrow.num_rows == rows
    assert arrow['flux'].to_pylist() == values.reshape(rows, 6).tolist()
    assert b'table_meta_yaml' in arrow.schema.metadata


def test_exports_support_metadata_without_columns(tmp_path):
    votable = VOTable.new([VOTableMetadataInfo.new('origin', 'RGES')], [])
    assert votable.to_astropy_table().meta['origin'] == 'RGES'
    output = tmp_path / 'empty.parquet'
    votable.to_parquet(output)
    footer = pq.read_metadata(output).metadata
    assert footer[b'origin'] == b'RGES'
    yaml = get_header_from_yaml(footer[b'table_meta_yaml'].decode().splitlines())
    assert yaml['datatype'] == []
    assert yaml['meta']['origin'] == 'RGES'
    assert footer[b'IVOA.VOTable-Parquet.version'] == b'1.0'
    xml = footer[b'IVOA.VOTable-Parquet.content']
    assert ElementTree.fromstring(xml).find('.//{*}DATA') is None
    embedded = parse(BytesIO(xml), verify='exception')
    assert embedded.get_first_table().infos[0].value == 'RGES'


def test_parquet_embedded_votable_has_no_data_in_additional_resources(release, tmp_path):
    extra = VOTable.new([], [VOTableColumn.new('extra', 'meta.id', u.one, np.array([42]))])
    release.resources[0].resources.append(extra.resources[0])
    output = tmp_path / 'multiple_tables.parquet'
    before = BytesIO()
    release.to_xml(before)

    release.to_parquet(output)

    footer = pq.read_metadata(output).metadata
    xml = footer[b'IVOA.VOTable-Parquet.content']
    assert ElementTree.fromstring(xml).find('.//{*}DATA') is None
    embedded = parse(BytesIO(xml), verify='exception')
    assert all(len(table.array) == 0 for table in embedded.iter_tables())
    assert pq.read_metadata(output).num_rows == 2
    after = BytesIO()
    release.to_xml(after)
    assert before.getvalue() == after.getvalue()


def test_parquet_preserves_masks_inside_array_cells(tmp_path):
    values = np.ma.array([[1, 2], [3, 4]], mask=[[False, True], [True, False]], dtype=np.int16)
    votable = VOTable.new([], [VOTableColumn.new('counts', 'phot.count', u.one, values)])
    output = tmp_path / 'masked_arrays.parquet'

    votable.to_parquet(output)

    assert pq.read_table(output)['counts'].to_pylist() == [[1, None], [None, 4]]
    np.testing.assert_array_equal(votable.get_first_table().array['counts'].mask, values.mask)


def test_table_metadata_overrides_resource_and_file_values(release):
    release.resources[0].infos.append(Info(name='origin', value='resource'))
    release.get_first_table().infos.append(Info(name='origin', value='table'))
    assert release.to_astropy_table().meta['origin'] == 'table'
