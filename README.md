# hcc-python
An implementation of the HCC Risk Adjustment Algorithm in Python and pyDatalog.


![ explanation ](execution-of-model.png)

## Motivation:
CMS Publishes code for health systems and other interested parties to run their population against an
HCC Risk model.  Although this model is 'free' as it is published by CMS [ here ](https://www.cms.gov/Medicare/Health-Plans/MedicareAdvtgSpecRateStats/Risk-Adjustors-Items/Risk2016.html?DLPage=1&DLEntries=10&DLSort=0&DLSortDir=descending), it comes with an implicit tax by 
being published in SAS:
  * SAS is not open-source and has a high yearly seat-license cost
  * SAS is NOT a useful language in the sense of other useful general purpose or stastitcal langugages 

Our hope with this repository is to engage the community by providing a free version of this algorithm in Python (specifically Python3).

This repository is **not** a means by which to generate a linear regression model.  It is instead the code to run 
the pre-existing HCC model (which had been generated against a national medicare population) against a list of beneficiaries and their diagnoses.

## Contents 
This repository contains the `hcc.py` library which implements the HCC summing algorithm. It also contains a mapping from ICD codes (both 9 and 10) to code categories, and mappings of code categories over others (called hierarchies).   All of these data files must be present to work properly.

Other files in this repository are expository (pngs, reference SAS code, and jupyter notebooks).

In summary, the following files are critical for running HCC on your own using python.
  * hcc.py  
  * icd10.txt 
  * icd9.txt 
  * coefficients.txt

## Implementation
The HCC Risk Adjustment algorithm is a linear regression model summing hundreds of independent variables to a single dependent variable called a risk score.
These independent variables are either engaged or not, and their associated coefficients are either added to the ongoing sum or not.  We show this diagramatically as such:

![ explanation ](model.png)

As you can see, the model (community in this case) is merely a sum of coefficients.  If a beneficiary and their diagnoses triggers one of these independent variables, it will add an incremental value to their risk score.  That incremental value is the calculated coefficient for that effect.

The following legend gives names to these components:

![ explanation ](legend.png)

## Usage
At this time

## Remaining Items




This model is a series of coefficients tied to 
  * ICD-9 Procedure Codes
    * HCPC/CPT Procedure Codes
      * DRG Codes


