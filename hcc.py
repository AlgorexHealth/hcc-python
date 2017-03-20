from enum import Enum,IntEnum
from functools import reduce
from datetime import datetime
from pyDatalog import pyDatalog

def age_as_of(dob,date_as_of):
  return date_as_of.year - dob.year - ((date_as_of.month, date_as_of.day) < (dob.month, dob.day))

class EntitlementReason(IntEnum):
  OASI=0
  DIB=1
  ESRD=2
  DIB_AND_ESRD = 3

class ICDType(IntEnum):
  NINE = 9
  TEN = 0

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

  def __repr__(self): # specifies how to display an Employee
    return str(self.hicno)

  def add_diagnosis(self,diag):
    self.diagnoses.append(diag)


# lines 352 - 361
def load_diagnostic_category_facts():
  diagnostic_categories = [
          ("cancer",["8","9","10","11","12"]),
          ("diabetes",["17","18","19"]),
          ("immune",["47"]),
          ("card_resp_fail",["82","83","84"]),
          ("chf",["85"]),
          ("copd",["110","111"]),
          ("renal",[str(x) for x in range(134,142)]),
          ("compl",["176"]),
          ("pressure_ulcer",["157","158","159","160"]),
          ("sepsis",["2"]) ]
  for dc, ccs in diagnostic_categories:
    for cc in ccs:
      pyDatalog.assert_fact('dc',dc,cc)

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

pyDatalog.create_terms('b,dc,overrides,has_cc_that_overrides_this_one,beneficiary_has_hcc,Type,OT,beneficiary_has_cc,cc,CC,CC2,ICD,edit,male,B,Diag,Ben,female,medicaid,age,A,old_age_entitled,new_enrollee,D,ben_hcc')
pyDatalog.create_terms('sepsis_card_resp_fail,cancer_immune,diabetes_chf,chf_copd,chf_renal, copd_card_resp_fail')
pyDatalog.create_terms('sepsis_pressure_ulcer, sepsis_artif_openings, art_openings_pressure_ulcer, diabetes_chf, copd_asp_spec_bact_pneum, asp_spec_bact_pneum_pres_ulc, sepsis_asp_spec_bact_pneum, schizophrenia_copd, schizophrenia_chf, schizophrenia_seizures,sex_age_range,U,L,f0_34,hcc8 ')

def load_facts():
  load_cc_facts("icd10.txt",0)
  load_cc_facts("icd9.txt",9)
  load_hcc_facts()
  load_diagnostic_category_facts()
  
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
  ben_hcc(B,CC) <= beneficiary_has_hcc(B,CC)

  edit(ICD,0,B,"48")  <= female(B) & (ICD.in_(["D66", "D67"]))
  edit(ICD,0,B,"112") <= (Ben.age[B] < 18) & (ICD.in_(["J410", 
                                 "J411", "J418", "J42",  "J430",
                                 "J431", "J432", "J438", "J439", "J440",
                                 "J441", "J449", "J982", "J983"]))

  # lines 363 - 368
  sepsis_card_resp_fail(CC,CC2) <= dc("sepsis",CC) & dc("card_resp_fail",CC2)
  cancer_immune(CC,CC2) <= dc("cancer",CC) & dc("immune",CC2)
  diabetes_chf(CC,CC2) <= dc("diabetes",CC) & dc("chf",CC2)
  chf_copd(CC,CC2) <= dc("chf",CC) & dc("copd",CC2)
  chf_renal(CC,CC2) <= dc("chf",CC) & dc("renal",CC2)
  copd_card_resp_fail(CC,CC2) <= dc("copd",CC) & dc("card_resp_fail",CC2)

  # PRESSURE_ULCER = MAX(HCC157, HCC158, HCC159, HCC160);
  sepsis_pressure_ulcer(CC,CC2) <= dc("sepsis",CC) & dc("pressure_ulcer",CC2) 
  sepsis_artif_openings(CC,"188") <= dc("sepsis",CC)
  art_openings_pressure_ulcer(CC,"188") <= dc("pressure_ulcer",CC)
  diabetes_chf(CC,CC2) <= dc("diabetes",CC) & dc("chf",CC2)
  copd_asp_spec_bact_pneum(CC,"114") <= dc("copd",CC)
  asp_spec_bact_pneum_pres_ulc(CC,"114") <= dc("pressure_ulcer",CC)
  sepsis_asp_spec_bact_pneum(CC,"114") <= dc("sepsis",CC)
  schizophrenia_copd(CC,"57") <= dc("copd",CC)
  schizophrenia_chf(CC,"57") <= dc("chf",CC)
  schizophrenia_seizures("79",CC) <= (CC == "57")

  # these predicates will be used to generate 
  # more specific predicates like "F0_34"
  sex_age_range("male",B,L,U) <= male(B) & age(B,A)& (A <= U) & (A > L) 
  sex_age_range("female",B,L,U) <= female(B) & age(B,A)& (A <= U) & (A > L) 

  f0_34(B) <= sex_age_range("female",B,0,34)
  hcc8(B) <= ben_hcc(B,"8")

