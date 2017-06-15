'''

Simple loading functions for datasets

   from deid.data import get_dataset

Copyright (c) 2017 Vanessa Sochat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''


from deid.utils import get_installdir
from deid.logger import bot
import os

def get_dataset(dataset=None):
    '''get_dataset will return some data provided by the application,
    based on a user-provided label. In the future, we can add https endpoints
    to retrieve online datasets.
    '''
    here = get_installdir()
    valid_datasets = {'dicom-cookies':'%s/data/dicom-cookies' %here}

    if dataset is not None:

        # In case the user gave an extension
        dataset = os.path.splitext(dataset)[0].lower()
        if dataset in valid_datasets:
            return valid_datasets[dataset]

    bot.info("Valid datasets include: %s" %(','.join(list(valid_datasets.keys()))))

