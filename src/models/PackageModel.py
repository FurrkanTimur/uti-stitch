from typing import Union, Literal
from sdks.novavision.src.base.model import Package, Configs, Config

from .StitchImagesModel import StitchImagesExecutor
from .StitchOcrModel import StitchOcrExecutor
from .OnEdgeModel import OnEdgeExecutor


class ConfigExecutor(Config):
    name: Literal["ConfigExecutor"] = "ConfigExecutor"
    value: Union[StitchImagesExecutor, StitchOcrExecutor, OnEdgeExecutor]
    type: Literal["executor"] = "executor"
    field: Literal["dependentDropdownlist"] = "dependentDropdownlist"

    class Config:
        title = "Task"


class PackageConfigs(Configs):
    executor: ConfigExecutor


class PackageModel(Package):
    configs: PackageConfigs
    type: Literal["component"] = "component"
    name: Literal["Stitch"] = "Stitch"
