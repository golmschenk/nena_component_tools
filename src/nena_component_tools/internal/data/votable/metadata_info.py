from nena_component_tools.internal.data.votable.metadata_field import VOTableMetadataField


class VOTableMetadataInfo(VOTableMetadataField):
    def __init__(self, name: str, value: str):
        super().__init__(name=name, value=value)

    @classmethod
    def new(cls, name: str, value: str):
        return cls(name=name, value=value)
