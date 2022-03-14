from setuptools import setup

with open("README.md") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()

setup(
    name="deduplicate",
    version="0.1.0",
    description="",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Loïc Goulefert",
    url="",
    license=license,
    packages=["deduplicate"],
    install_requires=[
        "click",
        "vpype>=1.9, <2.0",
        "tqdm==4.61.1",
    ],
    entry_points="""
            [vpype.plugins]
            deduplicate=deduplicate.deduplicate:deduplicate
        """,
)
