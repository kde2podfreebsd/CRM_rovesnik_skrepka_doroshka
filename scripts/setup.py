from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='CRM-TGBOTS-Rovesnik-Screpka-Dorozhka',
    version='0.1',
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'pip install -r requirements.txt'
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.11.6',
        'Authors: @kde2podfreebsd | @BychkovArthur | @complicat9d | @Haliava | @whend-dev'
    ],
)
