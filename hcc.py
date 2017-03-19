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

CC_LOOKUP = {}
LR_COEFFICIENTS = {"institutional":{"label2":0.4,"label":0.4},
                    "new_enrollee":{"label":0.4},
                    "community":{"label":0.4}}

def load_LR_COEFFICIENTS():
  return CC_LOOKUP

def load_CC_LOOKUP():
  return CC_LOOKUP

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

from enum import Enum,IntEnum
from functools import reduce
from datetime import datetime
from pyDatalog import pyDatalog

class EntitlementReason(IntEnum):
  OASI=0
  DIB=1
  ESRD=2
  DIB_AND_ESRD = 3

class ICDType(IntEnum):
  NINE = 9
  TEN = 0

def age_as_of(dob,date_as_of):
  return date_as_of.year - dob.year - ((date_as_of.month, date_as_of.day) < (dob.month, dob.day))

class Diagnosis(pyDatalog.Mixin):
  def __init__(self,
              beneficiary,
              icdcode,
              codetype=ICDType.NINE):
    super().__init__()
    self.beneficiary = beneficiary
    self.icdcode = icdcode
    self.codetype = codetype

  def __repr__(self): # specifies how to display an Employee
    return str(beneficiary) + str(self.icdcode) + str(self.codetype)


class Beneficiary(pyDatalog.Mixin):
  def __init__(self,
              hicno,sex,dob,
              original_reason_entitlement=EntitlementReason.OASI,
              medicaid=False,
              newenrollee_medicaid=False,):
    super().__init__()
    self.hicno = hicno
    self.sex = sex
    self.dob = datetime.strptime(dob,"%Y%m%d")
    self.age = age_as_of(self.dob,datetime.now())
    self.medicaid = medicaid
    self.newenrollee_medicaid = newenrollee_medicaid
    self.original_reason_entitlement = original_reason_entitlement
    self.diagnoses = []
    self.agesexv = dict([
                ("F0_34",False),  ("F35_44",False), ("F45_54",False), ("F55_59",False), ("F60_64",False), ("F65_69",False),
                ("F70_74",False), ("F75_79",False), ("F80_84",False), ("F85_89",False), ("F90_94",False), ("F95_GT",False),
                ("M0_34",False),  ("M35_44",False), ("M45_54",False), ("M55_59",False), ("M60_64",False), ("M65_69",False),
                ("M70_74",False), ("M75_79",False), ("M80_84",False), ("M85_89",False), ("M90_94",False), ("M95_GT",False),
                  ])

  def __repr__(self): # specifies how to display an Employee
    return str(self.hicno)

  def add_diagnosis(self,diag):
    self.diagnoses.append(diag)

  # date_as_of in YYYYmmdd format

  def set_cc(self,ccs):
    self.ccs = ccs

# bene should be an array of Beneficiary objects with
# multiple Diagnosis objects attached
def score_beneficiaries(bene):
  results = []
  for b in bene:
    for d in b.diagnoses:
      edit_diagnosis(b,d) # either &EDITMAC9 or &EDITMAC0
      create_category_coding(b,d) # INPUT(LEFT(PUT(DIAG,$I9&FMNAME9..)),4.)  -- as an example
    create_demographics(b)  #  &AGESEXMAC(AGEF=AGEF, SEX=SEX, OREC=OREC)
    create_hcc(b)
    create_interactions(b)
    create_disabled_interactions(b)
    scores = score(b)
    print("score is",b.__dict__)
    results.append( (b,scores) )
  return results

def output_beneficiaries(beneficiary_scores_tuple):
  for b,scores in beneficiary_scores_tuple:
    print("beneficiary",b.dob)

def score(b):
  def r(typez):
    coef = LR_COEFFICIENTS[typez]
    def reductor( score,label ):
      if label in coef:
        score += coef[label]
      return score
    return reduce( reductor ,b.get_variables(typez),0)
  community_score =      r("community")
  institutional_score =  r("institutional")
  new_enrollee_score =   r("new_enrollee")
  return (community_score,institutional_score,new_enrollee_score) 

