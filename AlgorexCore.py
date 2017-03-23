import random
from bokeh.palettes import Spectral11, small_palettes, plasma, BrBG, viridis, magma
# give me 100 patient ids
ids = range(1, 101)


pareto = [random.paretovariate(7) for x in ids]

expo = [random.expovariate(1) for x in range(5)]
# my = Model Year and all these arrays are empty to be populated for visualizations
myHCCRisk =[]
mySocialRisk = []
myHouseRisk = []
pyFullRisk = []  # py == Predicted Year full risk

for x in ids:
    var = random.expovariate(1.4) # this is our fake HCC... or our base variable
    sox = var * random.expovariate(.8) #expo == exponential distribution with a lambda of 0.8
    # sox == Social
    hous = var  * random.expovariate(.8)
    # hous == Housing
    myHCCRisk.append(var)
    mySocialRisk.append(sox)
    myHouseRisk.append(hous)
    pyFullRisk.append(var+sox+hous)
    # this is all the randomization for the "parallel coordinates" graph

riskRand = [random.expovariate(2) + random.random() for x in ids]

HCCRisk = {'2015':riskRand,'2016':[abs(random.uniform(-2,1) + x) for x in riskRand]}
SocialRisk = {'2015':[x  + random.expovariate(4) for x in riskRand]}

# #riskRand = [random.normalvariate(5,2) for x in ids]
# riskRand = myHCCRisk
# #HCCRisk = {'2015':riskRand,'2016':[x - abs(random.expovariate(1)  ) for x in riskRand]}
# HCCRisk = {'2015':riskRand,'2016':[x - random.random() for x in riskRand]}

#SocialRisk = {'2015':[abs(random.expovariate(4) + 1 + x) for x in riskRand]}

import pandas as pd
from decimal import *
getcontext().prec = 2
TotalMembership = 45000.0
TotalExpense = TotalMembership*10000
HospitalCare = TotalExpense * .3396
ProfessionalServices = TotalExpense * .2754
PrimaryCare = ProfessionalServices *.253
AmbulatorySurgery = ProfessionalServices *14
SpecialtyObservation = ProfessionalServices -AmbulatorySurgery -PrimaryCare
HomeHealth = TotalExpense * .0291
RxDrug = TotalExpense * .106
DME = TotalExpense *.0159
LongTermCare = TotalExpense * .1055
Radiology = TotalExpense * .0755
EmergencyCare = (TotalExpense - .0843)
Other = TotalExpense - HospitalCare - ProfessionalServices - HomeHealth - RxDrug -DME- LongTermCare- Radiology - EmergencyCare

d = {'Total Membership':TotalMembership, 'Expenses':{'Hospital Care':HospitalCare, 
'Professional Services':
    {'Primary Care':PrimaryCare,
     'Ambulatory Surgery':AmbulatorySurgery,
      'Specialty':SpecialtyObservation,
       'Total':ProfessionalServices},
'HomeHealth':HomeHealth, 
'RxDrug':RxDrug, 
'DME':DME,'LongTermCare':LongTermCare,
'Radiology':Radiology,
'Emergency':EmergencyCare,
'Other':Other,
'Total':TotalExpense }

}

ClaimsSummary = pd.DataFrame(d)





def getColor(count):
    colors = viridis(256)
    colors = colors * 40
    z = colors[0:count]
    return z





def dbConnect(constring):
	return True

def cursor(query):
	return range(int(TotalMembership * 2.4))

def width_calc(value):
    width = value*5
    if width > 25:
        return 25
    elif width < 2:
        return 2
    else:
        return width

def name_hcc(label):
  try:
    var = hcc_labels[label][0:8]
    return var
  except:
    return label[0:8]


hcc_labels = {'HCC1':"AIDS",
'HCC2':"Septicemia",
'HCC6':"Opportunistic_Infections",
'HCC8':"Metastatic_Cancer",
'HCC9':"Lung_Cancers",
'HCC10':"Lymphoma",
'HCC11':"Colorectal_Cancers",
'HCC12':"Breast_Prostate_Tumors",
'HCC17':"Diabetes_Acute_Complications",
'HCC18':"Diabetes_Chronic",
'HCC19':"Diabetes",
'HCC21':"Malnutrition",
'HCC22':"Obesity",
'HCC23':"Endocrine",
'HCC27':"ESLD",
'HCC28':"Cirrhosis",
'HCC29':"Hepatitis",
'HCC33':"Intestinal_Obstruction",
'HCC34':"Pancreatitis",
'HCC35':"IBD",
'HCC39':"BJM_Infections",
'HCC40':"Rheumatoid_Arthritis",
'HCC46':"Hematology_Disorders",
'HCC47':"Immunity_Disorders",
'HCC48':"Coagulation_Defects",
'HCC54':"Substance_Psychosis",
'HCC55':"Substance_Dependence",
'HCC57':"Schizophrenia",
'HCC58':"Deppresion_Bipolar",
'HCC70':"Quadriplegia",
'HCC71':"Paraplegia",
'HCC72':"Spinal_Cord_Disorders",
'HCC73':"ALS",
'HCC74':"Cerebral_Palsy",
'HCC75':"Myasthenia",
'HCC76':"Muscular_Dystrophy",
'HCC77':"Multiple_Sclerosis",
'HCC78':"Parkinson_Huntington",
'HCC79':"Seizures",
'HCC80':"Coma",
'HCC82':"Respirator_Dependence",
'HCC83':"Respiratory-Arrest",
'HCC84':"Cardio-Respiratory-Failure",
'HCC85':"CHF",
'HCC86':"AMI",
'HCC87':"IVD",
'HCC88':"Angina_Pectoris",
'HCC96':"Arrhythmias",
'HCC99':"Cerebral_Hemorrhage",
'HCC100':"Stroke",
'HCC103':"Hemiplegia",
'HCC104':"Monoplegia",
'HCC106':"Gangrene",
'HCC107':"Vascular_Disease_Complications",
'HCC108':"Vascular_Disease",
'HCC110':"Cystic_Fibrosis",
'HCC111':"COPD",
'HCC112':"Fibrosis_Lung",
'HCC114':"Pneumonias",
'HCC115':"Pneumococcal",
'HCC122':"Retinopathy",
'HCC124':"Macular_Degeneration",
'HCC134':"Dialysis_Status",
'HCC135':"Acute_Renal_Failure",
'HCC136':"CKD5",
'HCC137':"CKD6",
'HCC157':"Ulcer_Necrosis",
'HCC158':"Ulcer_Skin_Loss",
'HCC161':"Ulcer_Chronic",
'HCC162':"Burn",
'HCC166':"Head_Injury_Severe",
'HCC167':"Head_Injury",
'HCC169':"Spinal_Cord",
'HCC170':"Hip_Fracture",
'HCC173':"Amputation",
'HCC176':"Graft_Implant",
'HCC186':"Organ_Transplant",
'HCC188':"Artifical_Opening",
'HCC189':"Amputation_Complicated"}


office =['99201','99202','99203','99204','99205','99211','99212','99213','99214','99215']
nursing_facility = ['99304','99304','99305','99306','99307','99308','99309','99310', '99315','99316','99318']
rest_home = ['99324','99325','99326','99327','99328','99334','99335','99336','99337','99339','99340']
home_services = ['99341','99342','99343','99344','99345','99347','99348','99349','99350','99490','99495','99496']
wellness_visits = ['G0402','G0438','G0439']
preven_codes = [x for x in [office, nursing_facility, rest_home, wellness_visits]]

