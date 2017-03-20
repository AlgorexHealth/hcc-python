from enum import Enum,IntEnum
from functools import reduce
from datetime import datetime
from pyDatalog import pyDatalog

@pyDatalog.predicate()
def p2(X,Y):
    yield (1,2)
    yield (2,3)
    yield ("daniel",3)

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
    self.hccs = [] 

  def __repr__(self): # specifies how to display an Employee
    return str(self.hicno)

  def add_diagnosis(self,diag):
    self.diagnoses.append(diag)

  def calc_hccs(self):
    pre_calc = {
        '100': (lambda b: ben_hcc(b,'100') ),
        '103': (lambda b: ben_hcc(b,'103') ),
        '104': (lambda b: ben_hcc(b,'104') ),
        '106': (lambda b: ben_hcc(b,'106') ),
        '107': (lambda b: ben_hcc(b,'107') ),
        '108': (lambda b: ben_hcc(b,'108') ),
        '10': (lambda b: ben_hcc(b,'10') ),
        '110': (lambda b: ben_hcc(b,'110') ),
        '111': (lambda b: ben_hcc(b,'111') ),
        '112': (lambda b: ben_hcc(b,'112') ),
        '114': (lambda b: ben_hcc(b,'114') ),
        '115': (lambda b: ben_hcc(b,'115') ),
        '11': (lambda b: ben_hcc(b,'11') ),
        '122': (lambda b: ben_hcc(b,'122') ),
        '124': (lambda b: ben_hcc(b,'124') ),
        '12': (lambda b: ben_hcc(b,'12') ),
        '134': (lambda b: ben_hcc(b,'134') ),
        '135': (lambda b: ben_hcc(b,'135') ),
        '136': (lambda b: ben_hcc(b,'136') ),
        '137': (lambda b: ben_hcc(b,'137') ),
        '138': (lambda b: ben_hcc(b,'138') ),
        '139': (lambda b: ben_hcc(b,'139') ),
        '140': (lambda b: ben_hcc(b,'140') ),
        '141': (lambda b: ben_hcc(b,'141') ),
        '157': (lambda b: ben_hcc(b,'157') ),
        '158': (lambda b: ben_hcc(b,'158') ),
        '159': (lambda b: ben_hcc(b,'159') ),
        '160': (lambda b: ben_hcc(b,'160') ),
        '161': (lambda b: ben_hcc(b,'161') ),
        '162': (lambda b: ben_hcc(b,'162') ),
        '166': (lambda b: ben_hcc(b,'166') ),
        '167': (lambda b: ben_hcc(b,'167') ),
        '169': (lambda b: ben_hcc(b,'169') ),
        '170': (lambda b: ben_hcc(b,'170') ),
        '173': (lambda b: ben_hcc(b,'173') ),
        '176': (lambda b: ben_hcc(b,'176') ),
        '17': (lambda b: ben_hcc(b,'17') ),
        '186': (lambda b: ben_hcc(b,'186') ),
        '188': (lambda b: ben_hcc(b,'188') ),
        '189': (lambda b: ben_hcc(b,'189') ),
        '18': (lambda b: ben_hcc(b,'18') ),
        '19': (lambda b: ben_hcc(b,'19') ),
        '1': (lambda b: ben_hcc(b,'1') ),
        '21': (lambda b: ben_hcc(b,'21') ),
        '22': (lambda b: ben_hcc(b,'22') ),
        '23': (lambda b: ben_hcc(b,'23') ),
        '27': (lambda b: ben_hcc(b,'27') ),
        '28': (lambda b: ben_hcc(b,'28') ),
        '29': (lambda b: ben_hcc(b,'29') ),
        '2': (lambda b: ben_hcc(b,'2') ),
        '33': (lambda b: ben_hcc(b,'33') ),
        '34': (lambda b: ben_hcc(b,'34') ),
        '35': (lambda b: ben_hcc(b,'35') ),
        '39': (lambda b: ben_hcc(b,'39') ),
        '40': (lambda b: ben_hcc(b,'40') ),
        '46': (lambda b: ben_hcc(b,'46') ),
        '47': (lambda b: ben_hcc(b,'47') ),
        '48': (lambda b: ben_hcc(b,'48') ),
        '51': (lambda b: ben_hcc(b,'51') ),
        '52': (lambda b: ben_hcc(b,'52') ),
        '54': (lambda b: ben_hcc(b,'54') ),
        '55': (lambda b: ben_hcc(b,'55') ),
        '57': (lambda b: ben_hcc(b,'57') ),
        '58': (lambda b: ben_hcc(b,'58') ),
        '6': (lambda b: ben_hcc(b,'6') ),
        '70': (lambda b: ben_hcc(b,'70') ),
        '71': (lambda b: ben_hcc(b,'71') ),
        '72': (lambda b: ben_hcc(b,'72') ),
        '73': (lambda b: ben_hcc(b,'73') ),
        '74': (lambda b: ben_hcc(b,'74') ),
        '75': (lambda b: ben_hcc(b,'75') ),
        '76': (lambda b: ben_hcc(b,'76') ),
        '77': (lambda b: ben_hcc(b,'77') ),
        '78': (lambda b: ben_hcc(b,'78') ),
        '79': (lambda b: ben_hcc(b,'79') ),
        '80': (lambda b: ben_hcc(b,'80') ),
        '82': (lambda b: ben_hcc(b,'82') ),
        '83': (lambda b: ben_hcc(b,'83') ),
        '84': (lambda b: ben_hcc(b,'84') ),
        '85': (lambda b: ben_hcc(b,'85') ),
        '86': (lambda b: ben_hcc(b,'86') ),
        '87': (lambda b: ben_hcc(b,'87') ),
        '88': (lambda b: ben_hcc(b,'88') ),
        '8': (lambda b: ben_hcc(b,'8') ),
        '96': (lambda b: ben_hcc(b,'96') ),
        '99': (lambda b: ben_hcc(b,'99') ),
        '9': (lambda b: ben_hcc(b,'9') )
         }
    for (k,v) in pre_calc.items():
      if (len(v(self)) > 0):
        self.hccs += [k]
 

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
pyDatalog.create_terms('sepsis_pressure_ulcer, sepsis_artif_openings, art_openings_pressure_ulcer, diabetes_chf, copd_asp_spec_bact_pneum, asp_spec_bact_pneum_pres_ulc, sepsis_asp_spec_bact_pneum, schizophrenia_copd, schizophrenia_chf, schizophrenia_seizures,sex_age_range,U,L,disabled,originally_disabled,ben_hcc ')

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

  #    %* disabled;
  #    DISABL = (&AGEF < 65 & &OREC ne "0");
  disabled(B) <= (Ben.age[B] < 65) & ~(old_age_entitled(B))
  #    %* originally disabled: CHANGED FIRST TIME FOR THIS SOFTWARE;
  #    ORIGDS  = (&OREC = '1')*(DISABL = 0);
  originally_disabled(B) <= (Ben.original_reason_entitlement[B] == EntitlementReason.DIB) & ~(disabled(b))

  beneficiary_has_cc(B,CC) <= (Diag.beneficiary[D] == B)  & edit(Diag.icdcode[D],Diag.codetype[D],B,CC)
  beneficiary_has_cc(B,CC) <= (Diag.beneficiary[D] == B)  & cc(Diag.icdcode[D],CC,
                                        Diag.codetype[D]) & ~(edit(Diag.icdcode[D],Diag.codetype[D],B,CC2))
  has_cc_that_overrides_this_one(B,CC) <=  beneficiary_has_cc(B,OT)  & overrides(OT,CC)
  beneficiary_has_hcc(B,CC) <= beneficiary_has_cc(B,CC) & ~( has_cc_that_overrides_this_one(B,CC))
  ben_hcc(B,CC) <= beneficiary_has_hcc(B,CC)
  ben_hcc(B,CC) <= CC.in_(Ben.hccs[B])

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

