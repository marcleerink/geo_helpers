from setuptools import find_packages, setup

setup(
    name="geo-helper",
    version="0.1",
    author="Marc Leerink",
    author_email="marc.leerink@planet.com",
    description="helper modules for working with geospatial data",
    python_requires=">=3.9",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=["shapely", "jsonschema", "rasterio", "pyproj"],
    extras_require={"dev": ["pytest", "black", "ruff"]},
)
