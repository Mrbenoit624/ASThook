#!/usr/bin/env python
 
from setuptools import setup, find_packages
from setuptools.command.install import install
import subprocess

import asthook
from asthook.conf import VERSION_FRIDA
import bootstrap
import os, stat
 
class pre_install(install):
    def run(self):
        bootstrap.main()
        install.run(self)
        for filepath in self.get_outputs():
            if "api_key_detector/gibberish_detector/gibberish_detector.pki" in filepath:
                os.chmod(filepath, stat.S_IWOTH | stat.S_IROTH | stat.S_IRGRP | stat.S_IWGRP |stat.S_IREAD |stat.S_IWRITE)

with open('requirements.txt') as f:
    requirements = f.read().splitlines()
    requirements = [x if not x.startswith("frida") else f"frida=={VERSION_FRIDA}" for x in requirements]


setup(
    name='asthook',
    version='1.1.0',
    packages=find_packages() + \
            ['api_key_detector/my_tools',
             'api_key_detector/gibberish_detector'],
    include_package_data = True,
    author="MadSquirrel",
    author_email="benoit.forgette@ci-yow.com",
    description="Analyse apk source code and make a dynamic analysis",
    long_description_content_type="text/markdown",
    long_description=open('README.md').read(),
    download_url="https://gitlab.com/MadSquirrels/mobile/asthook",
    url='https://madsquirrels.gitlab.io/mobile/asthook/',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 1 - Planning"
    ],
 
    entry_points = {
        'console_scripts': [
            'asthook=asthook:main',
        ],
    },
    scripts=['asthook-manager'],
    cmdclass={
        'install': pre_install
    },
    install_requires = requirements,
    python_requires='>=3.5'
 
)
