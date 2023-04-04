from setuptools import find_packages, setup

setup(
    name="geo_helper",
    version="0.1",
    author="Marc Leerink",
    author_email="marc.leerink@planet.com",
    description="helper modules for working with geospatial data",
    python_requires=">=3.11",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=["shapely"],
    extras_require={"dev": ["pytest"]},
)
