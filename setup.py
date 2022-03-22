from setuptools import setup, find_packages

setup(
    name="bomberMan",
    version="0.0.1",
    author="Iwo Naglik",
    description="Custom environment for reinforcement learning experiments.",
    long_description="A custom environment that implements simplified version of BomberMan game for reinforcement learning experiments.",
    long_description_content_type="text/markdown",
    url="https://github.com/NaIwo/BomberManAI",
    packages=find_packages(),
    install_requires=['pettingzoo', 'gym', 'pygame'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
