from setuptools import setup

setup(name='epquery',
      version='0.0.1',
      description='EnergyPlus IDF editing tool',
      url='https://github.com/sdu-cfei/epquery',
      keywords='energyplus idf editor',
      author='Krzysztof Arendt',
      author_email='krzysztof.arendt@gmail.com',
      license='BSD',
      platforms=['Windows', 'Linux'],
      packages=[
          'epquery',
          'epquery.edit'
      ],
      include_package_data=True,
      install_requires=[
          'numpy',
          'fuzzywuzzy[speedup]',
          'requests'
      ],
      classifiers = [
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Topic :: Scientific/Engineering',
          'License :: OSI Approved :: BSD License'
      ]
      )
