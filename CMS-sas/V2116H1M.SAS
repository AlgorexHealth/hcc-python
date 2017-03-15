 %MACRO V2116H1M(INP=, IND=, OUTDATA=, IDVAR=, KEEPVAR=, SEDITS=,
                 DATE_ASOF=, 
                 FMNAME9=V21Y15RC, FMNAME0=V21Y16RC, 
                 AGEFMT9=I9AGEY15MCE, SEXFMT9=I9SEXY15MCE, 
                 AGEFMT0=I0AGEY16MCE, SEXFMT0=I0SEXY16MCE, DF=1, 
                 AGESEXMAC=AGESEXV2, EDITMAC9=V21I9ED1,
                 EDITMAC0=V21I0ED1, LABELMAC=V20H87L1, 
                 HIERMAC=V20H87H1, SCOREMAC=SCOREVAR);
%**********************************************************************
 * V2116H1M creates HCC and score variables for each person who is
 * present in a person file.
 * If a person has at least one diagnosis in DIAG file then HCCs are
 * created, otherwise HCCs are set to 0.
 * Score variables are created using coefficients from 3 final
 * models: community, institutional, new enrollees.
 *
 * Assumptions about input files:
 *   - both files are sorted by person ID
 *   - person level file has the following variables:
 *     :&IDVAR  - person ID variable (it is a macro parameter)
 *     :DOB     - date of birth
 *     :SEX     - sex
 *     :OREC    - original reason for entitlement
 *     :MCAID   - Medicaid dummy variable
 *     :NEMCAID - Medicaid dummy variable for new enrollees
 *
 *   - diagnosis level file has the following variables:
 *     :&IDVAR    - person ID variable (it is a macro parameter)
 *     :DIAG      - diagnosis
 *     :DIAG_TYPE - '9' for ICD9, '0' for ICD10
 *
 * Parameters:
 *      INP       - input person dataset
 *      IND       - input diagnosis dataset
 *      OUTDATA   - output dataset
 *      IDVAR     - name of person id variable (HICNO for Medicare data)
 *      KEEPVAR   - variables to keep in the output file
 *      SEDITS    - a switch that controls whether to perform MCE  
 *                  edits on ICD9 and ICD10: 1-YES, 0-NO
 *      DATE_ASOF - reference date to calculate age. Set to February 1
 *                  of the payment year for consistency with CMS.
 *      FMNAME9   - format name (crosswalk ICD9 to V21 CCs)
 *      FMNAME0   - format name (crosswalk ICD10 to V21 CCs)
 *      AGEFMT9   - format name (crosswalk ICD9 to acceptable age range
 *                  in case MCE edits on diags are to be performed)
 *      AGEFMT0   - format name (crosswalk ICD10 to acceptable age range
 *                  in case MCE edits on diags are to be performed)
 *      SEXFMT9   - format name (crosswalk ICD9 to acceptable sex in 
 *                  case MCE edits on diags are to be performed)
 *      SEXFMT0   - format name (crosswalk ICD10 to acceptable sex in 
 *                  case MCE edits on diags are to be performed)
 *      DF        - normalization factor.
 *                  Default=1
 *      AGESEXMAC - external macro name: create age/sex,
 *                  originally disabled, disabled vars
 *      EDITMAC9  - external macro name: perform edits to ICD9
 *      EDITMAC0  - external macro name: perform edits to ICD10
 *      LABELMAC  - external macro name: assign labels to HCCs
 *      HIERMAC   - external macro name: set HCC=0 according to
 *                  hierarchies
 *      SCOREMAC  - external macro name: calculate a score variable
 **********************************************************************;

 %**********************************************************************
 * step1: include external macros
 **********************************************************************;
 %IF "&AGESEXMAC" ne "" %THEN %DO;
     %INCLUDE IN0(&AGESEXMAC) /SOURCE2; %* create demographic variables;
 %END;
 %IF "&EDITMAC9" ne "" %THEN %DO;
     %INCLUDE IN0(&EDITMAC9)   /SOURCE2; %* perform edits on ICD9;
 %END;
 %IF "&EDITMAC0" ne "" %THEN %DO;
     %INCLUDE IN0(&EDITMAC0)   /SOURCE2; %* perform edits on ICD10;
 %END;
 %IF "&LABELMAC" ne "" %THEN %DO;
     %INCLUDE IN0(&LABELMAC)  /SOURCE2; %* hcc labels;
 %END;
 %IF "&HIERMAC" ne "" %THEN %DO;
     %INCLUDE IN0(&HIERMAC)   /SOURCE2; %* hierarchies;
 %END;
 %IF "&SCOREMAC" ne "" %THEN %DO;
     %INCLUDE IN0(&SCOREMAC)  /SOURCE2; %* calculate score variable;
 %END;

 %**********************************************************************
 * step2: define internal macro variables
 **********************************************************************;

 %LET N_CC=201;          %*max # of HCCs;

 %* age/sex variables for community and insititutional regression;
 %LET AGESEXV=  F0_34  F35_44 F45_54 F55_59 F60_64 F65_69
                F70_74 F75_79 F80_84 F85_89 F90_94 F95_GT
                M0_34  M35_44 M45_54 M55_59 M60_64 M65_69
                M70_74 M75_79 M80_84 M85_89 M90_94 M95_GT;


 %* diagnostic categories necessary to create interaction variables;
 %LET DIAG_CAT= CANCER  DIABETES  IMMUNE  CHF     CARD_RESP_FAIL
                COPD    RENAL     COMPL   SEPSIS  PRESSURE_ULCER;


 %*interaction variables for Community regression;
 %LET INTERRACC_VARS = %STR(DISABLED_HCC6         DISABLED_HCC34
                            DISABLED_HCC46        DISABLED_HCC54
                            DISABLED_HCC55        DISABLED_HCC110
                            DISABLED_HCC176       SEPSIS_CARD_RESP_FAIL
                            CANCER_IMMUNE         DIABETES_CHF
                            CHF_COPD              CHF_RENAL
                            COPD_CARD_RESP_FAIL);

 %*variables for Community regression ;
 %LET COMM_REG= %STR(&AGESEXV
                     MCAID_Female_Aged          MCAID_Female_Disabled
                     MCAID_Male_Aged            MCAID_Male_Disabled
                     OriginallyDisabled_Female  OriginallyDisabled_Male
                     &INTERRACC_VARS
                     &HCCV21_list87);


 %*interaction variables for Institutional regression;
 %LET INTERRACI_VARS = %STR(DISABLED_HCC85       DISABLED_PRESSURE_ULCER
                            DISABLED_HCC161      DISABLED_HCC39
                            DISABLED_HCC77       DISABLED_HCC6
                            CHF_COPD COPD_CARD_RESP_FAIL
                            SEPSIS_PRESSURE_ULCER
                            SEPSIS_ARTIF_OPENINGS
                            ART_OPENINGS_PRESSURE_ULCER
                            DIABETES_CHF
                            COPD_ASP_SPEC_BACT_PNEUM
                            ASP_SPEC_BACT_PNEUM_PRES_ULC
                            SEPSIS_ASP_SPEC_BACT_PNEUM
                            SCHIZOPHRENIA_COPD
                            SCHIZOPHRENIA_CHF
                            SCHIZOPHRENIA_SEIZURES);

 %*variables for Institutional regression;
 %LET INST_REG = %STR(&AGESEXV
                      MCAID  ORIGDS
                      &INTERRACI_VARS
                      &HCCV21_list87);


 %*variables for New Enrollees regression  ;
 %LET NE_REG=%STR(NEF0_34  NEF35_44 NEF45_54 NEF55_59 NEF60_64
                  NEF65    NEF66    NEF67    NEF68    NEF69
                  NEF70_74 NEF75_79 NEF80_84 NEF85_89 NEF90_94 NEF95_GT
                  NEM0_34  NEM35_44 NEM45_54 NEM55_59 NEM60_64
                  NEM65    NEM66    NEM67    NEM68    NEM69
                  NEM70_74 NEM75_79 NEM80_84 NEM85_89 NEM90_94 NEM95_GT
                  MCAID_FEMALE0_64  MCAID_FEMALE65    MCAID_FEMALE66_69
                  MCAID_FEMALE70_74 MCAID_FEMALE75_GT
                  MCAID_MALE0_64    MCAID_MALE65      MCAID_MALE66_69
                  MCAID_MALE70_74   MCAID_MALE75_GT
                  Origdis_female65     Origdis_female66_69
                  Origdis_female70_74  Origdis_female75_GT
                  Origdis_male65       Origdis_male66_69
                  Origdis_male70_74    Origdis_male75_GT);



 %**********************************************************************
 * step3: merge person and diagnosis files outputting one record
 *        per person with score and HCC variables for each input person
 *        level record
 ***********************************************************************;

 DATA &OUTDATA(KEEP=&KEEPVAR );
   %****************************************************
    * step3.1: declaration section
    ****************************************************;

    %IF "&LABELMAC" ne "" %THEN %&LABELMAC;  *HCC labels;

   %* length of new variables (length for other age/sex vars is set in
      &AGESEXMAC macro);
    LENGTH CC $4. AGEF 3.
           MCAID_Female_Aged          MCAID_Female_Disabled
           MCAID_Male_Aged            MCAID_Male_Disabled
           OriginallyDisabled_Female  OriginallyDisabled_Male
           MCAID_FEMALE0_64  MCAID_FEMALE65    MCAID_FEMALE66_69
           MCAID_FEMALE70_74 MCAID_FEMALE75_GT
           MCAID_MALE0_64    MCAID_MALE65      MCAID_MALE66_69
           MCAID_MALE70_74   MCAID_MALE75_GT
           Origdis_female65     Origdis_female66_69
           Origdis_female70_74  Origdis_female75_GT
           Origdis_male65       Origdis_male66_69
           Origdis_male70_74    Origdis_male75_GT
           CC1-CC&N_CC
           HCC1-HCC&N_CC
           &DIAG_CAT
           &INTERRACC_VARS
           &INTERRACI_VARS 3.;

    %*retain cc vars;
    RETAIN CC1-CC&N_CC 0  AGEF
           ;
    %*arrays;
    ARRAY C(&N_CC)  CC1-CC&N_CC;
    ARRAY HCC(&N_CC) HCC1-HCC&N_CC;
    %*interaction vars;
    ARRAY RV &INTERRACC_VARS &INTERRACI_VARS &DIAG_CAT;

    %***************************************************
    * step3.2: to bring in regression coefficients
    ****************************************************;
    IF _N_ = 1 THEN SET INCOEF.HCCCOEFN;
    %***************************************************
    * step3.3: merge
    ****************************************************;
    MERGE &INP(IN=IN1)
          &IND(IN=IN2);
    BY &IDVAR;

    IF IN1 THEN DO;

    %*******************************************************
    * step3.4: for the first record for a person set CC to 0
    ********************************************************;

       IF FIRST.&IDVAR THEN DO;
          %*set ccs to 0;
           DO I=1 TO &N_CC;
            C(I)=0;
           END;
           %* age;
           AGEF =FLOOR((INTCK(
                'MONTH',DOB,&DATE_ASOF)-(DAY(&DATE_ASOF)<DAY(DOB)))/12);
       END;

    %***************************************************
    * step3.5 if there are any diagnoses for a person
    *         then do the following:
    *         - perform diag edits using macro &EDITMAC9 if ICD9 or
    *           &EDITMAC0 if ICD10
    *         - create CC using corresponding formats for ICD9
    *           or ICD10     
    *         - assign additional CC using provided additional formats
    ****************************************************;
       IF IN1 & IN2 THEN DO;
          %*initialize;
          CC="9999";

          IF DIAG_TYPE = "9" THEN DO;
             %IF "&EDITMAC9" NE "" %THEN 
                  %&EDITMAC9(AGE=AGEF,SEX=SEX,ICD9=DIAG); 
             IF CC NE "-1.0" AND CC NE "9999" THEN DO;
                IND=INPUT(CC,4.);
                IF 1 <= IND <= &N_CC THEN C(IND)=1;
             END;
             ELSE IF CC="9999" THEN DO;
                ** primary assignment **;
                IND = INPUT(LEFT(PUT(DIAG,$I9&FMNAME9..)),4.);
                IF 1 <= IND <= &N_CC THEN C(IND)=1;
                ** duplicate assignment **;
                IND = INPUT(LEFT(PUT(DIAG,$I9DUP&FMNAME9..)),4.);
                IF 1 <= IND <= &N_CC THEN C(IND)=1;
             END;
          END;

          ELSE IF DIAG_TYPE = "0" THEN DO;
              %IF "&EDITMAC0" NE "" %THEN 
                   %&EDITMAC0(AGE=AGEF,SEX=SEX,ICD10=DIAG); 
              IF CC NE "-1.0" AND CC NE "9999" THEN DO;
                 IND=INPUT(CC,4.);
                 IF 1 <= IND <= &N_CC THEN C(IND)=1;
              END;
              ELSE IF CC="9999" THEN DO;
                 ** primary assignment **;
                 IND = INPUT(LEFT(PUT(DIAG,$I0&FMNAME0..)),4.);
                 IF 1 <= IND <= &N_CC THEN C(IND)=1;
                 ** duplicate assignment **;
                 IND = INPUT(LEFT(PUT(DIAG,$I0DUP&FMNAME0..)),4.);
                 IF 1 <= IND <= &N_CC THEN C(IND)=1;
                 ** secondary assignment **;
                 IND = INPUT(LEFT(PUT(DIAG,$I0SEC&FMNAME0..)),4.);
                 IF 1 <= IND <= &N_CC THEN C(IND)=1;
              END;
          END;
       END; %*CC creation;

    %*************************************************************
    * step3.6 for the last record for a person do the
    *         following:
    *         - create demographic variables needed (macro &AGESEXMAC)
    *         - create HCC using hierarchies (macro &HIERMAC)
    *         - create HCC interaction variables
    *         - create HCC and DISABL interaction variables
    *         - set HCCs and interaction vars to zero if there
    *           are no diagnoses for a person
    *         - create score for community model
    *         - create score for institutional model
    *         - create score for new enrollee model
    **************************************************************;
       IF LAST.&IDVAR THEN DO;

           %****************************
           * demographic vars
           *****************************;
           %*create age/sex cells, originally disabled, disabled vars;
           %IF "&AGESEXMAC" ne "" %THEN
           %&AGESEXMAC(AGEF=AGEF, SEX=SEX, OREC=OREC);

           %*interaction;
           MCAID_Female_Aged     = MCAID*(SEX='2')*(1 - DISABL);
           MCAID_Female_Disabled = MCAID*(SEX='2')*DISABL;
           MCAID_Male_Aged       = MCAID*(SEX='1')*(1 - DISABL);
           MCAID_Male_Disabled   = MCAID*(SEX='1')*DISABL;
           OriginallyDisabled_Female= ORIGDS*(SEX='2');
           OriginallyDisabled_Male  = ORIGDS*(SEX='1');

           %* NE interactions;
           MCAID_female0_64   =(SEX="2" & 0<=AGEF <65 & NEF65=0
                                     & NEMCAID>0);
           MCAID_female65     =(SEX="2" & NEF65 & NEMCAID>0);
           MCAID_female66_69  =(SEX="2" &
                              sum(NEF66,NEF67,NEF68,NEF69) & NEMCAID>0);
           MCAID_female70_74  =(SEX="2" & 70<=AGEF <75 & NEMCAID>0);
           MCAID_female75_GT  =(SEX="2" & AGEF >74 & NEMCAID>0);

           MCAID_male0_64     =(SEX="1" & 0<=AGEF <65 & NEM65=0
                                   & NEMCAID>0);
           MCAID_male65       =(SEX="1" & NEM65 & NEMCAID>0);
           MCAID_male66_69    =(SEX="1" &
                              sum(NEM66,NEM67,NEM68,NEM69) & NEMCAID>0);
           MCAID_male70_74    =(SEX="1" & 70<=AGEF <75
                                     & NEMCAID>0);
           MCAID_male75_GT    =(SEX="1" & AGEF >74 & NEMCAID>0);

           Origdis_female65      =(ORIGDS & NEF65 & SEX='2');
           Origdis_female66_69   =(ORIGDS &
                              sum(NEF66,NEF67,NEF68,NEF69) & SEX='2');
           Origdis_female70_74  =(ORIGDS & 70 <= AGEF  <75 & SEX='2');
           Origdis_female75_GT  =(ORIGDS & AGEF >74 & SEX='2');

           Origdis_male65       =(ORIGDS & NEM65 & SEX='1');
           Origdis_male66_69    =(ORIGDS &
                              sum(NEM66,NEM67,NEM68,NEM69) & SEX='1');
           Origdis_male70_74    =(ORIGDS & 70 <= AGEF  <75 & SEX='1');
           Origdis_male75_GT    =(ORIGDS & AGEF >74 & SEX='1');

           IF IN1 & IN2 THEN DO;
            %**********************
            * hierarchies
            **********************;
            %IF "&HIERMAC" ne "" %THEN %&HIERMAC;
            %************************
            * interaction variables
            *************************;
            %*community model diagnostic categories;
            CANCER         = MAX(HCC8, HCC9, HCC10, HCC11, HCC12);
            DIABETES       = MAX(HCC17, HCC18, HCC19);
            IMMUNE         = HCC47;
            CARD_RESP_FAIL = MAX(HCC82, HCC83, HCC84);
            CHF            = HCC85;
            COPD           = MAX(HCC110, HCC111);
            RENAL          = MAX(HCC134, HCC135, HCC136, HCC137,
                                 HCC138, HCC139, HCC140, HCC141);
            COMPL          = HCC176;
            SEPSIS         = HCC2;
            %*interactions ;
            SEPSIS_CARD_RESP_FAIL =  SEPSIS*CARD_RESP_FAIL;
            CANCER_IMMUNE         =  CANCER*IMMUNE;
            DIABETES_CHF          =  DIABETES*CHF ;
            CHF_COPD              =  CHF*COPD     ;
            CHF_RENAL             =  CHF*RENAL    ;
            COPD_CARD_RESP_FAIL   =  COPD*CARD_RESP_FAIL  ;
            %*interactions with disabled ;
            DISABLED_HCC6   = DISABL*HCC6;   %*Opportunistic Infections;
            DISABLED_HCC34  = DISABL*HCC34;  %*Chronic Pancreatitis;
            DISABLED_HCC46  = DISABL*HCC46;  %*Severe Hematol Disorders;
            DISABLED_HCC54  = DISABL*HCC54;  %*Drug/Alcohol Psychosis;
            DISABLED_HCC55  = DISABL*HCC55;  %*Drug/Alcohol Dependence;
            DISABLED_HCC110 = DISABL*HCC110; %*Cystic Fibrosis;
            DISABLED_HCC176 = DISABL*HCC176; %* added 7/2009;

            %*institutional model;
            PRESSURE_ULCER = MAX(HCC157, HCC158, HCC159, HCC160);
            SEPSIS_PRESSURE_ULCER = SEPSIS*PRESSURE_ULCER;
            SEPSIS_ARTIF_OPENINGS = SEPSIS*(HCC188);
            ART_OPENINGS_PRESSURE_ULCER = (HCC188)*PRESSURE_ULCER;
            DIABETES_CHF = DIABETES*CHF;
            COPD_ASP_SPEC_BACT_PNEUM = COPD*(HCC114);
            ASP_SPEC_BACT_PNEUM_PRES_ULC = (HCC114)*PRESSURE_ULCER;
            SEPSIS_ASP_SPEC_BACT_PNEUM = SEPSIS*(HCC114);
            SCHIZOPHRENIA_COPD = (HCC57)*COPD;
            SCHIZOPHRENIA_CHF= (HCC57)*CHF;
            SCHIZOPHRENIA_SEIZURES = (HCC57)*(HCC79);

            DISABLED_HCC85          = DISABL*(HCC85);
            DISABLED_PRESSURE_ULCER = DISABL*PRESSURE_ULCER;
            DISABLED_HCC161         = DISABL*(HCC161);
            DISABLED_HCC39          = DISABL*(HCC39);
            DISABLED_HCC77          = DISABL*(HCC77);

           END; *there are some diagnoses for a person;
           ELSE DO;
              DO I=1 TO &N_CC;
                 HCC(I)=0;
              END;
              DO OVER RV;
                 RV=0;
              END;
           END;

           %*score calculation;

           /***************************/
           /*    community model      */
           /***************************/;

        %IF "&SCOREMAC" ne "" %THEN %DO;
        %&SCOREMAC(PVAR=SCORE_COMMUNITY, RLIST=&COMM_REG, CPREF=CE_);

           /***************************/
           /*   institutional model   */
           /***************************/;

        %&SCOREMAC(PVAR=SCORE_INSTITUTIONAL, RLIST=&INST_REG, CPREF=INS_);

           /***************************/
           /*   new enrollees model   */
           /***************************/;

        %&SCOREMAC(PVAR=SCORE_NEW_ENROLLEE, RLIST=&NE_REG, CPREF=NE_);
        %END;

           /****************************/
           /*   normalize the scores   */
           /***************************/;
          SCORE_COMMUNITY      = SCORE_COMMUNITY    *&DF;
          SCORE_INSTITUTIONAL  = SCORE_INSTITUTIONAL*&DF;
          SCORE_NEW_ENROLLEE   = SCORE_NEW_ENROLLEE *&DF;

          OUTPUT &OUTDATA;
       END; %*last record for a person;
     END; %*there is a person record;
 RUN;

 %**********************************************************************
 * step4: data checks and proc contents
 ***********************************************************************;
 PROC PRINT U DATA=&OUTDATA(OBS=46);
     TITLE '*** V2116H1M output file ***';
 RUN ;
 PROC CONTENTS DATA=&OUTDATA;
 RUN;

 %MEND V2116H1M;