#   def load_all_indicators():
#     indicators = {
#      'ART_OPENINGS_PRESSURE_ULCER': (lambda b: ben_hcc(b,CC) & ben_hcc(b,CC2) & art_openings_pressure_ulcer(CC,CC2)),
#      'ASP_SPEC_BACT_PNEUM_PRES_ULC': (lambda b: ben_hcc(b,CC) & ben_hcc(b,CC2) & asp_spec_bact_pneum_pres_ulc(CC,CC2)),
#      'CANCER_IMMUNE': (lambda b: ben_hcc(b,CC) & ben_hcc(b,CC2) & cancer_immune(CC,CC2)),
#      'CHF_COPD': (lambda b: ben_hcc(b,CC) & ben_hcc(b,CC2) & chf_copd(CC,CC2)),
#      'CHF_RENAL': (lambda b: ben_hcc(b,CC) & ben_hcc(b,CC2) & chf_renal(CC,CC2)),
#      'COPD_ASP_SPEC_BACT_PNEUM': (lambda b: ben_hcc(b,CC) & ben_hcc(b,CC2) & copd_asp_spec_bact_pneum(CC,CC2)),
#      'COPD_CARD_RESP_FAIL': (lambda b: ben_hcc(b,CC) & ben_hcc(b,CC2) & copd_card_resp_fail(CC,CC2)),
#      'DIABETES_CHF': (lambda b: ben_hcc(b,CC) & ben_hcc(b,CC2) & diabetes_chf(CC,CC2)),
#      'DISABLED_HCC110': (lambda b: ben_hcc(b,'110') & disabled(b)),
#      'DISABLED_HCC161': (lambda b: ben_hcc(b,'161') & disabled(b)),
#      'DISABLED_HCC176': (lambda b: ben_hcc(b,'176') & disabled(b)),
#      'DISABLED_HCC34': (lambda b: ben_hcc(b,'34') & disabled(b)),
#      'DISABLED_HCC39': (lambda b: ben_hcc(b,'39') & disabled(b)),
#      'DISABLED_HCC46': (lambda b: ben_hcc(b,'46') & disabled(b)),
#      'DISABLED_HCC54': (lambda b: ben_hcc(b,'54') & disabled(b)),
#      'DISABLED_HCC55': (lambda b: ben_hcc(b,'55') & disabled(b)),
#      'DISABLED_HCC6': (lambda b: ben_hcc(b,'6') & disabled(b)),
#      'DISABLED_HCC77': (lambda b: ben_hcc(b,'77') & disabled(b)),
#      'DISABLED_HCC85': (lambda b: ben_hcc(b,'85') & disabled(b)),
#      # 'DISABLED_PRESSURE_ULCER': (lambda b: []),
#      # 'F0_34': (lambda b: []),
#      # 'F35_44': (lambda b: []),
#      # 'F45_54': (lambda b: []),
#      # 'F55_59': (lambda b: []),
#      # 'F60_64': (lambda b: []),
#      # 'F65_69': (lambda b: []),
#      # 'F70_74': (lambda b: []),
#      # 'F75_79': (lambda b: []),
#      # 'F80_84': (lambda b: []),
#      # 'F85_89': (lambda b: []),
#      # 'F90_94': (lambda b: []),
#      # 'F95_GT': (lambda b: []),
#      'HCC100': (lambda b: ben_hcc(b,'100') ),
#      'HCC103': (lambda b: ben_hcc(b,'103') ),
#      'HCC104': (lambda b: ben_hcc(b,'104') ),
#      'HCC106': (lambda b: ben_hcc(b,'106') ),
#      'HCC107': (lambda b: ben_hcc(b,'107') ),
#      'HCC108': (lambda b: ben_hcc(b,'108') ),
#      'HCC10': (lambda b: ben_hcc(b,'10') ),
#      'HCC110': (lambda b: ben_hcc(b,'110') ),
#      'HCC111': (lambda b: ben_hcc(b,'111') ),
#      'HCC112': (lambda b: ben_hcc(b,'112') ),
#      'HCC114': (lambda b: ben_hcc(b,'114') ),
#      'HCC115': (lambda b: ben_hcc(b,'115') ),
#      'HCC11': (lambda b: ben_hcc(b,'11') ),
#      'HCC122': (lambda b: ben_hcc(b,'122') ),
#      'HCC124': (lambda b: ben_hcc(b,'124') ),
#      'HCC12': (lambda b: ben_hcc(b,'12') ),
#      'HCC134': (lambda b: ben_hcc(b,'134') ),
#      'HCC135': (lambda b: ben_hcc(b,'135') ),
#      'HCC136': (lambda b: ben_hcc(b,'136') ),
#      'HCC137': (lambda b: ben_hcc(b,'137') ),
#      'HCC138': (lambda b: ben_hcc(b,'138') ),
#      'HCC139': (lambda b: ben_hcc(b,'139') ),
#      'HCC140': (lambda b: ben_hcc(b,'140') ),
#      'HCC141': (lambda b: ben_hcc(b,'141') ),
#      'HCC157': (lambda b: ben_hcc(b,'157') ),
#      'HCC158': (lambda b: ben_hcc(b,'158') ),
#      'HCC159': (lambda b: ben_hcc(b,'159') ),
#      'HCC160': (lambda b: ben_hcc(b,'160') ),
#      'HCC161': (lambda b: ben_hcc(b,'161') ),
#      'HCC162': (lambda b: ben_hcc(b,'162') ),
#      'HCC166': (lambda b: ben_hcc(b,'166') ),
#      'HCC167': (lambda b: ben_hcc(b,'167') ),
#      'HCC169': (lambda b: ben_hcc(b,'169') ),
#      'HCC170': (lambda b: ben_hcc(b,'170') ),
#      'HCC173': (lambda b: ben_hcc(b,'173') ),
#      'HCC176': (lambda b: ben_hcc(b,'176') ),
#      'HCC17': (lambda b: ben_hcc(b,'17') ),
#      'HCC186': (lambda b: ben_hcc(b,'186') ),
#      'HCC188': (lambda b: ben_hcc(b,'188') ),
#      'HCC189': (lambda b: ben_hcc(b,'189') ),
#      'HCC18': (lambda b: ben_hcc(b,'18') ),
#      'HCC19': (lambda b: ben_hcc(b,'19') ),
#      'HCC1': (lambda b: ben_hcc(b,'1') ),
#      'HCC21': (lambda b: ben_hcc(b,'21') ),
#      'HCC22': (lambda b: ben_hcc(b,'22') ),
#      'HCC23': (lambda b: ben_hcc(b,'23') ),
#      'HCC27': (lambda b: ben_hcc(b,'27') ),
#      'HCC28': (lambda b: ben_hcc(b,'28') ),
#      'HCC29': (lambda b: ben_hcc(b,'29') ),
#      'HCC2': (lambda b: ben_hcc(b,'2') ),
#      'HCC33': (lambda b: ben_hcc(b,'33') ),
#      'HCC34': (lambda b: ben_hcc(b,'34') ),
#      'HCC35': (lambda b: ben_hcc(b,'35') ),
#      'HCC39': (lambda b: ben_hcc(b,'39') ),
#      'HCC40': (lambda b: ben_hcc(b,'40') ),
#      'HCC46': (lambda b: ben_hcc(b,'46') ),
#      'HCC47': (lambda b: ben_hcc(b,'47') ),
#      'HCC48': (lambda b: ben_hcc(b,'48') ),
#      'HCC51': (lambda b: ben_hcc(b,'51') ),
#      'HCC52': (lambda b: ben_hcc(b,'52') ),
#      'HCC54': (lambda b: ben_hcc(b,'54') ),
#      'HCC55': (lambda b: ben_hcc(b,'55') ),
#      'HCC57': (lambda b: ben_hcc(b,'57') ),
#      'HCC58': (lambda b: ben_hcc(b,'58') ),
#      'HCC6': (lambda b: ben_hcc(b,'6') ),
#      'HCC70': (lambda b: ben_hcc(b,'70') ),
#      'HCC71': (lambda b: ben_hcc(b,'71') ),
#      'HCC72': (lambda b: ben_hcc(b,'72') ),
#      'HCC73': (lambda b: ben_hcc(b,'73') ),
#      'HCC74': (lambda b: ben_hcc(b,'74') ),
#      'HCC75': (lambda b: ben_hcc(b,'75') ),
#      'HCC76': (lambda b: ben_hcc(b,'76') ),
#      'HCC77': (lambda b: ben_hcc(b,'77') ),
#      'HCC78': (lambda b: ben_hcc(b,'78') ),
#      'HCC79': (lambda b: ben_hcc(b,'79') ),
#      'HCC80': (lambda b: ben_hcc(b,'80') ),
#      'HCC82': (lambda b: ben_hcc(b,'82') ),
#      'HCC83': (lambda b: ben_hcc(b,'83') ),
#      'HCC84': (lambda b: ben_hcc(b,'84') ),
#      'HCC85': (lambda b: ben_hcc(b,'85') ),
#      'HCC86': (lambda b: ben_hcc(b,'86') ),
#      'HCC87': (lambda b: ben_hcc(b,'87') ),
#      'HCC88': (lambda b: ben_hcc(b,'88') ),
#      'HCC8': (lambda b: ben_hcc(b,'8') ),
#      'HCC96': (lambda b: ben_hcc(b,'96') ),
#      'HCC99': (lambda b: ben_hcc(b,'99') ),
#      'HCC9': (lambda b: ben_hcc(b,'9') ),
#      # 'M0_34': (lambda b: []),
#      # 'M35_44': (lambda b: []),
#      # 'M45_54': (lambda b: []),
#      # 'M55_59': (lambda b: []),
#      # 'M60_64': (lambda b: []),
#      # 'M65_69': (lambda b: []),
#      # 'M70_74': (lambda b: []),
#      # 'M75_79': (lambda b: []),
#      # 'M80_84': (lambda b: []),
#      # 'M85_89': (lambda b: []),
#      # 'M90_94': (lambda b: []),
#      # 'M95_GT': (lambda b: []),
#      # 'MCAID_FEMALE0_64': (lambda b: []),
#      # 'MCAID_FEMALE65': (lambda b: []),
#      # 'MCAID_FEMALE66_69': (lambda b: []),
#      # 'MCAID_FEMALE70_74': (lambda b: []),
#      # 'MCAID_FEMALE75_GT': (lambda b: []),
#      # 'MCAID_Female_Aged': (lambda b: []),
#      # 'MCAID_Female_Disabled': (lambda b: []),
#      # 'MCAID': (lambda b: []),
#      # 'MCAID_MALE0_64': (lambda b: []),
#      # 'MCAID_MALE65': (lambda b: []),
#      # 'MCAID_MALE66_69': (lambda b: []),
#      # 'MCAID_MALE70_74': (lambda b: []),
#      # 'MCAID_MALE75_GT': (lambda b: []),
#      # 'MCAID_Male_Aged': (lambda b: []),
#      # 'MCAID_Male_Disabled': (lambda b: []),
#      # 'NEF0_34': (lambda b: []),
#      # 'NEF35_44': (lambda b: []),
#      # 'NEF45_54': (lambda b: []),
#      # 'NEF55_59': (lambda b: []),
#      # 'NEF60_64': (lambda b: []),
#      # 'NEF65': (lambda b: []),
#      # 'NEF66': (lambda b: []),
#      # 'NEF67': (lambda b: []),
#      # 'NEF68': (lambda b: []),
#      # 'NEF69': (lambda b: []),
#      # 'NEF70_74': (lambda b: []),
#      # 'NEF75_79': (lambda b: []),
#      # 'NEF80_84': (lambda b: []),
#      # 'NEF85_89': (lambda b: []),
#      # 'NEF90_94': (lambda b: []),
#      # 'NEF95_GT': (lambda b: []),
#      # 'NEM0_34': (lambda b: []),
#      # 'NEM35_44': (lambda b: []),
#      # 'NEM45_54': (lambda b: []),
#      # 'NEM55_59': (lambda b: []),
#      # 'NEM60_64': (lambda b: []),
#      # 'NEM65': (lambda b: []),
#      # 'NEM66': (lambda b: []),
#      # 'NEM67': (lambda b: []),
#      # 'NEM68': (lambda b: []),
#      # 'NEM69': (lambda b: []),
#      # 'NEM70_74': (lambda b: []),
#      # 'NEM75_79': (lambda b: []),
#      # 'NEM80_84': (lambda b: []),
#      # 'NEM85_89': (lambda b: []),
#      # 'NEM90_94': (lambda b: []),
#      # 'NEM95_GT': (lambda b: []),
#      # 'Origdis_female65': (lambda b: []),
#      # 'Origdis_female66_69': (lambda b: []),
#      # 'Origdis_female70_74': (lambda b: []),
#      # 'Origdis_female75_GT': (lambda b: []),
#      # 'Origdis_male65': (lambda b: []),
#      # 'Origdis_male66_69': (lambda b: []),
#      # 'Origdis_male70_74': (lambda b: []),
#      # 'Origdis_male75_GT': (lambda b: []),
#      # 'ORIGDS': (lambda b: []),
#      # 'OriginallyDisabled_Female': (lambda b: []),
#      # 'OriginallyDisabled_Male': (lambda b: []),
#      # 'SCHIZOPHRENIA_CHF': (lambda b: []),
#      # 'SCHIZOPHRENIA_COPD': (lambda b: []),
#      # 'SCHIZOPHRENIA_SEIZURES': (lambda b: []),
#      # 'SEPSIS_ARTIF_OPENINGS': (lambda b: []),
#      # 'SEPSIS_ASP_SPEC_BACT_PNEUM': (lambda b: []),
#      # 'SEPSIS_CARD_RESP_FAIL': (lambda b: []),
#      # 'SEPSIS_PRESSURE_ULCER': (lambda b: [])
#     }
#     return indicators

