import setuptools

setuptools.setup(
    name="stitch",
    version="0.0.1",
    author="DigiNova",
    author_email='info@diginova.com.tr',
    description="Stitch",
    url='https://github.com/novavision-ai/stitch',
    license='MIT',
    install_requires=['sdk', 'opencv-python-headless', 'numpy'],

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

    packages=[
        'novavision.stitch',
        'novavision.stitch.executors',
        'novavision.stitch.models',
        'novavision.stitch.utils'
    ],
    package_dir={'novavision.stitch': 'src'},
    python_requires=">=3.6"
)
