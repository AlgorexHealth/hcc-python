from enum import Enum,IntEnum
from functools import reduce
from datetime import datetime
from pyDatalog import pyDatalog
import os

pyDatalog.create_terms("""
output,Col,Val,score_em,Score,score,Scores,NE,INS,CE,institutional_score,age_range,
new_enrollee_score,community_score,Pair,Coef,coefficient,b,dc,overrides,wrap,
has_cc_that_overrides_this_one,beneficiary_has_hcc,Type,OT,beneficiary_has_cc,cc,CC,CC2,
ICD,edit,male,B,Diag,Ben,female,medicaid,age,A,old_age_entitled,new_enrollee,D,ben_hcc,
sepsis_card_resp_fail,cancer_immune,diabetes_chf,chf_copd,chf_renal,copd_card_resp_fail,
sepsis_pressure_ulcer, sepsis_artif_openings,art_openings_pressure_ulcer, diabetes_chf,
 copd_asp_spec_bact_pneum,asp_spec_bact_pneum_pres_ulc, sepsis_asp_spec_bact_pneum,
 schizophrenia_copd,schizophrenia_chf,schizophrenia_seizures,sex_age_range,U,L,disabled,
originally_disabled,ben_hcc,sex_age,MF,indicator,excised,beneficiary_icd,CC,B,
valid_community_variables,valid_institutional_variables,valid_new_enrollee_variables,indicator
""")
pyDatalog.create_terms("X,Y,Z")


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
    return str(self.beneficiary) + str(self.icdcode) + str(self.codetype)

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
    return "ID:" + str(self.hicno) + ",DOB:" + str(self.dob)

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
  for dcE, ccs in diagnostic_categories:
    for ccE in ccs:
      + dc(dcE,ccE)

def load_coefficients(f):
  dir = os.path.dirname(__file__)
  file = open(os.path.join(dir,f), 'r')                                     
  for line in file:
    vals = list(map(lambda s: s.strip(),line.split(",")))
    label,coeff = vals
    + coefficient(label,float(coeff)) 
  + coefficient('starting',0.00)

def load_cc_facts(f,icdcodetype):
  dir = os.path.dirname(__file__)
  file = open(os.path.join(dir,f), 'r')                                     
  for line in file:
    vals = line.split()
    if len(vals) == 2:
      icdE,ccE = vals
    elif len(vals) == 3:
      icdE,ccE,_ = vals
    + cc(icdE,ccE,icdcodetype) 

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
      + overrides(overrider,overridee)

def load_facts():
  
  load_cc_facts("icd10.txt",0)
  load_cc_facts("icd9.txt",9)
  load_hcc_facts()
  load_diagnostic_category_facts()
  load_coefficients("coefficients.txt")
  
