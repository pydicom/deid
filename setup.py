from setuptools import setup, find_packages
import sys
import os

##########################################################################################
# HELPER FUNCTIONS #######################################################################
##########################################################################################

def get_lookup():
    '''get version by way of singularity.version, returns a 
    lookup dictionary with several global variables without
    needing to import singularity
    '''
    lookup = dict()
    version_file = os.path.join('deid', 'version.py')
    with open(version_file) as filey:
        exec(filey.read(), lookup)
    return lookup


# Read in requirements
def get_requirements(lookup=None):
    '''get_requirements reads in requirements and versions from
    the lookup obtained with get_lookup'''

    if lookup == None:
        lookup = get_lookup()

    install_requires = []
    for module in lookup['INSTALL_REQUIRES']:
        module_name = module[0]
        module_meta = module[1]

        # Install exact version
        if "exact_version" in module_meta:
            dependency = "%s==%s" %(module_name,module_meta['exact_version'])

        # Install min version
        elif "min_version" in module_meta:
            if module_meta['min_version'] == None:
                dependency = module_name
            else:
                dependency = "%s>=%s" %(module_name,module_meta['min_version'])

        # Install min version
        elif "max_version" in module_meta:
            if module_meta['max_version'] == None:
                dependency = module_name
            else:
                dependency = "%s<=%s" %(module_name, module_meta['max_version'])

        install_requires.append(dependency)
    return install_requires


# Make sure everything is relative to setup.py
install_path = os.path.dirname(os.path.abspath(__file__)) 
os.chdir(install_path)

# Get version information from the lookup
lookup = get_lookup()
VERSION = lookup['__version__']
NAME = lookup['NAME']
AUTHOR = lookup['AUTHOR']
AUTHOR_EMAIL = lookup['AUTHOR_EMAIL']
PACKAGE_URL = lookup['PACKAGE_URL']
KEYWORDS = lookup['KEYWORDS']
DESCRIPTION = lookup['DESCRIPTION']
DEPENDENCY_LINKS = lookup['DEPENDENCY_LINKS']
LICENSE = lookup['LICENSE']
with open('README.md') as filey:
    LONG_DESCRIPTION = filey.read()

##########################################################################################
# MAIN ###################################################################################
##########################################################################################


INSTALL_REQUIRES = get_requirements(lookup)

setup(
    name=NAME,
    version=VERSION,
    license=LICENSE,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=PACKAGE_URL,
    packages=find_packages(), 
    include_package_data=True,
    long_description=LONG_DESCRIPTION,
    keywords=KEYWORDS,
    install_requires=INSTALL_REQUIRES,
    dependency_links = DEPENDENCY_LINKS,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development',
        'Topic :: Scientific/Engineering',
        'Topic :: System :: Shells',
        'Topic :: Terminals',
        'Topic :: Utilities'
    ],

    entry_points = {'console_scripts': [ 'deid=deid.main:main' ] }
)
