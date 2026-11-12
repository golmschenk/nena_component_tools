from collections.abc import Iterable

import numpy as np
from astropy.io.votable.converters import numpy_to_votable_dtype
from astropy.io.votable.tree import VOTableFile, Resource, TableElement, Field, Param

from nena_component_tools.internal.data.votable.column import VOTableColumnBase
from nena_component_tools.internal.data.votable.metadata_field import VOTableMetadataField
from nena_component_tools.internal.data.votable.time_column import VOTableTimeColumn


class VOTable(VOTableFile):
    @classmethod
    def new(cls, metadata_fields: list[VOTableMetadataField], columns: list[VOTableColumnBase]):
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
            table.params.append(Param(
                votable, name=metadata_field.name, ucd=metadata_field.ucd,
                unit=metadata_field.unit, value=metadata_field.value,
                **numpy_to_votable_dtype(np.result_type(metadata_field.dtype), np.shape(metadata_field.value)[::-1]),
            ))

        table.create_arrays(column_length)
        for column_index, column in enumerate(columns):
            table.array[table.fields[column_index].ID] = column.array

        return votable


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
