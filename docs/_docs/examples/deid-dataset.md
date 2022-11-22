---
title: Deidentify a Pydicom Dataset
category: Examples
order: 6
---

In this example we will create a custom class to deidentify a single instance of a `pydicom.Dataset` with a custom recipe.

<a id="Overview">
### Overview
We will use four files for this example:
```
my_deid_example
├── my_deid_recipe.dicom
├── my_dicom_file.json
├── my_module.py
└── requirements.txt
```

The `requirements.txt` file is used only to be able to run this example.
```
deid
pydicom
pycryptodome
```

We can install them by running the following commands (requires `conda`)
```bash
conda create -n deid_example python=3.9
conda activate deid_example
cd my_deid_example
pip install -r requirements.txt
```


The contents of `my_dicom_file.json` are used to load a pydicom.Dataset instance.
```json
{
    "SpecificCharacterSet":{"vr":"CS","Value":["ISO_IR 100"]},
    "ImageType":{"vr":"CS","Value":["DERIVED","PRIMARY"]},
    "SOPClassUID":{"vr":"UI","Value":["1.2.840.10008.5.1.4.1.1.1.2"]},
    "StudyDate":{"vr":"DA","Value":["20220627"]},
    "SeriesDate":{"vr":"DA","Value":["20220627"]},
    "AcquisitionDate":{"vr":"DA","Value":["20220627"]},
    "ContentDate":{"vr":"DA","Value":["20220627"]},
    "StudyTime":{"vr":"TM","Value":["080803"]},
    "ContentTime":{"vr":"TM","Value":["080808.202000"]},
    "PatientName":{"vr":"PN","Value":[{"Alphabetic":"Maria^Doe"}]},
    "PatientID":{"vr":"LO","Value":["1234567890"]},
    "PatientBirthDate":{"vr":"DA","Value":["19900606"]},
    "Modality":{"vr":"CS","Value":["MG"]},
    "PatientSex":{"vr":"CS","Value":["F"]},
    "PatientAge":{"vr":"AS","Value":["032Y"]},
    "StudyID":{"vr":"SH","Value":["mammogram87654"]}
}
```

<a id="The recipe">
### The recipe

We create a custom recipe `my_deid_recipe.dicom` that specifies what we want to do.
```
FORMAT dicom

%header

ADD PatientIdentityRemoved YES
ADD DeidentificationMethod my_deid_recipe.dicom.v1.0

# Specify what we want to keep

KEEP ContentDate
KEEP StudyDate

# Replacements with custom functions. Those are registered in my_module.py

REPLACE PatientName func:replace_name
REPLACE AccessionNumber func:hash_func
REPLACE AdmissionID func:hash_func
REPLACE InterpretationID func:hash_func
REPLACE PatientBirthDate func:remove_day
REPLACE PatientID func:hash_func
REPLACE PerformedProcedureStepID func:hash_func
REPLACE PerformingPhysicianName func:hash_func
REPLACE RequestedProcedureID func:hash_func
REPLACE ResultsID func:hash_func
REPLACE StudyID func:hash_func


# Tags that require custom regex expressions
# Curve Data"(50xx,xxxx)"
REMOVE contains:^50.{6}$
# Overlay comments and data (60xx[34]000)
REMOVE contains:^60.{2}[34]000$
# Private tags ggggeeee where gggg is odd
REMOVE contains:^.{3}[13579].{4}$

# Blank the other tags

BLANK PatientWeight
BLANK PatientSize
REMOVE PatientAge
REMOVE SeriesDate
REMOVE AcquisitionDate
REMOVE StudyTime
REMOVE ContentTime
REMOVE PatientAge
REMOVE PatientSex

# ... etc
```

<a id="The custom class">
### The custom deidentifier class