def load_all_indicators():
  {'DISABLED_HCC77': (lambda b: predicate),
   'SCHIZOPHRENIA_COPD': (lambda b: predicate),
   'DISABLED_HCC161': (lambda b: predicate),
   'M55_59': (lambda b: predicate),
   'HCC27': (lambda b: predicate),
   'HCC86': (lambda b: predicate),
   'COPD_ASP_SPEC_BACT_PNEUM': (lambda b: predicate),
   'NEF75_79': (lambda b: predicate),
   'MCAID_MALE66_69': (lambda b: predicate),
   'NEM85_89': (lambda b: predicate),
   'NEM55_59': (lambda b: predicate),
   'NEM95_GT': (lambda b: predicate),
   'M65_69': (lambda b: predicate),
   'NEF45_54': (lambda b: predicate),
   'Origdis_male70_74': (lambda b: predicate),
   'F90_94': (lambda b: predicate),
   'M45_54': (lambda b: predicate),
   'HCC170': (lambda b: predicate),
   'F60_64': (lambda b: predicate),
   'HCC79': (lambda b: predicate),
   'NEF0_34': (lambda b: predicate),
   'NEM0_34': (lambda b: predicate),
   'DISABLED_HCC55': (lambda b: predicate),
   'M95_GT': (lambda b: predicate),
   'HCC72': (lambda b: predicate),
   'HCC78': (lambda b: predicate),
   'HCC58': (lambda b: predicate),
   'HCC141': (lambda b: predicate),
   'HCC166': (lambda b: predicate),
   'NEM70_74': (lambda b: predicate),
   'SEPSIS_ASP_SPEC_BACT_PNEUM': (lambda b: predicate),
   'CHF_RENAL': (lambda b: predicate),
   'HCC136': (lambda b: predicate),
   'HCC74': (lambda b: predicate),
   'HCC73': (lambda b: predicate),
   'HCC137': (lambda b: predicate),
   'HCC40': (lambda b: predicate),
   'Origdis_female70_74': (lambda b: predicate),
   'HCC85': (lambda b: predicate),
   'NEF55_59': (lambda b: predicate),
   'F95_GT': (lambda b: predicate),
   'MCAID': (lambda b: predicate),
   'SEPSIS_PRESSURE_ULCER': (lambda b: predicate),
   'HCC103': (lambda b: predicate),
   'HCC106': (lambda b: predicate),
   'OriginallyDisabled_Male': (lambda b: predicate),
   'F45_54': (lambda b: predicate),
   'HCC23': (lambda b: predicate),
   'F55_59': (lambda b: predicate),
   'NEM90_94': (lambda b: predicate),
   'HCC82': (lambda b: predicate),
   'NEF68': (lambda b: predicate),
   'HCC139': (lambda b: predicate),
   'NEF65': (lambda b: predicate),
   'Origdis_female66_69': (lambda b: predicate),
   'MCAID_FEMALE0_64': (lambda b: predicate),
   'MCAID_MALE75_GT': (lambda b: predicate),
   'DISABLED_HCC85': (lambda b: predicate),
   'HCC186': (lambda b: predicate),
   'HCC134': (lambda b: predicate),
   'ORIGDS': (lambda b: predicate),
   'DISABLED_HCC39': (lambda b: predicate),
   'DISABLED_HCC6': (lambda b: predicate),
   'HCC6': (lambda b: predicate),
   'DIABETES_CHF': (lambda b: predicate),
   'HCC51': (lambda b: predicate),
   'HCC80': (lambda b: predicate),
   'MCAID_Female_Aged': (lambda b: predicate),
   'HCC48': (lambda b: predicate),
   'Origdis_male66_69': (lambda b: predicate),
   'HCC173': (lambda b: predicate),
   'HCC33': (lambda b: predicate),
   'Origdis_female75_GT': (lambda b: predicate),
   'HCC70': (lambda b: predicate),
   'HCC83': (lambda b: predicate),
   'HCC84': (lambda b: predicate),
   'HCC108': (lambda b: predicate),
   'NEF70_74': (lambda b: predicate),
   'SEPSIS_ARTIF_OPENINGS': (lambda b: predicate),
   'NEF67': (lambda b: predicate),
   'HCC21': (lambda b: predicate),
   'F0_34': (lambda b: predicate),
   'DISABLED_HCC176': (lambda b: predicate),
   'HCC110': (lambda b: predicate),
   'HCC159': (lambda b: predicate),
   'HCC75': (lambda b: predicate),
   'HCC111': (lambda b: predicate),
   'HCC99': (lambda b: predicate),
   'HCC169': (lambda b: predicate),
   'F80_84': (lambda b: predicate),
   'NEM65': (lambda b: predicate),
   'HCC22': (lambda b: predicate),
   'HCC71': (lambda b: predicate),
   'HCC160': (lambda b: predicate),
   'CANCER_IMMUNE': (lambda b: predicate),
   'HCC162': (lambda b: predicate),
   'MCAID_MALE0_64': (lambda b: predicate),
   'MCAID_MALE65': (lambda b: predicate),
   'COPD_CARD_RESP_FAIL': (lambda b: predicate),
   'HCC140': (lambda b: predicate),
   'HCC57': (lambda b: predicate),
   'HCC157': (lambda b: predicate),
   'DISABLED_HCC34': (lambda b: predicate),
   'HCC77': (lambda b: predicate),
   'NEF35_44': (lambda b: predicate),
   'F75_79': (lambda b: predicate),
   'Origdis_male65': (lambda b: predicate),
   'HCC10': (lambda b: predicate),
   'HCC88': (lambda b: predicate),
   'HCC161': (lambda b: predicate),
   'HCC46': (lambda b: predicate),
   'M60_64': (lambda b: predicate),
   'NEM60_64': (lambda b: predicate),
   'DISABLED_PRESSURE_ULCER': (lambda b: predicate),
   'DISABLED_HCC46': (lambda b: predicate),
   'HCC11': (lambda b: predicate),
   'HCC34': (lambda b: predicate),
   'HCC47': (lambda b: predicate),
   'MCAID_FEMALE70_74': (lambda b: predicate),
   'NEM80_84': (lambda b: predicate),
   'HCC39': (lambda b: predicate),
   'HCC158': (lambda b: predicate),
   'HCC114': (lambda b: predicate),
   'NEM75_79': (lambda b: predicate),
   'OriginallyDisabled_Female': (lambda b: predicate),
   'CHF_COPD': (lambda b: predicate),
   'HCC138': (lambda b: predicate),
   'ART_OPENINGS_PRESSURE_ULCER': (lambda b: predicate),
   'SCHIZOPHRENIA_CHF': (lambda b: predicate),
   'NEF85_89': (lambda b: predicate),
   'NEM45_54': (lambda b: predicate),
   'HCC2': (lambda b: predicate),
   'HCC8': (lambda b: predicate),
   'HCC76': (lambda b: predicate),
   'HCC17': (lambda b: predicate),
   'F70_74': (lambda b: predicate),
   'HCC18': (lambda b: predicate),
   'HCC104': (lambda b: predicate),
   'HCC54': (lambda b: predicate),
   'MCAID_MALE70_74': (lambda b: predicate),
   'MCAID_FEMALE66_69': (lambda b: predicate),
   'F35_44': (lambda b: predicate),
   'HCC12': (lambda b: predicate),
   'M35_44': (lambda b: predicate),
   'MCAID_FEMALE75_GT': (lambda b: predicate),
   'M90_94': (lambda b: predicate),
   'NEF80_84': (lambda b: predicate),
   'NEM67': (lambda b: predicate),
   'HCC96': (lambda b: predicate),
   'NEF95_GT': (lambda b: predicate),
   'F65_69': (lambda b: predicate),
   'HCC176': (lambda b: predicate),
   'NEF69': (lambda b: predicate),
   'NEM69': (lambda b: predicate),
   'MCAID_Male_Aged': (lambda b: predicate),
   'HCC29': (lambda b: predicate),
   'NEF60_64': (lambda b: predicate),
   'NEM66': (lambda b: predicate),
   'HCC9': (lambda b: predicate),
   'HCC1': (lambda b: predicate),
   'HCC188': (lambda b: predicate),
   'HCC122': (lambda b: predicate),
   'M0_34': (lambda b: predicate),
   'HCC55': (lambda b: predicate),
   'HCC115': (lambda b: predicate),
   'HCC87': (lambda b: predicate),
   'HCC167': (lambda b: predicate),
   'NEF90_94': (lambda b: predicate),
   'SCHIZOPHRENIA_SEIZURES': (lambda b: predicate),
   'DISABLED_HCC54': (lambda b: predicate),
   'HCC124': (lambda b: predicate),
   'HCC100': (lambda b: predicate),
   'MCAID_FEMALE65': (lambda b: predicate),
   'HCC28': (lambda b: predicate),
   'HCC135': (lambda b: predicate),
   'Origdis_male75_GT': (lambda b: predicate),
   'M85_89': (lambda b: predicate),
   'Origdis_female65': (lambda b: predicate),
   'M80_84': (lambda b: predicate),
   'MCAID_Male_Disabled': (lambda b: predicate),
   'MCAID_Female_Disabled': (lambda b: predicate),
   'HCC35': (lambda b: predicate),
   'HCC112': (lambda b: predicate),
   'HCC107': (lambda b: predicate),
   'HCC189': (lambda b: predicate),
   'NEM68': (lambda b: predicate),
   'M75_79': (lambda b: predicate),
   'NEM35_44': (lambda b: predicate),
   'ASP_SPEC_BACT_PNEUM_PRES_ULC': (lambda b: predicate),
   'HCC19': (lambda b: predicate),
   'NEF66': (lambda b: predicate),
   'F85_89': (lambda b: predicate),
   'DISABLED_HCC110': (lambda b: predicate),
   'SEPSIS_CARD_RESP_FAIL': (lambda b: predicate),
   'M70_74': (lambda b: predicate),
   'HCC52'}

