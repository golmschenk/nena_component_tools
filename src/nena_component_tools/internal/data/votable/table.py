from astropy.io.votable.tree import VOTableFile, Resource, TableElement, Field

from nena_component_tools.internal.data.votable.column import VOTableColumn
from nena_component_tools.internal.data.votable.metadata_field import VOTableMetadataField


class VOTable(VOTableFile):
    @classmethod
    def new(cls, metadata_fields: list[VOTableMetadataField], columns: list[VOTableColumn]):
        votable = VOTableFile()
        resource = Resource()
        votable.resources.append(resource)
        table = TableElement(votable)
        resource.tables.append(table)