def load_all_stringified_indicators():
  indicators = {
   'ART_OPENINGS_PRESSURE_ULCER': "rule(B,'ART_OPENINGS_PRESSURE_ULCER') <=  ben_hcc(B,CC) & ben_hcc(B,CC2) & art_openings_pressure_ulcer(CC,CC2)",
   'ASP_SPEC_BACT_PNEUM_PRES_ULC': "rule(B,'ASP_SPEC_BACT_PNEUM_PRES_ULC') <=  ben_hcc(B,CC) & ben_hcc(B,CC2) & asp_spec_bact_pneum_pres_ulc(CC,CC2)",
   'CANCER_IMMUNE': "rule(B,'CANCER_IMMUNE') <=  ben_hcc(B,CC) & ben_hcc(B,CC2) & cancer_immune(CC,CC2)",
   'CHF_COPD': "rule(B,'CHF_COPD') <=  ben_hcc(B,CC) & ben_hcc(B,CC2) & chf_copd(CC,CC2)",
   'CHF_RENAL': "rule(B,'CHF_RENAL') <=  ben_hcc(B,CC) & ben_hcc(B,CC2) & chf_renal(CC,CC2)",
   'COPD_ASP_SPEC_BACT_PNEUM': "rule(B,'COPD_ASP_SPEC_BACT_PNEUM') <=  ben_hcc(B,CC) & ben_hcc(B,CC2) & copd_asp_spec_bact_pneum(CC,CC2)",
   'COPD_CARD_RESP_FAIL': "rule(B,'COPD_CARD_RESP_FAIL') <=  ben_hcc(B,CC) & ben_hcc(B,CC2) & copd_card_resp_fail(CC,CC2)",
   'DIABETES_CHF': "rule(B,'DIABETES_CHF') <=  ben_hcc(B,CC) & ben_hcc(B,CC2) & diabetes_chf(CC,CC2)",
   'DISABLED_HCC110': "rule(B,'DISABLED_HCC110') <=  ben_hcc(B,'110') & disabled(B)",
   'DISABLED_HCC161': "rule(B,'DISABLED_HCC161') <=  ben_hcc(B,'161') & disabled(B)",
   'DISABLED_HCC176': "rule(B,'DISABLED_HCC176') <=  ben_hcc(B,'176') & disabled(B)",
   'DISABLED_HCC34': "rule(B,'DISABLED_HCC34') <=  ben_hcc(B,'34') & disabled(B)",
   'DISABLED_HCC39': "rule(B,'DISABLED_HCC39') <=  ben_hcc(B,'39') & disabled(B)",
   'DISABLED_HCC46': "rule(B,'DISABLED_HCC46') <=  ben_hcc(B,'46') & disabled(B)",
   'DISABLED_HCC54': "rule(B,'DISABLED_HCC54') <=  ben_hcc(B,'54') & disabled(B)",
   'DISABLED_HCC55': "rule(B,'DISABLED_HCC55') <=  ben_hcc(B,'55') & disabled(B)",
   'DISABLED_HCC6': "rule(B,'DISABLED_HCC6') <=  ben_hcc(B,'6') & disabled(B)",
   'DISABLED_HCC77': "rule(B,'DISABLED_HCC77') <=  ben_hcc(B,'77') & disabled(B)",
   'DISABLED_HCC85': "rule(B,'DISABLED_HCC85') <=  ben_hcc(B,'85') & disabled(B)",
   'DISABLED_PRESSURE_ULCER': "rule(B,'DISABLED_HCC85') <=  ben_hcc(B,CC) & dc(CC,'pressure_ulcer') & disabled(B)",
   'F0_34': "rule(B,'F0_34') <=  sex_age_range('female',B,0,34)",
   'F35_44': "rule(B,'F35_44') <=  sex_age_range('female',B,35,44)",
   'F45_54': "rule(B,'F45_54') <=  sex_age_range('female',B,45,54)",
   'F55_59': "rule(B,'F55_59') <=  sex_age_range('female',B,55,59)",
   'F60_64': "rule(B,'F60_64') <=  sex_age_range('female',B,60,64)",
   'F65_69': "rule(B,'F65_69') <=  sex_age_range('female',B,65,69)",
   'F70_74': "rule(B,'F70_74') <=  sex_age_range('female',B,70,74)",
   'F75_79': "rule(B,'F75_79') <=  sex_age_range('female',B,75,79)",
   'F80_84': "rule(B,'F80_84') <=  sex_age_range('female',B,80,84)",
   'F85_89': "rule(B,'F85_89') <=  sex_age_range('female',B,85,89)",
   'F90_94': "rule(B,'F90_94') <=  sex_age_range('female',B,90,94)",
   'F95_GT': "rule(B,'F95_GT') <=  sex_age_range('female',B,95,99999)",
   'HCC100': "rule(B,'HCC100') <=  ben_hcc(B,'100') ",
   'HCC103': "rule(B,'HCC103') <=  ben_hcc(B,'103') ",
   'HCC104': "rule(B,'HCC104') <=  ben_hcc(B,'104') ",
   'HCC106': "rule(B,'HCC106') <=  ben_hcc(B,'106') ",
   'HCC107': "rule(B,'HCC107') <=  ben_hcc(B,'107') ",
   'HCC108': "rule(B,'HCC108') <=  ben_hcc(B,'108') ",
   'HCC10': "rule(B,'HCC10') <=  ben_hcc(B,'10') ",
   'HCC110': "rule(B,'HCC110') <=  ben_hcc(B,'110') ",
   'HCC111': "rule(B,'HCC111') <=  ben_hcc(B,'111') ",
   'HCC112': "rule(B,'HCC112') <=  ben_hcc(B,'112') ",
   'HCC114': "rule(B,'HCC114') <=  ben_hcc(B,'114') ",
   'HCC115': "rule(B,'HCC115') <=  ben_hcc(B,'115') ",
   'HCC11': "rule(B,'HCC11') <=  ben_hcc(B,'11') ",
   'HCC122': "rule(B,'HCC122') <=  ben_hcc(B,'122') ",
   'HCC124': "rule(B,'HCC124') <=  ben_hcc(B,'124') ",
   'HCC12': "rule(B,'HCC12') <=  ben_hcc(B,'12') ",
   'HCC134': "rule(B,'HCC134') <=  ben_hcc(B,'134') ",
   'HCC135': "rule(B,'HCC135') <=  ben_hcc(B,'135') ",
   'HCC136': "rule(B,'HCC136') <=  ben_hcc(B,'136') ",
   'HCC137': "rule(B,'HCC137') <=  ben_hcc(B,'137') ",
   'HCC138': "rule(B,'HCC138') <=  ben_hcc(B,'138') ",
   'HCC139': "rule(B,'HCC139') <=  ben_hcc(B,'139') ",
   'HCC140': "rule(B,'HCC140') <=  ben_hcc(B,'140') ",
   'HCC141': "rule(B,'HCC141') <=  ben_hcc(B,'141') ",
   'HCC157': "rule(B,'HCC157') <=  ben_hcc(B,'157') ",
   'HCC158': "rule(B,'HCC158') <=  ben_hcc(B,'158') ",
   'HCC159': "rule(B,'HCC159') <=  ben_hcc(B,'159') ",
   'HCC160': "rule(B,'HCC160') <=  ben_hcc(B,'160') ",
   'HCC161': "rule(B,'HCC161') <=  ben_hcc(B,'161') ",
   'HCC162': "rule(B,'HCC162') <=  ben_hcc(B,'162') ",
   'HCC166': "rule(B,'HCC166') <=  ben_hcc(B,'166') ",
   'HCC167': "rule(B,'HCC167') <=  ben_hcc(B,'167') ",
   'HCC169': "rule(B,'HCC169') <=  ben_hcc(B,'169') ",
   'HCC170': "rule(B,'HCC170') <=  ben_hcc(B,'170') ",
   'HCC173': "rule(B,'HCC173') <=  ben_hcc(B,'173') ",
   'HCC176': "rule(B,'HCC176') <=  ben_hcc(B,'176') ",
   'HCC17': "rule(B,'HCC17') <=  ben_hcc(B,'17') ",
   'HCC186': "rule(B,'HCC186') <=  ben_hcc(B,'186') ",
   'HCC188': "rule(B,'HCC188') <=  ben_hcc(B,'188') ",
   'HCC189': "rule(B,'HCC189') <=  ben_hcc(B,'189') ",
   'HCC18': "rule(B,'HCC18') <=  ben_hcc(B,'18') ",
   'HCC19': "rule(B,'HCC19') <=  ben_hcc(B,'19') ",
   'HCC1': "rule(B,'HCC1') <=  ben_hcc(B,'1') ",
   'HCC21': "rule(B,'HCC21') <=  ben_hcc(B,'21') ",
   'HCC22': "rule(B,'HCC22') <=  ben_hcc(B,'22') ",
   'HCC23': "rule(B,'HCC23') <=  ben_hcc(B,'23') ",
   'HCC27': "rule(B,'HCC27') <=  ben_hcc(B,'27') ",
   'HCC28': "rule(B,'HCC28') <=  ben_hcc(B,'28') ",
   'HCC29': "rule(B,'HCC29') <=  ben_hcc(B,'29') ",
   'HCC2': "rule(B,'HCC2') <=  ben_hcc(B,'2') ",
   'HCC33': "rule(B,'HCC33') <=  ben_hcc(B,'33') ",
   'HCC34': "rule(B,'HCC34') <=  ben_hcc(B,'34') ",
   'HCC35': "rule(B,'HCC35') <=  ben_hcc(B,'35') ",
   'HCC39': "rule(B,'HCC39') <=  ben_hcc(B,'39') ",
   'HCC40': "rule(B,'HCC40') <=  ben_hcc(B,'40') ",
   'HCC46': "rule(B,'HCC46') <=  ben_hcc(B,'46') ",
   'HCC47': "rule(B,'HCC47') <=  ben_hcc(B,'47') ",
   'HCC48': "rule(B,'HCC48') <=  ben_hcc(B,'48') ",
   'HCC51': "rule(B,'HCC51') <=  ben_hcc(B,'51') ",
   'HCC52': "rule(B,'HCC52') <=  ben_hcc(B,'52') ",
   'HCC54': "rule(B,'HCC54') <=  ben_hcc(B,'54') ",
   'HCC55': "rule(B,'HCC55') <=  ben_hcc(B,'55') ",
   'HCC57': "rule(B,'HCC57') <=  ben_hcc(B,'57') ",
   'HCC58': "rule(B,'HCC58') <=  ben_hcc(B,'58') ",
   'HCC6': "rule(B,'HCC6') <=  ben_hcc(B,'6') ",
   'HCC70': "rule(B,'HCC70') <=  ben_hcc(B,'70') ",
   'HCC71': "rule(B,'HCC71') <=  ben_hcc(B,'71') ",
   'HCC72': "rule(B,'HCC72') <=  ben_hcc(B,'72') ",
   'HCC73': "rule(B,'HCC73') <=  ben_hcc(B,'73') ",
   'HCC74': "rule(B,'HCC74') <=  ben_hcc(B,'74') ",
   'HCC75': "rule(B,'HCC75') <=  ben_hcc(B,'75') ",
   'HCC76': "rule(B,'HCC76') <=  ben_hcc(B,'76') ",
   'HCC77': "rule(B,'HCC77') <=  ben_hcc(B,'77') ",
   'HCC78': "rule(B,'HCC78') <=  ben_hcc(B,'78') ",
   'HCC79': "rule(B,'HCC79') <=  ben_hcc(B,'79') ",
   'HCC80': "rule(B,'HCC80') <=  ben_hcc(B,'80') ",
   'HCC82': "rule(B,'HCC82') <=  ben_hcc(B,'82') ",
   'HCC83': "rule(B,'HCC83') <=  ben_hcc(B,'83') ",
   'HCC84': "rule(B,'HCC84') <=  ben_hcc(B,'84') ",
   'HCC85': "rule(B,'HCC85') <=  ben_hcc(B,'85') ",
   'HCC86': "rule(B,'HCC86') <=  ben_hcc(B,'86') ",
   'HCC87': "rule(B,'HCC87') <=  ben_hcc(B,'87') ",
   'HCC88': "rule(B,'HCC88') <=  ben_hcc(B,'88') ",
   'HCC8': "rule(B,'HCC8') <=  ben_hcc(B,'8') ",
   'HCC96': "rule(B,'HCC96') <=  ben_hcc(B,'96') ",
   'HCC99': "rule(B,'HCC99') <=  ben_hcc(B,'99') ",
   'HCC9': "rule(B,'HCC9') <=  ben_hcc(B,'9') ",
   'M0_34': "rule(B,'M0_34') <=  sex_age_range('male',B,0,34)",
   'M35_44': "rule(B,'M35_44') <=  sex_age_range('male',B,35,44)",
   'M45_54': "rule(B,'M45_54') <=  sex_age_range('male',B,45,54)",
   'M55_59': "rule(B,'M55_59') <=  sex_age_range('male',B,55,59)",
   'M60_64': "rule(B,'M60_64') <=  sex_age_range('male',B,60,64)",
   'M65_69': "rule(B,'M65_69') <=  sex_age_range('male',B,65,69)",
   'M70_74': "rule(B,'M70_74') <=  sex_age_range('male',B,70,74)",
   'M75_79': "rule(B,'M75_79') <=  sex_age_range('male',B,75,79)",
   'M80_84': "rule(B,'M80_84') <=  sex_age_range('male',B,80,84)",
   'M85_89': "rule(B,'M85_89') <=  sex_age_range('male',B,85,89)",
   'M90_94': "rule(B,'M90_94') <=  sex_age_range('male',B,90,94)",
   'M95_GT': "rule(B,'M95_GT') <=  sex_age_range('male',B,95,99999)",
   # 'MCAID_FEMALE0_64': "rule(B,'MCAID_FEMALE0_64') <=  []",
   # 'MCAID_FEMALE65': "rule(B,'MCAID_FEMALE65') <=  []",
   # 'MCAID_FEMALE66_69': "rule(B,'MCAID_FEMALE66_69') <=  []",
   # 'MCAID_FEMALE70_74': "rule(B,'MCAID_FEMALE70_74') <=  []",
   # 'MCAID_FEMALE75_GT': "rule(B,'MCAID_FEMALE75_GT') <=  []",
   # 'MCAID_Female_Aged': "rule(B,'MCAID_Female_Aged') <=  []",
   # 'MCAID_Female_Disabled': "rule(B,'MCAID_Female_Disabled') <=  []",
   # 'MCAID': "rule(B,'MCAID') <=  []",
   # 'MCAID_MALE0_64': "rule(B,'MCAID_MALE0_64') <=  []",
   # 'MCAID_MALE65': "rule(B,'MCAID_MALE65') <=  []",
   # 'MCAID_MALE66_69': "rule(B,'MCAID_MALE66_69') <=  []",
   # 'MCAID_MALE70_74': "rule(B,'MCAID_MALE70_74') <=  []",
   # 'MCAID_MALE75_GT': "rule(B,'MCAID_MALE75_GT') <=  []",
   # 'MCAID_Male_Aged': "rule(B,'MCAID_Male_Aged') <=  []",
   # 'MCAID_Male_Disabled': "rule(B,'MCAID_Male_Disabled') <=  []",
   # 'NEF0_34': "rule(B,'NEF0_34') <=  []",
   # 'NEF35_44': "rule(B,'NEF35_44') <=  []",
   # 'NEF45_54': "rule(B,'NEF45_54') <=  []",
   # 'NEF55_59': "rule(B,'NEF55_59') <=  []",
   # 'NEF60_64': "rule(B,'NEF60_64') <=  []",
   # 'NEF65': "rule(B,'NEF65') <=  []",
   # 'NEF66': "rule(B,'NEF66') <=  []",
   # 'NEF67': "rule(B,'NEF67') <=  []",
   # 'NEF68': "rule(B,'NEF68') <=  []",
   # 'NEF69': "rule(B,'NEF69') <=  []",
   # 'NEF70_74': "rule(B,'NEF70_74') <=  []",
   # 'NEF75_79': "rule(B,'NEF75_79') <=  []",
   # 'NEF80_84': "rule(B,'NEF80_84') <=  []",
   # 'NEF85_89': "rule(B,'NEF85_89') <=  []",
   # 'NEF90_94': "rule(B,'NEF90_94') <=  []",
   # 'NEF95_GT': "rule(B,'NEF95_GT') <=  []",
   # 'NEM0_34': "rule(B,'NEM0_34') <=  []",
   # 'NEM35_44': "rule(B,'NEM35_44') <=  []",
   # 'NEM45_54': "rule(B,'NEM45_54') <=  []",
   # 'NEM55_59': "rule(B,'NEM55_59') <=  []",
   # 'NEM60_64': "rule(B,'NEM60_64') <=  []",
   # 'NEM65': "rule(B,'NEM65') <=  []",
   # 'NEM66': "rule(B,'NEM66') <=  []",
   # 'NEM67': "rule(B,'NEM67') <=  []",
   # 'NEM68': "rule(B,'NEM68') <=  []",
   # 'NEM69': "rule(B,'NEM69') <=  []",
   # 'NEM70_74': "rule(B,'NEM70_74') <=  []",
   # 'NEM75_79': "rule(B,'NEM75_79') <=  []",
   # 'NEM80_84': "rule(B,'NEM80_84') <=  []",
   # 'NEM85_89': "rule(B,'NEM85_89') <=  []",
   # 'NEM90_94': "rule(B,'NEM90_94') <=  []",
   # 'NEM95_GT': "rule(B,'NEM95_GT') <=  []",
   # 'Origdis_female65': "rule(B,'Origdis_female65') <=  []",
   # 'Origdis_female66_69': "rule(B,'Origdis_female66_69') <=  []",
   # 'Origdis_female70_74': "rule(B,'Origdis_female70_74') <=  []",
   # 'Origdis_female75_GT': "rule(B,'Origdis_female75_GT') <=  []",
   # 'Origdis_male65': "rule(B,'Origdis_male65') <=  []",
   # 'Origdis_male66_69': "rule(B,'Origdis_male66_69') <=  []",
   # 'Origdis_male70_74': "rule(B,'Origdis_male70_74') <=  []",
   # 'Origdis_male75_GT': "rule(B,'Origdis_male75_GT') <=  []",
   # 'ORIGDS': "rule(B,'ORIGDS') <=  []",
   # 'OriginallyDisabled_Female': "rule(B,'OriginallyDisabled_Female') <=  []",
   # 'OriginallyDisabled_Male': "rule(B,'OriginallyDisabled_Male') <=  []",
   # 'SCHIZOPHRENIA_CHF': "rule(B,'SCHIZOPHRENIA_CHF') <=  []",
   # 'SCHIZOPHRENIA_COPD': "rule(B,'SCHIZOPHRENIA_COPD') <=  []",
   # 'SCHIZOPHRENIA_SEIZURES': "rule(B,'SCHIZOPHRENIA_SEIZURES') <=  []",
   # 'SEPSIS_ARTIF_OPENINGS': "rule(B,'SEPSIS_ARTIF_OPENINGS') <=  []",
   # 'SEPSIS_ASP_SPEC_BACT_PNEUM': "rule(B,'SEPSIS_ASP_SPEC_BACT_PNEUM') <=  []",
   # 'SEPSIS_CARD_RESP_FAIL': "rule(B,'SEPSIS_CARD_RESP_FAIL') <=  []",
   # 'SEPSIS_PRESSURE_ULCER': " [])
  }
  return indicators

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

