from pydantic import Field, validator
from typing import List, Optional, Union, Literal
from sdks.novavision.src.base.model import (
    Package,
    Inputs,
    Configs,
    Outputs,
    Response,
    Request,
    Output,
    Input,
    Config,
    Detection,
)


class OCRDetection(Detection):
    data: str


class InputDetections(Input):
    name: Literal["inputDetections"] = "inputDetections"
    value: List[Detection]
    type: str = "object"

    class Config:
        title = "OCR Detections"


class OutputStitched(Output):
    name: Literal["outputStitched"] = "outputStitched"
    value: List[OCRDetection]
    type: str = "object"

    class Config:
        title = "Stitched"


class ReadingDirectionLeftToRight(Config):
    name: Literal["ReadingDirectionLeftToRight"] = "ReadingDirectionLeftToRight"
    value: Literal["left_to_right"] = "left_to_right"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "Left to Right"


class ReadingDirectionRightToLeft(Config):
    name: Literal["ReadingDirectionRightToLeft"] = "ReadingDirectionRightToLeft"
    value: Literal["right_to_left"] = "right_to_left"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "Right to Left"


class ReadingDirectionVerticalTopToBottom(Config):
    name: Literal["ReadingDirectionVerticalTopToBottom"] = (
        "ReadingDirectionVerticalTopToBottom"
    )
    value: Literal["vertical_top_to_bottom"] = "vertical_top_to_bottom"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "Vertical Top to Bottom"


class ReadingDirectionVerticalBottomToTop(Config):
    name: Literal["ReadingDirectionVerticalBottomToTop"] = (
        "ReadingDirectionVerticalBottomToTop"
    )
    value: Literal["vertical_bottom_to_top"] = "vertical_bottom_to_top"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "Vertical Bottom to Top"


class ReadingDirectionAuto(Config):
    name: Literal["ReadingDirectionAuto"] = "ReadingDirectionAuto"
    value: Literal["auto"] = "auto"
    type: Literal["string"] = "string"
    field: Literal["option"] = "option"

    class Config:
        title = "Auto"


class ReadingDirection(Config):
    """
    Specifies the logical flow of the text language.
    This determines the order in which detected words are concatenated (e.g., Left-to-Right for English, Right-to-Left for Arabic).
    """
    name: Literal["ReadingDirection"] = "ReadingDirection"
    value: Union[
        ReadingDirectionLeftToRight,
        ReadingDirectionRightToLeft,
        ReadingDirectionVerticalTopToBottom,
        ReadingDirectionVerticalBottomToTop,
        ReadingDirectionAuto,
    ]
    type: Literal["object"] = "object"
    field: Literal["dropdownlist"] = "dropdownlist"

    class Config:
        title = "Reading Direction"
        json_schema_extra = {
            "shortDescription": "Text Flow Order"
        }


class Tolerance(Config):
    """
    Extra vertical gap (in pixels) allowed beyond a word's own bounding box before it
    is considered part of the next line. Words on the same visual line already overlap
    vertically, so 0 works for most documents.
    - Higher values: More forgiving of skewed/misaligned text, but each extra pixel
      risks chaining separate lines together into one (words on adjacent lines start
      getting merged), which quickly garbles reading order.
    - Recommended range: 0-3. Increase gradually and re-check the output before going
      higher.
    """
    name: Literal["Tolerance"] = "Tolerance"
    value: int = Field(ge=0, le=100, default=1)
    type: Literal["number"] = "number"
    field: Literal["textInput"] = "textInput"

    class Config:
        title = "Tolerance"
        json_schema_extra = {
            "shortDescription": "Line Alignment Sensitivity"
        }


class ClusterDistance(Config):
    """
    The maximum horizontal gap (in pixels) allowed between words to merge them into a single sentence or block.
    - Higher values: Merges words that are far apart (e.g., across columns).
    - Lower values: Keeps words separate if there is a gap.
    """
    name: Literal["ClusterDistance"] = "ClusterDistance"
    value: int = Field(ge=0, default=100)
    type: Literal["number"] = "number"
    field: Literal["textInput"] = "textInput"

    class Config:
        title = "Cluster Distance"
        json_schema_extra = {
            "shortDescription": "Word Merge Gap (px)"
        }


class StitchInputs(Inputs):
    inputDetections: InputDetections


class StitchOutputs(Outputs):
    outputStitched: OutputStitched


class StitchConfigs(Configs):
    readingDirection: ReadingDirection
    tolerance: Tolerance
    clusterDistance: ClusterDistance


class StitchRequest(Request):
    inputs: Optional[StitchInputs]
    configs: StitchConfigs

    class Config:
        json_schema_extra = {"target": "configs"}


class StitchResponse(Response):
    outputs: StitchOutputs


class StitchOcrExecutor(Config):
    name: Literal["StitchOcr"] = "StitchOcr"
    value: Union[StitchRequest, StitchResponse]
    type: Literal["object"] = "object"
    field: Literal["option"] = "option"

    class Config:
        title = "Stitch OCR"
        json_schema_extra = {"target": {"value": 0}}