def community_regression():
  # &COMM_REG
  reg_vars = ["F0_34","F35_44", "F45_54", "F55_59", "F60_64", "F65_69",
  "F70_74", "F75_79", "F80_84", "F85_89", "F90_94", "F95_GT",
  "M0_34","M35_44", "M45_54", "M55_59", "M60_64", "M65_69",
  "M70_74", "M75_79", "M80_84", "M85_89", "M90_94", "M95_GT",
  "MCAID_Female_Aged","MCAID_Female_Disabled",
  "MCAID_Male_Aged","MCAID_Male_Disabled",
  "OriginallyDisabled_Female","OriginallyDisabled_Male",
  "DISABLED_HCC6", "DISABLED_HCC34", "DISABLED_HCC46","DISABLED_HCC54",
  "DISABLED_HCC55","DISABLED_HCC110", "DISABLED_HCC176", "SEPSIS_CARD_RESP_FAIL",
  "CANCER_IMMUNE", "DIABETES_CHF", "CHF_COPD","CHF_RENAL", "COPD_CARD_RESP_FAIL",
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
  reg_vars = ["F0_34","F35_44", "F45_54", "F55_59", "F60_64", "F65_69",
              "F70_74", "F75_79", "F80_84", "F85_89", "F90_94", "F95_GT",
              "M0_34","M35_44", "M45_54", "M55_59", "M60_64", "M65_69",
              "M70_74", "M75_79", "M80_84", "M85_89", "M90_94", "M95_GT",
              "MCAID","ORIGDS", "DISABLED_HCC85", "DISABLED_PRESSURE_ULCER",
              "DISABLED_HCC161","DISABLED_HCC39", "DISABLED_HCC77", "DISABLED_HCC6",
              "CHF_COPD", "COPD_CARD_RESP_FAIL", "SEPSIS_PRESSURE_ULCER", "SEPSIS_ARTIF_OPENINGS",
              "ART_OPENINGS_PRESSURE_ULCER", "DIABETES_CHF", "COPD_ASP_SPEC_BACT_PNEUM", "ASP_SPEC_BACT_PNEUM_PRES_ULC",
              "SEPSIS_ASP_SPEC_BACT_PNEUM", "SCHIZOPHRENIA_COPD", "SCHIZOPHRENIA_CHF", "SCHIZOPHRENIA_SEIZURES",
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

def load_rules():
  Ben = Beneficiary
  Diag = Diagnosis

  male(B) <=  (Ben.sex[B] == "male")
  female(B) <=  (Ben.sex[B] == "female")
  medicaid(B) <= (Ben.medicaid[B] == True)
  age(B,A) <= (Ben.age[B] == A)
  old_age_entitled(B) <= (Ben.original_reason_entitlement[B] == EntitlementReason.OASI)
  new_enrollee(B)  <= (Ben.newenrollee_medicaid[B] == True)

  #    %* disabled;
  #    DISABL = (&AGEF < 65 & &OREC ne "0");
  disabled(B) <= (Ben.age[B] < 65) & ~(old_age_entitled(B))
  #    %* originally disabled: CHANGED FIRST TIME FOR THIS SOFTWARE;
  #    ORIGDS  = (&OREC = '1')*(DISABL = 0);
  originally_disabled(B) <= (Ben.original_reason_entitlement[B] == EntitlementReason.DIB) & ~(disabled(B))

  edit(ICD,9,B,"48")  <= female(B) & (ICD.in_(["2860", "2861"]))
  edit(ICD,9,B,"112") <= age(B,A)  & (A < 18) & \
                              (ICD.in_(["4910", "4911", "49120", "49121", "49122",
                                        "4918", "4919", "4920",  "4928",  "496",  
                                        "5181", "5182"]))
  edit(ICD,0,B,"48")  <= female(B) & (ICD.in_(["D66", "D67"]))
  edit(ICD,0,B,"112") <= age(B,A)  & (A < 18) & (ICD.in_(["J410", 
                                 "J411", "J418", "J42",  "J430",
                                 "J431", "J432", "J438", "J439", "J440",
                                 "J441", "J449", "J982", "J983"]))

  #IF &AGE < 18 AND &ICD9 IN ("49320", "49321", "49322") 
  #                                           THEN CC="-1.0";
  excised(ICD,9,B) <= age(B,A)  & (A < 18) & (ICD.in_(["49320", "49321", "49322"]))

  beneficiary_icd(B,ICD,Type) <= (Diag.beneficiary[D] == B) & (Diag.icdcode[D]==ICD) & (Diag.codetype[D]==Type) 
  beneficiary_has_cc(B,CC) <= beneficiary_icd(B,ICD,Type)  & edit(ICD,Type,B,CC) & ~(excised(ICD,Type,B))
  beneficiary_has_cc(B,CC) <= beneficiary_icd(B,ICD,Type)  & \
    cc(ICD,CC,Type) & ~(edit(ICD,Type,B,CC2)) & ~(excised(ICD,Type,B))

  has_cc_that_overrides_this_one(B,CC) <=  beneficiary_has_cc(B,OT)  & overrides(OT,CC)
  beneficiary_has_hcc(B,CC) <= beneficiary_has_cc(B,CC) & ~( has_cc_that_overrides_this_one(B,CC))

  ben_hcc(B,CC) <= beneficiary_has_hcc(B,CC)

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
  age_range(B,L,U) <= age(B,A) & (A <= U) & (A > L) 
  age_range(B,L,-1.0) <= age(B,A) & (A > L) 
  sex_age_range("male",B,L,U) <= male(B) & age_range(B,L,U)
  sex_age_range("female",B,L,U) <= female(B) & age_range(B,L,U)
  sex_age(MF,B,A) <= sex_age_range(MF,B,(A+1),A)
  
  indicator(B,'ART_OPENINGS_PRESSURE_ULCER') <=  ben_hcc(B,CC) & ben_hcc(B,CC2) & art_openings_pressure_ulcer(CC,CC2)
  indicator(B,'ASP_SPEC_BACT_PNEUM_PRES_ULC') <=  ben_hcc(B,CC) & ben_hcc(B,CC2) & asp_spec_bact_pneum_pres_ulc(CC,CC2)
  indicator(B,'CANCER_IMMUNE') <=  ben_hcc(B,CC) & ben_hcc(B,CC2) & cancer_immune(CC,CC2)
  indicator(B,'CHF_COPD') <=  ben_hcc(B,CC) & ben_hcc(B,CC2) & chf_copd(CC,CC2)
  indicator(B,'CHF_RENAL') <=  ben_hcc(B,CC) & ben_hcc(B,CC2) & chf_renal(CC,CC2)
  indicator(B,'COPD_ASP_SPEC_BACT_PNEUM') <=  ben_hcc(B,CC) & ben_hcc(B,CC2) & copd_asp_spec_bact_pneum(CC,CC2)
  indicator(B,'COPD_CARD_RESP_FAIL') <=  ben_hcc(B,CC) & ben_hcc(B,CC2) & copd_card_resp_fail(CC,CC2)
  indicator(B,'DIABETES_CHF') <=  ben_hcc(B,CC) & ben_hcc(B,CC2) & diabetes_chf(CC,CC2)
  indicator(B,'DISABLED_HCC110') <=  ben_hcc(B,'110') & disabled(B)
  indicator(B,'DISABLED_HCC161') <=  ben_hcc(B,'161') & disabled(B)
  indicator(B,'DISABLED_HCC176') <=  ben_hcc(B,'176') & disabled(B)
  indicator(B,'DISABLED_HCC34') <=  ben_hcc(B,'34') & disabled(B)
  indicator(B,'DISABLED_HCC39') <=  ben_hcc(B,'39') & disabled(B)
  indicator(B,'DISABLED_HCC46') <=  ben_hcc(B,'46') & disabled(B)
  indicator(B,'DISABLED_HCC54') <=  ben_hcc(B,'54') & disabled(B)
  indicator(B,'DISABLED_HCC55') <=  ben_hcc(B,'55') & disabled(B)
  indicator(B,'DISABLED_HCC6') <=  ben_hcc(B,'6') & disabled(B)
  indicator(B,'DISABLED_HCC77') <=  ben_hcc(B,'77') & disabled(B)
  indicator(B,'DISABLED_HCC85') <=  ben_hcc(B,'85') & disabled(B)
  indicator(B,'DISABLED_HCC85') <=  ben_hcc(B,CC) & dc(CC,'pressure_ulcer') & disabled(B)
  indicator(B,'F0_34') <=  sex_age_range('female',B,0,34)
  indicator(B,'F35_44') <=  sex_age_range('female',B,35,44)
  indicator(B,'F45_54') <=  sex_age_range('female',B,45,54)
  indicator(B,'F55_59') <=  sex_age_range('female',B,55,59)
  indicator(B,'F60_64') <=  sex_age_range('female',B,60,64)
  indicator(B,'F65_69') <=  sex_age_range('female',B,65,69)
  indicator(B,'F70_74') <=  sex_age_range('female',B,70,74)
  indicator(B,'F75_79') <=  sex_age_range('female',B,75,79)
  indicator(B,'F80_84') <=  sex_age_range('female',B,80,84)
  indicator(B,'F85_89') <=  sex_age_range('female',B,85,89)
  indicator(B,'F90_94') <=  sex_age_range('female',B,90,94)
  indicator(B,'F95_GT') <=  sex_age_range('female',B,95,-1.0)
  hccees = [ 
        '100', '103', '104', '106', '107', '108', '10', '110', '111', '112', '114', '115', 
        '11', '122', '124', '12', '134', '135', '136', '137', '138', '139', '140', '141', 
        '157', '158', '159', '160', '161', '162', '166', '167', '169', '170', '173', '176', 
        '17', '186', '188', '189', '18', '19', '1', '21', '22', '23', '27', '28', '29', '2', 
        '33', '34', '35', '39', '40', '46', '47', '48', '51', '52', '54', '55', '57', '58', 
        '6', '70', '71', '72', '73', '74', '75', '76', '77', '78', '79', '80', '82', '83', 
        '84', '85', '86', '87', '88', '8', '96', '99', '9']
  for i in hccees:
    indicator(B,'HCC' + i ) <=  ben_hcc(B,i) 
  indicator(B,'M0_34') <=  sex_age_range('male',B,0,34)
  indicator(B,'M35_44') <=  sex_age_range('male',B,35,44)
  indicator(B,'M45_54') <=  sex_age_range('male',B,45,54)
  indicator(B,'M55_59') <=  sex_age_range('male',B,55,59)
  indicator(B,'M60_64') <=  sex_age_range('male',B,60,64)
  indicator(B,'M65_69') <=  sex_age_range('male',B,65,69)
  indicator(B,'M70_74') <=  sex_age_range('male',B,70,74)
  indicator(B,'M75_79') <=  sex_age_range('male',B,75,79)
  indicator(B,'M80_84') <=  sex_age_range('male',B,80,84)
  indicator(B,'M85_89') <=  sex_age_range('male',B,85,89)
  indicator(B,'M90_94') <=  sex_age_range('male',B,90,94)
  indicator(B,'M95_GT') <=  sex_age_range('male',B,95,-1.0)

  # THESE NEED TO CHANGE
  indicator(B,'MCAID_FEMALE0_64') <= medicaid(B) & sex_age_range('female',B,0,64)
  indicator(B,'MCAID_FEMALE65') <=  medicaid(B) & sex_age('female',B,65)
  indicator(B,'MCAID_FEMALE66_69') <=  medicaid(B) & sex_age_range('female',B,66,69)
  indicator(B,'MCAID_FEMALE70_74') <= medicaid(B) & sex_age_range('female',B,70,74)
  indicator(B,'MCAID_FEMALE75_GT') <=  medicaid(B) & sex_age_range('female',B,75,-1.0)
  indicator(B,'MCAID_Female_Aged') <=   medicaid(B) & ~disabled(B) & female(B)
  indicator(B,'MCAID_Female_Disabled') <=  medicaid(B) & disabled(B) & male(B)
  indicator(B,'MCAID') <= medicaid(B) 
  indicator(B,'MCAID_MALE0_64') <= medicaid(B) & sex_age_range('male',B,0,64)
  indicator(B,'MCAID_MALE65') <=  medicaid(B) & sex_age('male',B,65)
  indicator(B,'MCAID_MALE66_69') <=  medicaid(B) & sex_age_range('male',B,66,69)
  indicator(B,'MCAID_MALE70_74') <= medicaid(B) & sex_age_range('male',B,70,74)
  indicator(B,'MCAID_MALE75_GT') <=  medicaid(B) & sex_age_range('male',B,75,-1.0)
  indicator(B,'MCAID_Male_Aged') <=  medicaid(B) & ~disabled(B) & male(B)
  indicator(B,'MCAID_Male_Disabled') <=   medicaid(B) & disabled(B) & male(B)
  # -- UNTIL HERE... need to add NEF65 indicator stuff instead of sex_age_range

  indicator(B,'NEM0_34') <=  sex_age_range("male",B,0,34)
  indicator(B,'NEM35_44') <=  sex_age_range("male",B,35,44)
  indicator(B,'NEM45_54') <=  sex_age_range("male",B,45,54)
  indicator(B,'NEM55_59') <=  sex_age_range("male",B,55,59)
  indicator(B,'NEM60_64') <=  sex_age_range("male",B,60,63)
  #        WHEN(&SEX='2' & &AGEF=64 & &OREC NE '0') NE_AGESEX = 5;
  #        WHEN(&SEX='2' & &AGEF=64 & &OREC='0')    NE_AGESEX = 6;
  indicator(B,'NEM60_64') <=  sex_age("male",B,64) & ~(old_age_entitled(B))
  indicator(B,'NEM65') <=  sex_age("male",B,64) & old_age_entitled(B)
  indicator(B,'NEM65') <=  sex_age("male",B,65)
  indicator(B,'NEM66') <=  sex_age("male",B,66)
  indicator(B,'NEM67') <=  sex_age("male",B,67)
  indicator(B,'NEM68') <=  sex_age("male",B,68)
  indicator(B,'NEM69') <=  sex_age("male",B,69)
  indicator(B,'NEM70_74') <=  sex_age_range("male",B,70,74)
  indicator(B,'NEM75_79') <=  sex_age_range("male",B,75,79)
  indicator(B,'NEM80_84') <=  sex_age_range("male",B,80,84)
  indicator(B,'NEM85_89') <=  sex_age_range("male",B,85,89)
  indicator(B,'NEM90_94') <=  sex_age_range("male",B,90,94)
  indicator(B,'NEM95_GT') <=  sex_age_range("male",B,95,-1.0)
  indicator(B,'NEF0_34') <=  sex_age_range("female",B,0,34)
  indicator(B,'NEF35_44') <=  sex_age_range("female",B,35,44)
  indicator(B,'NEF45_54') <=  sex_age_range("female",B,45,54)
  indicator(B,'NEF55_59') <=  sex_age_range("female",B,55,59)
  indicator(B,'NEF60_64') <=  sex_age_range("female",B,60,63)
  #        WHEN(&SEX='2' & &AGEF=64 & &OREC NE '0') NE_AGESEX = 5;
  #        WHEN(&SEX='2' & &AGEF=64 & &OREC='0')    NE_AGESEX = 6;
  indicator(B,'NEF60_64') <=  sex_age("female",B,64) & ~(old_age_entitled(B))
  indicator(B,'NEF65') <=  sex_age("female",B,64) & old_age_entitled(B)
  indicator(B,'NEF65') <=  sex_age("female",B,65)
  indicator(B,'NEF66') <=  sex_age("female",B,66)
  indicator(B,'NEF67') <=  sex_age("female",B,67)
  indicator(B,'NEF68') <=  sex_age("female",B,68)
  indicator(B,'NEF69') <=  sex_age("female",B,69)
  indicator(B,'NEF70_74') <=  sex_age_range("female",B,70,74)
  indicator(B,'NEF75_79') <=  sex_age_range("female",B,75,79)
  indicator(B,'NEF80_84') <=  sex_age_range("female",B,80,84)
  indicator(B,'NEF85_89') <=  sex_age_range("female",B,85,89)
  indicator(B,'NEF90_94') <=  sex_age_range("female",B,90,94)
  indicator(B,'NEF95_GT') <=  sex_age_range("female",B,95,-1.0)
  indicator(B,'Origdis_female65') <=  originally_disabled(B) & indicator(B, 'NEF65')
  indicator(B,'Origdis_female66_69') <=  originally_disabled(B) & indicator(B, 'NEF66')
  indicator(B,'Origdis_female66_69') <=  originally_disabled(B) & indicator(B, 'NEF67')
  indicator(B,'Origdis_female66_69') <=  originally_disabled(B) & indicator(B, 'NEF68')
  indicator(B,'Origdis_female66_69') <=  originally_disabled(B) & indicator(B, 'NEF69')
  indicator(B,'Origdis_female70_74') <=  originally_disabled(B) & indicator(B, 'NEF70_74')
  indicator(B,'Origdis_female75_GT') <=  originally_disabled(B) & sex_age_range("female",B,74,-1.0)
  indicator(B,'Origdis_male65') <=  originally_disabled(B) & indicator(B, 'NEM65')
  indicator(B,'Origdis_male66_69') <=  originally_disabled(B) & indicator(B, 'NEM66')
  indicator(B,'Origdis_male66_69') <=  originally_disabled(B) & indicator(B, 'NEM67')
  indicator(B,'Origdis_male66_69') <=  originally_disabled(B) & indicator(B, 'NEM68')
  indicator(B,'Origdis_male66_69') <=  originally_disabled(B) & indicator(B, 'NEM69')
  indicator(B,'Origdis_male70_74') <=  originally_disabled(B) & indicator(B, 'NEM70_74')
  indicator(B,'Origdis_male75_GT') <=  originally_disabled(B) & sex_age_range("male",B,74,-1.0)
  indicator(B,'ORIGDS') <= originally_disabled(B) 
  indicator(B,'OriginallyDisabled_Female') <=  originally_disabled(B) & female(B)
  indicator(B,'OriginallyDisabled_Male') <=  originally_disabled(B) & male(B)
  indicator(B,'SCHIZOPHRENIA_CHF') <=  ben_hcc(B,CC) & ben_hcc(B,CC2) & schizophrenia_chf(CC,CC2) 
  indicator(B,'SCHIZOPHRENIA_COPD') <= ben_hcc(B,CC) & ben_hcc(B,CC2) & schizophrenia_copd(CC,CC2) 
  indicator(B,'SCHIZOPHRENIA_SEIZURES') <= ben_hcc(B,CC) & ben_hcc(B,CC2) & schizophrenia_seizures(CC,CC2) 
  indicator(B,'SEPSIS_ARTIF_OPENINGS') <= ben_hcc(B,CC) & ben_hcc(B,CC2) & sepsis_artif_openings(CC,CC2) 
  indicator(B,'SEPSIS_ASP_SPEC_BACT_PNEUM') <=  ben_hcc(B,CC) & ben_hcc(B,CC2) & sepsis_asp_spec_bact_pneum(CC,CC2)
  indicator(B,'SEPSIS_CARD_RESP_FAIL') <=  ben_hcc(B,CC) & ben_hcc(B,CC2) & sepsis_card_resp_fail(CC,CC2)
 
  # the following 3 lines are plain python 
  cvars = community_regression()
  ivars = institutional_regression()
  nevars = new_enrollee_regression()
  allvars = list(set().union(cvars,ivars,nevars))

  (valid_community_variables[B] == concat_(CC,key=CC,sep=',')) <= indicator(B,CC) & CC.in_(cvars)
  (valid_institutional_variables[B] == concat_(CC,key=CC,sep=',')) <= indicator(B,CC) & CC.in_(ivars)
  (valid_new_enrollee_variables[B] == concat_(CC,key=CC,sep=',')) <= indicator(B,CC) & CC.in_(nevars)

  (new_enrollee_score[B] == sum_(Coef,key=Coef)) <=  indicator(B,CC) \
                                                & CC.in_(nevars) & coefficient("NE_"+CC,Coef)
  (institutional_score[B] == sum_(Coef,key=Coef)) <=  indicator(B,CC) \
                                                & CC.in_(ivars) & coefficient("INS_"+CC,Coef)
  (community_score[B] == sum_(Coef,key=Coef)) <=  indicator(B,CC) \
                                                & CC.in_(cvars) & coefficient("CE_"+CC,Coef)

  score(B,"community",Score) <= (community_score[B] == Score)
  score(B,"institutional",Score) <= (institutional_score[B] == Score)
  score(B,"new_enrollee",Score) <= (new_enrollee_score[B] == Score)
  output(B,Col,Val) <= score(B,Col,Val)
  output(B,Col,0) <=   Col.in_(allvars) & ~(indicator(B,Col))
  output(B,Col,1) <= indicator(B,Col)
  output(B,"sex",Val) <= (Ben.sex[B]==Val)
  

load_facts()
load_rules()


####################################################
jane = Beneficiary(2,"female","19740824",EntitlementReason.DIB,True)
jane.add_diagnosis(Diagnosis(jane,"D66",ICDType.TEN))  
jane.add_diagnosis(Diagnosis(jane,"C182",ICDType.TEN))  

daniel = Beneficiary(1,"male","19740824",EntitlementReason.DIB)
daniel.add_diagnosis(Diagnosis(daniel,"A0223",ICDType.TEN))  # 51
daniel.add_diagnosis(Diagnosis(daniel,"A0224",ICDType.TEN))  # 52
daniel.add_diagnosis(Diagnosis(daniel,"D66",ICDType.TEN))  
daniel.add_diagnosis(Diagnosis(daniel,"C163",ICDType.TEN))  
daniel.add_diagnosis(Diagnosis(daniel,"C163",ICDType.TEN))  
daniel.add_diagnosis(Diagnosis(daniel,"C182",ICDType.TEN))  
daniel.add_diagnosis(Diagnosis(daniel,"C800",ICDType.TEN))  
daniel.add_diagnosis(Diagnosis(daniel,"A072",ICDType.TEN))  

bob = Beneficiary(3,"male","20040824",EntitlementReason.DIB,True)
bob.add_diagnosis(Diagnosis(bob,"A0223",ICDType.TEN))
bob.add_diagnosis(Diagnosis(bob,"A0224",ICDType.TEN))

jacob = Beneficiary(4,"male","1940824",EntitlementReason.DIB,True)

antonio = Beneficiary(3,"male","20040824",EntitlementReason.DIB,True)
antonio.add_diagnosis(Diagnosis(antonio,"A0223",ICDType.TEN))
antonio.add_diagnosis(Diagnosis(antonio,"49320",ICDType.NINE))

john = Beneficiary(5,"male","19920824",EntitlementReason.DIB,True)
john.add_diagnosis(Diagnosis(john,"A0223",ICDType.TEN))
john.add_diagnosis(Diagnosis(john,"49320",ICDType.NINE))

####################################################