def run_on(b,dicto):
  res = []
  for (k,v) in dicto.items():
    if( len(v(b)) > 0):
      res += [k]
  return res

def time():
  start = datetime.now()
  daniel.calc_hccs()
  run_on(daniel,load_all_indicators())
  run_on(daniel,load_all_indicators())
  run_on(daniel,load_all_indicators())
  end =  datetime.now()
  print("time was:", (end - start).seconds)

def time2():
  start = datetime.now()
  run_on(daniel,load_all_indicators())
  run_on(bob,load_all_indicators())
  run_on(jane,load_all_indicators())
  end =  datetime.now()
  print("time was:", (end - start).seconds)

pyDatalog.create_terms('CC,B,valid_variables,rule')

(valid_variables[B] == concat_(CC,key=CC,sep=',')) <= rule(B,CC) & CC.in_(['HCC23', 'HCC137', 'COPD_CARD_RESP_FAIL', 'HCC77', 'HCC27', 'HCC73', 'HCC115', 'HCC111', 'HCC186', 'DISABLED_HCC110', 'HCC22', 'HCC87', 'HCC34', 'HCC96', 'HCC21', 'HCC55', 'HCC188', 'HCC48', 'HCC100', 'HCC12', 'F95_GT', 'HCC161', 'HCC52', 'HCC33', 'F65_69', 'HCC138', 'F70_74', 'HCC141', 'HCC82', 'HCC6', 'ART_OPENINGS_PRESSURE_ULCER', 'F0_34', 'HCC78', 'HCC169', 'HCC51', 'HCC122', 'CHF_COPD', 'HCC189', 'HCC8', 'HCC136', 'F45_54', 'F35_44', 'DISABLED_HCC176', 'HCC135', 'HCC106', 'HCC72', 'HCC74', 'HCC85', 'HCC110', 'HCC54', 'HCC47', 'HCC35', 'HCC170', 'HCC9', 'HCC99', 'HCC88', 'HCC157', 'HCC39', 'HCC176', 'DISABLED_HCC161', 'HCC108', 'CHF_RENAL', 'HCC104', 'HCC75', 'HCC29', 'HCC17', 'F60_64', 'HCC10', 'DISABLED_HCC34', 'DISABLED_HCC54', 'F85_89', 'HCC79', 'HCC71', 'COPD_ASP_SPEC_BACT_PNEUM', 'DISABLED_HCC55', 'DISABLED_HCC39', 'DISABLED_HCC85', 'HCC160', 'HCC103', 'HCC83', 'DISABLED_HCC77', 'HCC166', 'DIABETES_CHF', 'HCC46', 'HCC167', 'HCC158', 'CANCER_IMMUNE', 'HCC140', 'HCC76', 'HCC2', 'F75_79', 'HCC19', 'HCC159', 'HCC107', 'DISABLED_HCC46', 'HCC28', 'ASP_SPEC_BACT_PNEUM_PRES_ULC', 'HCC57', 'HCC139', 'HCC162', 'HCC40', 'HCC84', 'HCC173', 'HCC18', 'HCC124', 'HCC58', 'DISABLED_PRESSURE_ULCER', 'HCC134', 'HCC80', 'HCC86', 'HCC11', 'F90_94', 'DISABLED_HCC6', 'F80_84', 'HCC1', 'HCC114', 'F55_59', 'HCC70', 'HCC112'])

[pyDatalog.load(v) for (k,v) in load_all_stringified_indicators().items()]
