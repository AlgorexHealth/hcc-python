options mlogic mcompile;
/*
    The following is JCL if you are using an IBM-type mainframe:

   //JOBCARD
   //V2116H1P EXEC SAS94,REGION=8M,
   // OPTIONS='ERRORS=0,NOCENTER,NEWS'
   //WORK  DD SPACE=(CYL,(1000,2))
   //WORK1 DD SPACE=(CYL,(2000,2))
   //* user-defined the location of formats
   //LIBRARY DD DISP=SHR,DSN=XXXX.XXXXXXX
   //*user-defined the location of macros
   //IN0 DD DISP=SHR,DSN=XXXX.XXXXXX
   //*the location of person-level file
   //IN1 DD DISP=SHR,DSN=XXXX.PERSON
   //*the location of the diagnosis file
   //IN2 DD DISP=SHR,DSN=XXXX.DIAG
   //*the location of the file containing all coefficients
   //INCOEF DD DISP=SHR,DSN=XXXX.HCCCOEFN
   //*the output file containing person-level scores
   //OUT DD DISP=(NEW,CATLG,KEEP),
   //    DSN=XXX.V2116H1P.PERSON,
   //    SPACE=(TRK,(20,10),RLSE)
   //SYSIN  DD *

   ******************************************************************
  If you are using PC-SAS, you must specify the location of the files
  on your PC in a libname/filename statement.

  LIBNAME LIBRARY "location of formats";
  FILENAME IN0 "location of macros";
  LIBNAME  IN1 "location of person-level file";
  LIBNAME  IN2 "location of diagnosis file";
  LIBNAME  INCOEF "location of the coefficients file";
  LIBNAME  OUT "location for the output file";
  */
  LIBNAME LIBRARY "/folders/myfolders/algorex";
  FILENAME IN0 "/folders/myfolders/CMS-HCC software V2116.87.H1";
  LIBNAME  IN1 "/folders/myfolders/algorex";
  LIBNAME  IN2 "/folders/myfolders/algorex";
  LIBNAME  INCOEF "/folders/myfolders/algorex";
  LIBNAME  OUT "/folders/myfolders/output";
 ***********************************************************************
 *
 *   DESCRIPTION:
 *
 * V2116H1P program creates eighty seven HCC variables version 21 
 * (&HCCV21_list87) and three score variables for each person who is 
 * present in a person file (supplied by a user).
 * If a person has at least one diagnosis in DIAG file (supplied by a
 * user) then HCC variables are created, otherwise HCCs are set to 0.
 * Score variables are created using coefficients from 3 final
 * models: community, institutional, new enrollees.
 *
 * Assumptions about input files:
 *   - both files are sorted by person ID
 *
 *   - person level file has the following variables:
 *     :&IDVAR  - person ID variable (it is a macro parameter, HICNO  
 *                for Medicare data)
 *     :DOB     - date of birth
 *     :SEX     - sex
 *     :OREC    - original reason for entitlement
 *     :MCAID   - Medicaid dummy variable (base year)
 *     :NEMCAID - Medicaid dummy variable for new enrollees (predicted
 *                year)
 *
 *   - diagnosis level file has the following vars:
 *     :&IDVAR  - person ID variable (it is a macro parameter, HICNO 
 *                for Medicare data)
 *     :DIAG    - diagnosis
 *     :DIAG_TYPE - diagnosis version ('9' for ICD9 and '0' for ICD10)
 *
 * The program supplies parameters to a main macro %V2116H1M that calls
 * other external macros specific to V21 HCCs:
 *
 *      %AGESEXV2   - create age/sex, originally disabled, disabled vars
 *      %V21I9ED1   - perform edits to ICD9 diagnosis
 *      %V21I0ED1   - perform edits to ICD10 diagnosis
 *      %V20H87L1   - assign labels to HCCs
 *      %V20H87H1   - set HCC=0 according to hierarchies
 *      %SCOREVAR   - calculate a score variable
 *
 * Program steps:
 *         step1: include external macros
 *         step2: define internal macro variables
 *         step3: merge person and diagnosis files outputting one
 *                record per person for each input person level record
 *         step3.1: declaration section
 *         step3.2: bring regression coefficients
 *         step3.3: merge person and diagnosis file
 *         step3.4: for the first record for a person set CC to 0
 *                  and calculate age
 *         step3.5: if there are any diagnoses for a person
 *                  then do the following:
 *                   - perform ICD9 edits using V21I9ED1 macro or
 *                     perform ICD10 edits using V21I0ED1 macro
 *                   - create CC using provided format 
 *                   - create additional CC using additional formats
 *         step3.6: for the last record for a person do the
 *                  following:
 *                   - create demographic variables needed
 *                     for regressions (macro AGESEXV2)
 *                   - create HCC using hierarchies (macro V20H87H1)
 *                   - create HCC interaction variables
 *                   - create HCC and DISABL interaction variables
 *                   - set HCCs and interaction vars to zero if there
 *                     are no diagnoses for a person
 *                   - create score for community model
 *                   - create score for institutional model
 *                   - create score for new enrollee model
 *                   - normalize score if needed
 *         step4: data checks and proc contents
 *
 *   USER CUSTOMIZATION:
 *
 * A user must supply 2 files with the variables described above and
 * set the following parameters:
 *      INP      - SAS input person dataset
 *      IND      - SAS input diagnosis dataset
 *      OUTDATA  - SAS output dataset
 *      IDVAR    - name of person id variable (HICNO for medicare data)
 *      KEEPVAR  - variables to keep in the output dataset
 *      SEDITS   - a switch that controls whether to perform MCE edits
 *                 on ICD9 and ICD10: 1-YES, 0-NO
 *      DATE_ASOF- reference date to calculate age. Set to February 1  
 *                 of the payment year for consistency with CMS. 
 *      DF       - normalization factor (set to 1 by default)
 ***********************************************************************;

 %LET INPUTVARS=%STR(SEX DOB MCAID NEMCAID OREC);

 %*demographic variables;
 %LET DEMVARS  =%STR(AGEF ORIGDS DISABL
                     F0_34  F35_44 F45_54 F55_59 F60_64 F65_69
                     F70_74 F75_79 F80_84 F85_89 F90_94 F95_GT
                     M0_34  M35_44 M45_54 M55_59 M60_64 M65_69
                     M70_74 M75_79 M80_84 M85_89 M90_94 M95_GT
                     NEF0_34  NEF35_44 NEF45_54 NEF55_59 NEF60_64
                     NEF65    NEF66    NEF67    NEF68    NEF69
                     NEF70_74 NEF75_79 NEF80_84 NEF85_89 NEF90_94
                     NEF95_GT
                     NEM0_34  NEM35_44 NEM45_54 NEM55_59 NEM60_64
                     NEM65    NEM66    NEM67    NEM68    NEM69
                     NEM70_74 NEM75_79 NEM80_84 NEM85_89 NEM90_94
                     NEM95_GT);

 %*list of HCCs included in models;
 %LET HCCV21_list87 = %STR(      
      HCC1    HCC2    HCC6    HCC8    HCC9    HCC10   HCC11   HCC12 
      HCC17   HCC18   HCC19   HCC21   HCC22   HCC23   HCC27   HCC28
      HCC29   HCC33   HCC34   HCC35   HCC39   HCC40   HCC46   HCC47 
      HCC48   HCC51   HCC52   HCC54   HCC55   HCC57   HCC58   HCC70 
      HCC71   HCC72   HCC73   HCC74   HCC75   HCC76   HCC77   HCC78 
      HCC79   HCC80   HCC82   HCC83   HCC84   HCC85   HCC86   HCC87 
      HCC88   HCC96   HCC99   HCC100  HCC103  HCC104  HCC106  HCC107
      HCC108  HCC110  HCC111  HCC112  HCC114  HCC115  HCC122  HCC124
      HCC134  HCC135  HCC136  HCC137  HCC138  HCC139  HCC140  HCC141
      HCC157  HCC158  HCC159  HCC160  HCC161  HCC162  HCC166  HCC167
      HCC169  HCC170  HCC173  HCC176  HCC186  HCC188  HCC189  
      );

 %*list of CCs that correspond to model HCCs;
 %LET CCV21_list87 = %STR(      
      CC1     CC2     CC6     CC8     CC9     CC10    CC11    CC12 
      CC17    CC18    CC19    CC21    CC22    CC23    CC27    CC28
      CC29    CC33    CC34    CC35    CC39    CC40    CC46    CC47 
      CC48    CC51    CC52    CC54    CC55    CC57    CC58    CC70 
      CC71    CC72    CC73    CC74    CC75    CC76    CC77    CC78 
      CC79    CC80    CC82    CC83    CC84    CC85    CC86    CC87 
      CC88    CC96    CC99    CC100   CC103   CC104   CC106   CC107
      CC108   CC110   CC111   CC112   CC114   CC115   CC122   CC124
      CC134   CC135   CC136   CC137   CC138   CC139   CC140   CC141
      CC157   CC158   CC159   CC160   CC161   CC162   CC166   CC167
      CC169   CC170   CC173   CC176   CC186   CC188   CC189   
      );

 %LET SCOREVARS=%STR(SCORE_COMMUNITY
                     SCORE_INSTITUTIONAL
                     SCORE_NEW_ENROLLEE);

 %* include main macro;
 %INCLUDE IN0(V2116H1M)/SOURCE2;

 %V2116H1M(INP      =IN1._2010bene,
           IND      =IN2._2010diag,
           OUTDATA  =OUT._2010results,
           IDVAR    =HICNO,
           KEEPVAR  =HICNO &INPUTVARS &SCOREVARS &DEMVARS 
                     &HCCV21_list87 &CCV21_list87, 
           SEDITS   =1,
           DATE_ASOF="1FEB2016"D);