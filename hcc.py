 #####################################
 #  The following is a set of comments copied from SAS code
 #  which will be used to guide the structure of this python code
 # -----------------------------------
 # Program steps:
 #X        step1: include external macros
 #X        step2: define internal macro variables
 #X        step3: merge person and diagnosis files outputting one
 #X               record per person for each input person level record
 #X        step3.1: declaration section
 #X        step3.2: bring regression coefficients
 #X        step3.3: merge person and diagnosis file
 #         step3.4: for the first record for a person set CC to 0
 #                  and calculate age
 #         step3.5: if there are any diagnoses for a person
 #                  then do the following:
 #                   - perform ICD9 edits using V21I9ED1 macro or
 #                     perform ICD10 edits using V21I0ED1 macro
 #                   - create CC using provided format 
 #                   - create additional CC using additional formats
 #         step3.6: for the last record for a person do the
 #                  following:
 #                   - create demographic variables needed
 #                     for regressions (macro AGESEXV2)
 #                   - create HCC using hierarchies (macro V20H87H1)
 #                   - create HCC interaction variables
 #                   - create HCC and DISABL interaction variables
 #                   - set HCCs and interaction vars to zero if there
 #                     are no diagnoses for a person
 #                   - create score for community model
 #                   - create score for institutional model
 #                   - create score for new enrollee model
 #                   - normalize score if needed

# bene is a class
EDITS_ON = True
#    
#    Data requirements for the SAS input files. The variable
#    names listed are required by the programs as written:
#    1) PERSON file
#    x HICNO (or other person identification variable. It
#    must be set in the macro variable IDVAR)
#    -character or numeric type and unique to an individual
#    x SEX
#    -one character, 1=male; 2=female
#    x DOB
#    - SAS date format, date of birth
#    x MCAID
#    -numeric, =1 if number of months in Medicaid in base
#    year >0,
#    =0 otherwise
#    x NEMCAID
#    -numeric, =1 if a new Medicare enrollee and number of
#    months in Medicaid in payment year >0;
#    =0 otherwise
#    x OREC
#    -one character, original reason for entitlement with
#    the following values:
#    0 - OLD AGE (OASI)
#    1 - DISABILITY (DIB)
#    2 – ESRD
#    3 - BOTH DIB AND ESRD

from enum import Enum 
from datetime import datetime

class EntitlemenReason(Enum):
  OASI=0
  DIB=1
  ESRD=2
  DIB_AND_ESRD = 3

class ICDType(Enum):
  NINE = 9
  TEN = 0


class Diagnosis:
  def __init__(self,
              icdcode,
              codetype=ICDType.NINE):
    self.icdcode = icdcode
    self.codetype = codetype

class Beneficiary:
  def __init__(self,
              hicno,sex,dob,
              original_reason_entitlement=EntitlemenReason.OASI,
              medicaid=False,
              newenrollee_medicaid=False,):
    self.hicno = hicno
    self.sex = sex
    self.dob = datetime.strptime(dob,"%Y%m%d")
    self.medicaid = medicaid
    self.newenrollee_medicaid = newenrollee_medicaid
    self.original_reason_entitlement = original_reason_entitlement
    self.diagnoses = []

  def add_diagnosis(self,diag):
    self.diagnoses.append(diag)

  # date_as_of in YYYYmmdd format
  def age_as_of(self,date_as_of):
    return date_as_of.year - self.dob.year - ((date_as_of.month, date_as_of.day) < (self.dob.month, self.dob.day))

def score_beneficiaries(bene):
  results = []
  for b in bene:
    for d in b.diagnoses:
      edit_diagnosis(b,d)
      create_category_coding(d)
      print("eu",b.age_as_of(datetime.today()))
    create_demographics(b)
    create_hcc(b)
    create_interactions(b)
    create_disabled_interactions(b)
    scores = score(b)
    results.append( (b,scores) )


def score(b):
  (23,34,44) 


def edit_diagnosis(beneficiary,diagnosis):
  if EDITS_ON:
    print("editing digansis")
    
def create_category_coding(d):
  ""

def create_hcc(beneficiary):
  ""

def create_demographics(bene):
  ""

def create_interactions(bene):
  ""

def create_disabled_interactions(bene):
  ""

x = Beneficiary("eu",232,"19430302")
x.add_diagnosis(Diagnosis("343",ICDType.TEN))
x.add_diagnosis(Diagnosis("234",ICDType.TEN))
score_beneficiaries([x])