load_facts()
load_rules()

def community_regression():
  # &COMM_REG
  reg_vars = ["F0_34","F35_44", "F45_54", "F55_59", "F60_64", "F65_69",
  "F70_74", "F75_79", "F80_84", "F85_89", "F90_94", "F95_GT",
  "M0_34","M35_44", "M45_54", "M55_59", "M60_64", "M65_69",
  "M70_74", "M75_79", "M80_84", "M85_89", "M90_94", "M95_GT",
  "MCAID_Female_Aged","MCAID_Female_Disabled",
  "MCAID_Male_Aged","MCAID_Male_Disabled",
  "OriginallyDisabled_Female","OriginallyDisabled_Male",
  "DISABLED_HCC6", "DISABLED_HCC34",
  "DISABLED_HCC46","DISABLED_HCC54",
  "DISABLED_HCC55","DISABLED_HCC110",
  "DISABLED_HCC176", "SEPSIS_CARD_RESP_FAIL",
  "CANCER_IMMUNE", "DIABETES_CHF",
  "CHF_COPD","CHF_RENAL",
  "COPD_CARD_RESP_FAIL",
  "HCC1","HCC2","HCC6","HCC8","HCC9","HCC10", "HCC11", "HCC12", 
  "HCC17", "HCC18", "HCC19", "HCC21", "HCC22", "HCC23", "HCC27", "HCC28",
  "HCC29", "HCC33", "HCC34", "HCC35", "HCC39", "HCC40", "HCC46", "HCC47", 
  "HCC48", "HCC51", "HCC52", "HCC54", "HCC55", "HCC57", "HCC58", "HCC70", 
  "HCC71", "HCC72", "HCC73", "HCC74", "HCC75", "HCC76", "HCC77", "HCC78", 
  "HCC79", "HCC80", "HCC82", "HCC83", "HCC84", "HCC85", "HCC86", "HCC87", 
  "HCC88", "HCC96", "HCC99", "HCC100","HCC103","HCC104","HCC106","HCC107",
  "HCC108","HCC110","HCC111","HCC112","HCC114","HCC115","HCC122","HCC124",
  "HCC134","HCC135","HCC136","HCC137","HCC138","HCC139","HCC140","HCC141",
  "HCC157","HCC158","HCC159","HCC160","HCC161","HCC162","HCC166","HCC167",
  "HCC169","HCC170","HCC173","HCC176","HCC186","HCC188","HCC189" ]
  return reg_vars

