from collections.abc import Iterable

import numpy as np
from astropy.io.votable.converters import numpy_to_votable_dtype
from astropy.io.votable.tree import VOTableFile, Resource, TableElement, Field, Info, Param
from astropy.time import Time

from nena_component_tools.internal.data.votable.column import VOTableColumnBase
from nena_component_tools.internal.data.votable.metadata_field import VOTableMetadataField
from nena_component_tools.internal.data.votable.metadata_info import VOTableMetadataInfo
from nena_component_tools.internal.data.votable.metadata_param import VOTableMetadataParam
from nena_component_tools.internal.data.votable.time_column import VOTableTimeColumn


class VOTable(VOTableFile):
    @classmethod
    def new(cls, metadata_fields: list[VOTableMetadataField], columns: list[VOTableColumnBase]):
        field_names = set()
        for field in [*metadata_fields, *columns]:
            if field.name in field_names:
                raise ValueError(f'Duplicate field name: `{field.name}`.')
            field_names.add(field.name)

        votable = cls()
        resource = Resource()
        votable.resources.append(resource)
        table = TableElement(votable)
        resource.tables.append(table)

        column_length = len(columns[0].array) if columns else 0
        for column in columns[1:]:
            if len(column.array) != column_length:
                raise ValueError(f'Column `{column.name}` length does not match `{columns[0].name}`.')

        time_columns = [column for column in columns if isinstance(column, VOTableTimeColumn)]
        cls.combine_duplicate_time_systems(time_columns)

        for column in columns:
            ref = None
            if isinstance(column, VOTableTimeColumn):
                if column.time_system not in resource.time_systems:
                    resource.time_systems.append(column.time_system)
                ref = column.time_system.ID
            table.fields.append(Field(
                votable, name=column.name, ucd=column.ucd, unit=column.unit, ref=ref,
                **numpy_to_votable_dtype(np.result_type(column.dtype), column.array.shape[1:][::-1]),
            ))

        for metadata_field in metadata_fields:
            if isinstance(metadata_field, VOTableMetadataInfo):
                table.infos.append(Info(name=metadata_field.name, value=metadata_field.value))
            elif isinstance(metadata_field, VOTableMetadataParam):
                table.params.append(Param(
                    votable, name=metadata_field.name, ucd=metadata_field.ucd,
                    unit=metadata_field.unit, value=metadata_field.value,
                    **numpy_to_votable_dtype(np.result_type(metadata_field.dtype), np.shape(metadata_field.value)[::-1]),
                ))
            else:
                raise TypeError(f'Unsupported metadata field type: {type(metadata_field).__name__}')

        table.create_arrays(column_length)
        for column_index, column in enumerate(columns):
            table.array[table.fields[column_index].ID] = column.array

        return votable


    @classmethod
    def for_rges_data_release(cls, metadata_fields: list[VOTableMetadataField], columns: list[VOTableColumnBase]):
        constant_metadata_fields = [
            VOTableMetadataInfo.new(name='ccsp.name', value='RGES'),
            VOTableMetadataInfo.new(name='ccsp.archive_lead', value='Greg Olmschenk'),
            VOTableMetadataInfo.new(name='ccsp.investigator', value='Scott Gaudi'),
            VOTableMetadataInfo.new(name='ccsp.doi', value='11.11111/xxxx-xxxx'),  # TODO: Requires real value.
            VOTableMetadataInfo.new(name='license', value='CC BY 4.0'),
            VOTableMetadataInfo.new(name='license_url', value='https://creativecommons.org/licenses/by/4.0/'),
            VOTableMetadataInfo.new(name='telescope', value='ROMAN'),
            VOTableMetadataInfo.new(name='instrument.name', value='WFI'),
            VOTableMetadataInfo.new(name='instrument.optical_element', value='F146,F087,F213'),
            VOTableMetadataInfo.new(name='wavelength.band', value='OPTICAL'),
            VOTableMetadataInfo.new(name='ccsp.intent', value='SCIENCE'),
            VOTableMetadataInfo.new(name='wavelength.minimum', value='869'),
            VOTableMetadataInfo.new(name='wavelength.maximum', value='2125'),
            VOTableMetadataInfo.new(name='file_date', value=str(Time(Time.now(), format='isot').value))
        ]
        constant_names = {field.name for field in constant_metadata_fields}
        for field in [*metadata_fields, *columns]:
            if field.name in constant_names:
                raise ValueError(f'Field name `{field.name}` is reserved for RGES constant metadata.')

        required_metadata_field_names = [
            'ccsp.data_release_id',
            'file_version',
            'target_name',  # TODO: It this always appropriate?
            'target_keywords',
            'simulated_flag',
            'source_observations_id',

        ]
        provided_metadata_names = {
            field.name for field in metadata_fields if isinstance(field, VOTableMetadataField)
        }
        missing_names = [name for name in required_metadata_field_names if name not in provided_metadata_names]
        if missing_names:
            names = ', '.join(f'`{name}`' for name in missing_names)
            raise ValueError(f'Missing required RGES metadata fields: {names}.')

        return cls.new(metadata_fields=[*constant_metadata_fields, *metadata_fields], columns=columns)


    @staticmethod
    def combine_duplicate_time_systems(time_columns: Iterable[VOTableTimeColumn]) -> None:
        unique_time_systems = {}
        for column in time_columns:
            time_system = column.time_system
            time_origin = time_system.timeorigin
            if time_origin == 'JD-origin':
                time_origin = 0.0
            elif time_origin == 'MJD-origin':
                time_origin = 2400000.5
            key = (time_origin, time_system.timescale, time_system.refposition)
            column.time_system = unique_time_systems.setdefault(key, time_system)

        for index, time_system in enumerate(unique_time_systems.values()):
            suffix = str(index) if len(unique_time_systems) > 1 else ''
            time_system.ID = f'ref.votable.timesys{suffix}'
