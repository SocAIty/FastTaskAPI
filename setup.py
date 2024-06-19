from setuptools import setup, find_packages

setup(
    name='socaity-router',
    version='0.0.4',
    description="A router for AI services running anywhere, locally, hosted, serverless and decentralized. Plays well with existing providers like runpod and famous libraries like fastapi.",
    author='SocAIty',
    packages=find_packages(),
    install_requires=[
        'uvicorn',
        'fastapi',
        'singleton-decorator==1.0.0',
        'runpod>=1.6.0'
    ]
)