def new_enrollee_regression():
  # 
  reg_vars = ["NEF0_34","NEF35_44", "NEF45_54", "NEF55_59", "NEF60_64",
              "NEF65","NEF66","NEF67","NEF68","NEF69",
              "NEF70_74", "NEF75_79", "NEF80_84", "NEF85_89", "NEF90_94", "NEF95_GT",
              "NEM0_34","NEM35_44", "NEM45_54", "NEM55_59", "NEM60_64",
              "NEM65","NEM66","NEM67","NEM68","NEM69",
              "NEM70_74", "NEM75_79", "NEM80_84", "NEM85_89", "NEM90_94", "NEM95_GT",
              "MCAID_FEMALE0_64","MCAID_FEMALE65","MCAID_FEMALE66_69",
              "MCAID_FEMALE70_74", "MCAID_FEMALE75_GT",
              "MCAID_MALE0_64","MCAID_MALE65","MCAID_MALE66_69",
              "MCAID_MALE70_74", "MCAID_MALE75_GT",
              "Origdis_female65", "Origdis_female66_69",
              "Origdis_female70_74","Origdis_female75_GT",
              "Origdis_male65", "Origdis_male66_69",
              "Origdis_male70_74","Origdis_male75_GT"]
  return reg_vars

def institutional_regression():
  # &INST_REG
  reg_vars = ["F0_34","F35_44", "F45_54", "F55_59", "F60_64", "F65_69",
              "F70_74", "F75_79", "F80_84", "F85_89", "F90_94", "F95_GT",
              "M0_34","M35_44", "M45_54", "M55_59", "M60_64", "M65_69",
              "M70_74", "M75_79", "M80_84", "M85_89", "M90_94", "M95_GT",
              "MCAID","ORIGDS",
              "DISABLED_HCC85", "DISABLED_PRESSURE_ULCER",
              "DISABLED_HCC161","DISABLED_HCC39",
              "DISABLED_HCC77", "DISABLED_HCC6",
              "CHF_COPD", "COPD_CARD_RESP_FAIL",
              "SEPSIS_PRESSURE_ULCER",
              "SEPSIS_ARTIF_OPENINGS",
              "ART_OPENINGS_PRESSURE_ULCER",
              "DIABETES_CHF",
              "COPD_ASP_SPEC_BACT_PNEUM",
              "ASP_SPEC_BACT_PNEUM_PRES_ULC",
              "SEPSIS_ASP_SPEC_BACT_PNEUM",
              "SCHIZOPHRENIA_COPD",
              "SCHIZOPHRENIA_CHF",
              "SCHIZOPHRENIA_SEIZURES",
              "HCC1","HCC2","HCC6","HCC8","HCC9","HCC10", "HCC11", "HCC12", 
              "HCC17", "HCC18", "HCC19", "HCC21", "HCC22", "HCC23", "HCC27", "HCC28",
              "HCC29", "HCC33", "HCC34", "HCC35", "HCC39", "HCC40", "HCC46", "HCC47", 
              "HCC48", "HCC51", "HCC52", "HCC54", "HCC55", "HCC57", "HCC58", "HCC70", 
              "HCC71", "HCC72", "HCC73", "HCC74", "HCC75", "HCC76", "HCC77", "HCC78", 
              "HCC79", "HCC80", "HCC82", "HCC83", "HCC84", "HCC85", "HCC86", "HCC87", 
              "HCC88", "HCC96", "HCC99", "HCC100","HCC103","HCC104","HCC106","HCC107",
              "HCC108","HCC110","HCC111","HCC112","HCC114","HCC115","HCC122","HCC124",
              "HCC134","HCC135","HCC136","HCC137","HCC138","HCC139","HCC140","HCC141",
              "HCC157","HCC158","HCC159","HCC160","HCC161","HCC162","HCC166","HCC167",
              "HCC169","HCC170","HCC173","HCC176","HCC186","HCC188","HCC189" ]
  return reg_vars 


####################################################

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

print("bottom")

def a(query):
  answer =pyDatalog.ask(query) 
  if answer != None:
    return (True, answer.answers)
  else:
    return (False,None)

def a2(results):
  if len(results) > 0:
    return True
  else:
    return False


