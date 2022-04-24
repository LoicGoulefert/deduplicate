from setuptools import setup

with open("README.md") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()

setup(
    name="deduplicate",
    version="0.1.0a1",
    description="Duplicate line removal plug-in for vpype",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Loïc Goulefert",
    url="https://github.com/LoicGoulefert/deduplicate",
    license=license,
    packages=["deduplicate"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Topic :: Multimedia :: Graphics",
        "Environment :: Plugins",
    ],
    setup_requires=["wheel"],
    install_requires=[
        "click",
        "numpy",
        "shapely>=1.8.0",
        "vpype>=1.9, <2.0",
        "tqdm>=4.61.1",
    ],
    entry_points="""
            [vpype.plugins]
            deduplicate=deduplicate.deduplicate:deduplicate
        """,
)
