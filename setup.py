import os
from setuptools import setup, find_packages
import htpayway


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-htpayway',
    url='https://github.com/logithr/djangocms-htpayway',
    author='Sasha Matijasic',
    author_email='sasha@selectnull.com',
    version=htpayway.__version__,
    description='HT PayWay (payment gateway) API integration with Django',
    long_description=open('README.md').read(),
    license='MIT',
    keywords='htpayway ht payway',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django>=1.3',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