```python
from deid.config import DeidRecipe
from deid.dicom.parser import DicomParser
import pydicom
from Crypto.Hash import SHA512
from datetime import datetime

class DeidDataset:
    """This class allows to pseudonymize an instance of
    pydicom.Dataset with our custom recipe and functions.
    """
    def __init__(self, secret_salt: str, recipe_path: str):
        """New instance of our pseudonymizer class.

        :param secret_salt: a random string that makes the
         hashing harder to break.
        :param recipe_path: path to our deid recipe.
        """
        self.secret_salt = secret_salt
        self.recipe = DeidRecipe(recipe_path)

    def pseudonymize(self, dataset:pydicom.Dataset) -> pydicom.Dataset:
        """Pseudonymize a single dicom dataset

        :param dataset: dataset that will be pseudonymized
        :returns: pseudonymized dataset
        """
        parser = DicomParser(dataset, self.recipe)
        # register functions that are specified in the recipe
        parser.define('replace_name', self.replace_name)
        parser.define('hash_func', self.deid_hash_func)
        parser.define('remove_day', self.remove_day)
        # parse the dataset and apply the deidentification
        parser.parse(strip_sequences=True, remove_private=True)
        return parser.dicom

    # All registered functions that are used in the recipe must
    # receive the arguments: `item`, `value`, `field`, `dicom`

    def deid_hash_func(self, item, value, field, dicom) -> str:
        """Performs self.hash to field.element.value"""
        val = field.element.value
        return self.hash(str(val))

    @staticmethod
    def remove_day(item, value, field, dicom) -> str:
        """Removes the day from a DT field in the deid framework"""
        dt = datetime.strptime(field.element.value, '%Y%m%d')
        return dt.strftime("%Y%m01")

    @staticmethod
    def replace_name(item, value, field, dicom) -> str:
        """Replace PatientName with PatientSex and coarse PatientAge"""
        sex = dicom.get('PatientSex')
        sex = {"F":'Female', "M": 'Male', 'O':'Other'}[sex]
        age = DeidDataset.round_to_nearest(int(dicom.get('PatientAge')[:-1]), 5)
        return f"{sex} {age:03d}Y {dicom.get('Modality')}"

    # Helper methods for our registered ones
    @staticmethod
    def round_to_nearest(value, interval):
        """Rounds value to closest multiple of interval"""
        return interval * round(value/interval)

    def hash(self, msg: str) -> str:
        """
        :param msg: message that we want to encrypt,
         normally the PatientID or the StudyID.
        :return: the encrypted message as hexdigest
         (in characters from '0' to '9' and 'a' to 'f')
        """
        assert type(msg) == str, f"value is not of type str, {type(msg)}"
        h = SHA512.new(truncate="256")
        bytes_str = bytes(f"{self.secret_salt}{msg}", "utf-8")
        h.update(bytes_str)
        return str(h.hexdigest())

# Load the pydicom Dataset
import json

# Unorthodox way of loading a pydicom.Dataset
# please see pydicom documentation for more information
# on how to load dicom files
with open('my_dicom_file.json') as f:
    dataset_dict = json.load(f)
dataset = pydicom.Dataset.from_json(dataset_dict)

print('Dataset before pseudonymization')
print(dataset)

#create an instance of our class
deid_ds = DeidDataset("!2#4%6&7abc", 'my_deid_recipe.dicom')

#pseudonymize the dataset
print('\nDataset after pseudonymization')
pseudonymized = deid_ds.pseudonymize(dataset)
print(pseudonymized)
```

If we execute our python module

```bash
python my_module.py
```

It will give us the following output:
```
Dataset before pseudonymization
(0008, 0005) Specific Character Set              CS: 'ISO_IR 100'
(0008, 0008) Image Type                          CS: ['DERIVED', 'PRIMARY']
(0008, 0016) SOP Class UID                       UI: Digital Mammography X-Ray Image Storage - For Presentation
(0008, 0020) Study Date                          DA: '20220627'
(0008, 0021) Series Date                         DA: '20220627'
(0008, 0022) Acquisition Date                    DA: '20220627'
(0008, 0023) Content Date                        DA: '20220627'
(0008, 0030) Study Time                          TM: '080803'
(0008, 0033) Content Time                        TM: '080808.202000'
(0008, 0060) Modality                            CS: 'MG'
(0010, 0010) Patient's Name                      PN: 'Maria^Doe'
(0010, 0020) Patient ID                          LO: '1234567890'
(0010, 0030) Patient's Birth Date                DA: '19900606'
(0010, 0040) Patient's Sex                       CS: 'F'
(0010, 1010) Patient's Age                       AS: '032Y'
(0020, 0010) Study ID                            SH: 'mammogram87654'

Dataset after pseudonymization
(0008, 0005) Specific Character Set              CS: 'ISO_IR 100'
(0008, 0008) Image Type                          CS: ['DERIVED', 'PRIMARY']
(0008, 0016) SOP Class UID                       UI: Digital Mammography X-Ray Image Storage - For Presentation
(0008, 0020) Study Date                          DA: '20220627'
(0008, 0023) Content Date                        DA: '20220627'
(0008, 0060) Modality                            CS: 'MG'
(0010, 0010) Patient's Name                      PN: 'Female 030Y MG'
(0010, 0020) Patient ID                          LO: 'df65775690879c36437ae950c52d025102a1f9b8c8132f8b017f14e9ec45eacb'
(0010, 0030) Patient's Birth Date                DA: '19900601'
(0012, 0062) Patient Identity Removed            CS: 'Yes'
(0012, 0063) De-identification Method            LO: 'my_deid_recipe.dicom.v1.0'
(0020, 0010) Study ID                            SH: 'ae4b477e5709d0c1f746e0adc9ab552fee100b91416f9f3a04037e999077e823'
```
