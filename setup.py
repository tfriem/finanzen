from setuptools import setup

setup(name='finanzen',
      version='0.1',
      author='Tobias Friemel',
      author_email='tfriem@gmail.com',
      packages=['finanzen'],
      install_requires=[],
      entry_points={
          'console_scripts': ['finanzen=finanzen.command_line:main']
      })