def edit_diagnosis(beneficiary,diagnosis):
  if EDITS_ON:
    print("editing digansis")
    
# Category Codings are assigned to the Beneficiary (as a rollup)
# and not the diagnosis, as multiple diagnoses in the same category
# are compressed into one category
def create_category_coding(b,d):
  if not CC_LOOKUP:
    load_CC_LOOKUP()
  key = (d.icdcode,d.codetype)
  if key in CC_LOOKUP:
    ccs = CC_LOOKUP[key]
    b.set_cc(ccs)
  return b

def create_hcc(beneficiary):
  ""

# put people into buckets
# based on their age
# also set originalds and disabled
def create_demographics(bene):
  ""

def create_interactions(bene):
  ""

def create_disabled_interactions(bene):
  ""

def a(query):
  answer =pyDatalog.ask(query) 
  if answer != None:
    return (True, answer.answers)
  else:
    return (False,None)


def load_cc_facts(f,icdcodetype):
  file = open(f, 'r')                                     
  for line in file:
    vals = line.split()
    if len(vals) == 2:
      icd,cc = vals
    elif len(vals) == 3:
      icd,cc,_ = vals
    pyDatalog.assert_fact('cc',icd,cc,icdcodetype) 

def load_hcc_facts():
  overriders = [
          ("8",["9","10","11","12" ]),
          ("9",["10","11","12" ]),
          ("10",["11","12" ]),
          ("11",["12" ]),
          ("17",["18","19" ]),
          ("18",["19" ]),
          ("27",["28","29","80" ]),
          ("28",["29" ]),
          ("46",["48" ]),
          ("51",["52" ]),
          ("54",["55" ]),
          ("57",["58" ]),
          ("70",["71","72","103","104","169" ]),
          ("71",["72","104","169" ]),
          ("72",["169" ]),
          ("82",["83","84" ]),
          ("83",["84" ]),
          ("86",["87","88" ]),
          ("87",["88" ]),
          ("99",["100" ]),
          ("103",["104" ]),
          ("106",["107","108","161","189" ]),
          ("107",["108" ]),
          ("110",["111","112" ]),
          ("111",["112" ]),
          ("114",["115" ]),
          ("134",["135","136","137","138","139","140","141"]),
          ("135",["136","137","138","139","140","141" ]),
          ("136",["137","138","139","140","141" ]),
          ("137",["138","139","140","141" ]),
          ("138",["139","140","141" ]),
          ("139",["140","141" ]),
          ("140",["141" ]),
          ("157",["158","159","160","161" ]),
          ("158",["159","160","161" ]),
          ("159",["160","161" ]),
          ("160",["161" ]),
          ("166",["80","167" ])
          ]
  for overrider, overridees in overriders:
    for overridee in overridees:
      pyDatalog.assert_fact('overrides',overrider,overridee)

def load_facts():
  load_cc_facts("icd10.txt",0)
  load_cc_facts("icd9.txt",9)
  load_hcc_facts()

    

jane = Beneficiary(2,"female","19740824",EntitlementReason.DIB,True)
jane.add_diagnosis(Diagnosis(jane,"D66",ICDType.TEN))  
jane.add_diagnosis(Diagnosis(jane,"C182",ICDType.TEN))  

daniel = Beneficiary(1,"male","19740824")
daniel.add_diagnosis(Diagnosis(daniel,"A0223",ICDType.TEN))  # 51
daniel.add_diagnosis(Diagnosis(daniel,"A0224",ICDType.TEN))  # 52
daniel.add_diagnosis(Diagnosis(daniel,"C163",ICDType.TEN))  
daniel.add_diagnosis(Diagnosis(daniel,"C163",ICDType.TEN))  
daniel.add_diagnosis(Diagnosis(daniel,"C182",ICDType.TEN))  
daniel.add_diagnosis(Diagnosis(daniel,"C800",ICDType.TEN))  
daniel.add_diagnosis(Diagnosis(daniel,"A072",ICDType.TEN))  
bob = Beneficiary(3,"male","20040824",EntitlementReason.DIB,True)
bob.add_diagnosis(Diagnosis(bob,"A0223",ICDType.TEN))
bob.add_diagnosis(Diagnosis(bob,"A0224",ICDType.TEN))
jacob = Beneficiary(4,"male","1940824",EntitlementReason.DIB,True)


