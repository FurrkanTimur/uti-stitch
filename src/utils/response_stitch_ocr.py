from sdks.novavision.src.helper.package import PackageHelper
from ..models.StitchOcrModel import (
    StitchOutputs,
    StitchResponse,
    StitchOcrExecutor,
    OutputStitched,
)
from ..models.PackageModel import PackageModel, PackageConfigs, ConfigExecutor


def build_response_stitch_ocr(context):
    outputStitched = OutputStitched(value=context.stitched)
    _outputs = StitchOutputs(outputStitched=outputStitched)
    packageResponse = StitchResponse(outputs=_outputs)
    packageExecutor = StitchOcrExecutor(value=packageResponse)
    executor = ConfigExecutor(value=packageExecutor)
    packageConfigs = PackageConfigs(executor=executor)
    package = PackageHelper(packageModel=PackageModel, packageConfigs=packageConfigs)
    packageModel = package.build_model(context)
    return packageModel
