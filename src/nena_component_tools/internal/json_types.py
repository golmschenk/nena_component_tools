type JsonType = dict[str, 'JsonType'] | list['JsonType'] | str | int | float | bool | None
type JsonDictionary = dict[str, JsonType]