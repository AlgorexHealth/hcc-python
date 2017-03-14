
 # Program steps:
 #         step1: include external macros
 #         step2: define internal macro variables
 #         step3: merge person and diagnosis files outputting one
 #                record per person for each input person level record
 #         step3.1: declaration section
 #         step3.2: bring regression coefficients
 #         step3.3: merge person and diagnosis file
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


def score_beneficiaries(bene):

