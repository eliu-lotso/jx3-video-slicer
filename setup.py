from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="jx3-video-slicer",
    version="1.0.0",
    author="JX3 Video Slicer Team",
    description="剑网三花舞剑竞技场视频智能切片工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eliu-lotso/jx3-video-slicer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Video",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "jx3-slicer=video_slicer_ui:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["models/*.pth", "bin/*.exe"],
    },
) 