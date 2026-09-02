# components/Stitch/src/utils/response_stitch_images.py

from sdks.novavision.src.helper.package import PackageHelper
from ..models.StitchImagesModel import StitchImagesOutputs, StitchImagesResponse, StitchImagesExecutor, OutputImage
from ..models.PackageModel import PackageModel, PackageConfigs, ConfigExecutor


def build_response_stitch_images(context):
    outputImage = OutputImage(value=context.outputImage)
    stitchImagesOutputs = StitchImagesOutputs(outputImage=outputImage)
    stitchImagesResponse = StitchImagesResponse(outputs=stitchImagesOutputs)
    stitchImagesExecutor = StitchImagesExecutor(value=stitchImagesResponse)
    executor = ConfigExecutor(value=stitchImagesExecutor)
    packageConfigs = PackageConfigs(executor=executor)
    package = PackageHelper(packageModel=PackageModel, packageConfigs=packageConfigs)
    packageModel = package.build_model(context)
    return packageModel
