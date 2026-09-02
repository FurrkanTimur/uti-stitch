from pydantic import Field, validator
from typing import List, Optional, Union, Literal
from sdks.novavision.src.base.model import Package, Image, Inputs, Configs, Outputs, Response, Request, Output, Input, Config

class InputImageA(Input):
    name: Literal["inputImageA"] = "inputImageA"
    value: Image
    type: Literal["object"] = "object"
    class Config:
        title = "Image A"

class InputImageB(Input):
    name: Literal["inputImageB"] = "inputImageB"
    value: Image
    type: Literal["object"] = "object"
    class Config:
        title = "Image B"

class StitchImagesInputs(Inputs):
    inputImageA: InputImageA
    inputImageB: InputImageB

class OutputImage(Output):
    name: Literal["outputImage"] = "outputImage"
    value: Union[List[Image], Image]
    type: str = "object"

    @validator("type", pre=True, always=True)
    def set_type_based_on_value(cls, value, values):
        value = values.get('value')
        if isinstance(value, Image):
            return "object"
        elif isinstance(value, list):
            return "list"

    class Config:
        title = "Image"

class ConfigMaxAllowedReprojectionError(Config):
    """
    Maximum allowed reprojection error, in pixels, to treat a point pair as
    an inlier during RANSAC homography calculation (cv2.findHomography's
    ransacReprojThreshold). Lower values require stricter alignment; higher
    values tolerate more matching noise (useful for low-detail images).
    """
    name: Literal["configMaxAllowedReprojectionError"] = "configMaxAllowedReprojectionError"
    value: float = Field(default=3.0, ge=0.0)
    type: Literal["number"] = "number"
    field: Literal["textInput"] = "textInput"

    class Config:
        title = "Max Reprojection Error"
        json_schema_extra = {
            "shortDescription": "RANSAC inlier threshold in pixels for homography estimation."
        }

class ConfigCountOfBestMatchesPerQueryDescriptor(Config):
    """
    Number of best matches per descriptor for BFMatcher KNN.
    Usually set to 2 for Lowe's ratio test.
    """
    name: Literal["configCountOfBestMatchesPerQueryDescriptor"] = "configCountOfBestMatchesPerQueryDescriptor"
    value: int = Field(default=2, gt=0)
    type: Literal["number"] = "number"
    field: Literal["textInput"] = "textInput"

    class Config:
        title = "KNN Match Count"
        json_schema_extra = {
            "shortDescription": "Number of nearest neighbors (k) for KNN matching."
        }

class StitchImagesConfigs(Configs):
    configMaxAllowedReprojectionError: ConfigMaxAllowedReprojectionError
    configCountOfBestMatchesPerQueryDescriptor: ConfigCountOfBestMatchesPerQueryDescriptor

class StitchImagesOutputs(Outputs):
    outputImage: OutputImage

class StitchImagesRequest(Request):
    inputs: Optional[StitchImagesInputs]
    configs: StitchImagesConfigs
    class Config:
        json_schema_extra = {
            "target": "configs"
        }

class StitchImagesResponse(Response):
    outputs: StitchImagesOutputs

class StitchImagesExecutor(Config):
    name: Literal["StitchImages"] = "StitchImages"
    value: Union[StitchImagesRequest, StitchImagesResponse]
    type: Literal["object"] = "object"
    field: Literal["option"] = "option"

    class Config:
        title = "StitchImages"
        json_schema_extra = {
            "target": {
                "value": 0
            }
        }
