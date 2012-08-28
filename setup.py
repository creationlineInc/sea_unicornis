# -*- coding: utf-8 -*-
import os
from setuptools import setup

install_requires = [
    'Kotti >= 0.7',
    'Babel',
    'kotti_mapreduce >= 0.2.0',
]

setup(name='sea_unicornis',
      version='0.1.0',
      description='The Simple Hive Application',
      long_description='',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python',
          'Framework :: Pylons',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
          'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
          'License :: Repoze Public License',
      ],
      author='Creationline, Inc',
      author_email='info at creationline.com',
      url='https://github.com/creationlineInc/sea_unicornis',
      keywords='mapreduce emr hive kotti',
      license='Commercial License',
      packages=['sea_unicornis'],
      package_data={'sea_unicornis': [
          'static/*',
          'templates/*.pt',
          'locale/*.*',
          'locale/*/LC_MESSAGES/*.*']},
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      test_requires=['pytest', 'pytest-pep8'],
      dependency_links=[
      ],
      #[fanstatic.libraries]
      #sea_unicornis = sea_unicornis.static:lib_kotti
      entry_points="""
      """,
      message_extractors={'sea_unicornis': [
          ('**.py', 'lingua_python', None),
          ('templates/**.pt', 'lingua_xml', None),
      ]},
      )
