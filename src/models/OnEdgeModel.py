from pydantic import Field, validator
from typing import Optional, Union, Literal
from sdks.novavision.src.base.model import Package, Image, Inputs, Configs, Outputs, Response, Request, Output, Input, Config

from .StitchImagesModel import OutputImage


class InputImages(Input):
    name: Literal["inputImages"] = "inputImages"
    value: Union[list, Image]
    type: str = "list"

    @validator("type", pre=True, always=True)
    def set_type_based_on_value(cls, value, values):
        value = values.get('value')
        if isinstance(value, list):
            return "list"
        return "object"

    class Config:
        title = "Images"


class ConfigRowCount(Config):
    """
    Fixed number of rows in the collage grid.
    """
    name: Literal["configRowCount"] = "configRowCount"
    value: int = Field(default=1, ge=1, le=100)
    type: Literal["number"] = "number"
    field: Literal["textInput"] = "textInput"
    placeHolder: Literal["[1, 100]"] = "[1, 100]"

    class Config:
        title = "Row Count"
        json_schema_extra = {
            "shortDescription": "Number of rows."
        }


class ConfigRowFixed(Config):
    configRowCount: ConfigRowCount
    name: Literal["Fixed"] = "Fixed"
    value: Literal["Fixed"] = "Fixed"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "Fixed"


class ConfigRowMax(Config):
    name: Literal["Max"] = "Max"
    value: Literal["Max"] = "Max"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "Max"


class ConfigRow(Config):
    """
    Row axis of the collage grid.
    - Max: the row axis grows freely to fit all frames; the column axis
      determines capacity.
    - Fixed: the row count is pinned to the given value.

    Setting Row to Max and Column to 1 stacks every frame vertically.
    Setting both axes to Max lays the frames out in a near-square grid.
    """
    name: Literal["configRow"] = "configRow"
    value: Union[ConfigRowMax, ConfigRowFixed]
    type: Literal["object"] = "object"
    field: Literal["dependentDropdownlist"] = "dependentDropdownlist"

    class Config:
        title = "Row"
        json_schema_extra = {
            "shortDescription": "Grow rows freely (Max) or pin them (Fixed)."
        }


class ConfigColumnCount(Config):
    """
    Fixed number of columns in the collage grid.
    """
    name: Literal["configColumnCount"] = "configColumnCount"
    value: int = Field(default=1, ge=1, le=100)
    type: Literal["number"] = "number"
    field: Literal["textInput"] = "textInput"
    placeHolder: Literal["[1, 100]"] = "[1, 100]"

    class Config:
        title = "Column Count"
        json_schema_extra = {
            "shortDescription": "Number of columns."
        }


class ConfigColumnFixed(Config):
    configColumnCount: ConfigColumnCount
    name: Literal["Fixed"] = "Fixed"
    value: Literal["Fixed"] = "Fixed"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "Fixed"


class ConfigColumnMax(Config):
    name: Literal["Max"] = "Max"
    value: Literal["Max"] = "Max"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "Max"


class ConfigColumn(Config):
    """
    Column axis of the collage grid.
    - Max: the column axis grows freely to fit all frames; the row axis
      determines capacity.
    - Fixed: the column count is pinned to the given value.

    Setting Column to Max and Row to 1 places every frame side by side.
    Setting both axes to Max lays the frames out in a near-square grid.
    """
    name: Literal["configColumn"] = "configColumn"
    value: Union[ConfigColumnMax, ConfigColumnFixed]
    type: Literal["object"] = "object"
    field: Literal["dependentDropdownlist"] = "dependentDropdownlist"

    class Config:
        title = "Column"
        json_schema_extra = {
            "shortDescription": "Grow columns freely (Max) or pin them (Fixed)."
        }


class ConfigMaxFrames(Config):
    """
    Absolute cap on how many frames end up in the collage, applied before
    the grid is laid out. When more frames arrive than this cap, they are
    resampled at even intervals across the whole sequence rather than
    truncated, so the collage still spans the full event from start to end.
    """
    name: Literal["configMaxFrames"] = "configMaxFrames"
    value: int = Field(default=12, ge=1, le=400)
    type: Literal["number"] = "number"
    field: Literal["textInput"] = "textInput"
    placeHolder: Literal["[1, 400]"] = "[1, 400]"

    class Config:
        title = "Max Frames"
        json_schema_extra = {
            "shortDescription": "Frame cap; excess frames are resampled, not dropped."
        }


class ConfigCellWidth(Config):
    """
    Width in pixels each frame is resized to before being placed in the
    grid. Cell height follows from the first frame's aspect ratio, so all
    cells stay uniform. Keeps the stitched output from growing to tens of
    megapixels when many full-resolution frames are combined.
    """
    name: Literal["configCellWidth"] = "configCellWidth"
    value: int = Field(default=480, ge=32, le=4096)
    type: Literal["number"] = "number"
    field: Literal["textInput"] = "textInput"
    placeHolder: Literal["[32, 4096]"] = "[32, 4096]"

    class Config:
        title = "Cell Width (px)"
        json_schema_extra = {
            "shortDescription": "Per-frame width in the collage."
        }


class OnEdgeInputs(Inputs):
    inputImages: InputImages


class OnEdgeConfigs(Configs):
    configRow: ConfigRow
    configColumn: ConfigColumn
    configMaxFrames: ConfigMaxFrames
    configCellWidth: ConfigCellWidth


class OnEdgeOutputs(Outputs):
    outputImage: OutputImage


class OnEdgeRequest(Request):
    inputs: Optional[OnEdgeInputs]
    configs: OnEdgeConfigs

    class Config:
        json_schema_extra = {
            "target": "configs"
        }


class OnEdgeResponse(Response):
    outputs: OnEdgeOutputs


class OnEdgeExecutor(Config):
    name: Literal["OnEdge"] = "OnEdge"
    value: Union[OnEdgeRequest, OnEdgeResponse]
    type: Literal["object"] = "object"
    field: Literal["option"] = "option"

    class Config:
        title = "OnEdge"
        json_schema_extra = {
            "target": {
                "value": 0
            }
        }
