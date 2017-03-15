 %MACRO V21I9ED1(AGE=, SEX=, ICD9= );
 %**********************************************************************
 ***********************************************************************
 1  MACRO NAME:  V21I9ED1
 2  PURPOSE:     age/sex edits on ICD9: some edits are mandatory, 
                 others - are based on MCE list to check
                 if age or sex for a beneficiary is within the
                 range of acceptable age/sex, if not- CC is set to 
                 -1.0 - invalid
 3  PARAMETERS:  AGE   - beneficiary age variable calculated by DOB
                         from a person level file
                 SEX   - beneficiary SEX variable in a person level file
                 ICD9  - diagnosis variable in a diagnosis file

 4  COMMENTS:    1. Age format AGEFMT9 and sex format SEXFMT9 are 
                    parameters in the main macro. They have to 
                    correspond to the years of data

                 2. If ICD9 code does not have any restriction on age
                    or sex then the corresponding format puts it in "-1"

                 3. AGEL format sets lower limits for age
                    AGEU format sets upper limit for age
                    for specific edit categories:
                    "0"= "0 newborn (age 0)      "
                    "1"= "1 pediatric (age 0 -17)"
                    "2"= "2 maternity (age 12-55)"
                    "3"= "3 adult (age 14+)      "

                 4. SEDITS - parameter for the main macro
 **********************************************************************;
   %* reset of CCs that is based on beneficiary age or sex;
   /* Hemophilia for women*/ 
   IF &SEX="2" AND &ICD9 IN ("2860", "2861")  THEN CC="48"; 
   ELSE
   /*emphysema/chronic bronchitis */
   IF &AGE < 18 AND &ICD9 IN ("4910", "4911", "49120", "49121", "49122",
                              "4918", "4919", "4920",  "4928",  "496",  
                              "5181", "5182") THEN CC="112";
   ELSE
   /*chronic obstructive asthma */
   IF &AGE < 18 AND &ICD9 IN ("49320", "49321", "49322") 
                                              THEN CC="-1.0";

  %* MCE edits if needed (should be decided by a user by setting
     parameter SEDITS);
  %IF &SEDITS = 1 %THEN %DO;
     %* check if Age is within acceptable range;
     _TAGE=PUT(&ICD9, $&AGEFMT9..);
     IF _TAGE NE "-1" AND
        (&AGE < INPUT(PUT(_TAGE, $AGEL.),8.) OR
         &AGE > INPUT(PUT(_TAGE, $AGEU.),8.)) THEN CC='-1.0';

     %* check if Sex for a person is the one in the MCE file;
     _TSEX=PUT(&ICD9, $&SEXFMT9..);
     IF _TSEX NE "-1"  & _TSEX NE &SEX THEN CC='-1.0';

  %END;
 %MEND V21I9ED1;