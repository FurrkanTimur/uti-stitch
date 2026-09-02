from sdks.novavision.src.helper.package import PackageHelper
from ..models.OnEdgeModel import OnEdgeOutputs, OnEdgeResponse, OnEdgeExecutor
from ..models.StitchImagesModel import OutputImage
from ..models.PackageModel import PackageModel, PackageConfigs, ConfigExecutor


def build_response_on_edge(context):
    outputImage = OutputImage(value=context.outputImage)
    onEdgeOutputs = OnEdgeOutputs(outputImage=outputImage)
    onEdgeResponse = OnEdgeResponse(outputs=onEdgeOutputs)
    onEdgeExecutor = OnEdgeExecutor(value=onEdgeResponse)
    executor = ConfigExecutor(value=onEdgeExecutor)
    packageConfigs = PackageConfigs(executor=executor)
    package = PackageHelper(packageModel=PackageModel, packageConfigs=packageConfigs)
    packageModel = package.build_model(context)
    return packageModel
