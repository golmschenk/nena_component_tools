from collections.abc import Iterable

from astropy.io.votable.tree import VOTableFile, Resource, TableElement, Field

from nena_component_tools.internal.data.votable.column import VOTableColumn
from nena_component_tools.internal.data.votable.metadata_field import VOTableMetadataField
from nena_component_tools.internal.data.votable.time_column import VOTableTimeColumn


class VOTable(VOTableFile):
    @classmethod
    def new(cls, metadata_fields: list[VOTableMetadataField], columns: list[VOTableColumn]):
        votable = VOTableFile()
        resource = Resource()
        votable.resources.append(resource)
        table = TableElement(votable)
        resource.tables.append(table)

        column_length = columns[0].array.size
        for column_index, column in enumerate(columns[1:]):
            if column.array.size != column_length:
                raise ValueError(f'Column `{column.name}` length does not match `{columns[0].name}`.')

        time_columns = [column for column in columns if isinstance(column, VOTableTimeColumn)]
        cls.combine_duplicate_time_systems(time_columns)


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
