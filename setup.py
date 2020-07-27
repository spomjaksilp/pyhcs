from setuptools import setup, find_packages

source_path = 'src'
packages = find_packages(source_path)

distribution = setup(name='hcs',
                     version='0.1',
                     packages=packages,
                     package_dir={'': source_path},
                     )