pyDatalog.create_terms('overrides,has_cc_that_overrides_this_one,beneficiary_has_hcc,Type,OT,beneficiary_has_cc,cc,CC,CC2,ICD,edit,male,B,Diag,Ben,female,medicaid,age,A,old_age_entitled,new_enrollee,D')

def load_rules():
  Ben = Beneficiary
  Diag = Diagnosis

  male(B) <=  (Ben.sex[B] == "male")
  female(B) <=  (Ben.sex[B] == "female")
  medicaid(B) <= (Ben.medicaid[B] == True)
  age(B,A) <= (Ben.age[B] == A)
  old_age_entitled(B) <= (Ben.original_reason_entitlement[B] == EntitlementReason.OASI)
  new_enrollee(B)  <= (Ben.newenrollee_medicaid[B] == True)

  beneficiary_has_cc(B,CC) <= (Diag.beneficiary[D] == B)  & edit(Diag.icdcode[D],Diag.codetype[D],B,CC)
  beneficiary_has_cc(B,CC) <= (Diag.beneficiary[D] == B)  & cc(Diag.icdcode[D],CC,
                                        Diag.codetype[D]) & ~(edit(Diag.icdcode[D],Diag.codetype[D],B,CC2))
  has_cc_that_overrides_this_one(B,CC) <=  beneficiary_has_cc(B,OT)  & overrides(OT,CC)
  beneficiary_has_hcc(B,CC) <= beneficiary_has_cc(B,CC) & ~( has_cc_that_overrides_this_one(B,CC))


  edit(ICD,0,B,"48")  <= female(B) & (ICD.in_(["D66", "D67"]))
  edit(ICD,0,B,"112") <= (Ben.age[B] < 18) & (ICD.in_(["J410", 
                                 "J411", "J418", "J42",  "J430",
                                 "J431", "J432", "J438", "J439", "J440",
                                 "J441", "J449", "J982", "J983"]))


diagnostic_categories_logic = """
+  scurvy("6") 
+  cancer("8") 
+  cancer("9") 
+  cancer("10") 
+  cancer("11") 
+  diabetes("17") 
+  diabetes("18") 
+  diabetes("19") 
+  immune("11") 
+  sepsis("2") 
+  card_resp_failure("11") 
+  card_resp_failure("11") 
+  card_resp_failure("11") 
+  pressure_ulcer("157") 
+  pressure_ulcer("158") 
+  pressure_ulcer("159") 
+  pressure_ulcer("160") 
"""

interaction_logic = """
sepsis_pressure_ulcer(CC,CC2) <= sepsis(CC) & pressure_ulcer(CC2)
scurvy_and_cancer(CC,CC2) <= scurvy(CC) & cancer(CC2)
ben_has_scurvy_and_cancer(B) <= bhc(B,CC) & bhc(B,CC2) & scurvy_and_cancer(CC,CC2)
ben_has_sepsis_pressure_ulcer(B) <= bhc(B,CC) & bhc(B,CC2) & sepsis_pressure_ulcer(CC,CC2)
bhc(B,CC) <= beneficiary_has_hcc(B,CC)
"""

inst_model = [
  ("ben_has_scurvy_and_cancer",0.32),
  ("ben_has_scurvy_and_cancer",0.52)
]

all_rules = diagnostic_categories_logic + interaction_logic


load_rules()
load_facts()

pyDatalog.load(all_rules)
print("bottom")
