 %MACRO SCOREVAR( PVAR=, RLIST=, CPREF=);
 %**********************************************************************
 ***********************************************************************
  1  MACRO NAME:     SCOREVAR
  2  PURPOSE:        calculate SCORE variable
  3  PARAMETERS:
                     PVAR    - SCORE variable name
                     RLIST   - regression variables list
                     CPREF   - coefficients Prefix: coefficients name
                               are the same as corresponding variable
                               name with thei prefix
 ***********************************************************************;
   %LOCAL I;
   %LET I=1;
   &PVAR=0;
   %DO %UNTIL(%SCAN(&RLIST,&I)=);
       &PVAR = &PVAR + %SCAN(&RLIST,&I)*&CPREF%SCAN(&RLIST,&I);
       %LET I=%EVAL(&I+1);
   %END;

 %MEND SCOREVAR;