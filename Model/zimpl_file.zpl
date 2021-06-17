# ---- Data sets -------------------------------------------------------------
set S := {read "data/Products_list.txt" as "<1s>"};
set JBase := {read "data/Weeks_list.txt" as "<1s>"};
set JNumBase := {read "data/Weeks_list.txt" as "<2n>"};

param weekToNumber[JBase] := read "data/Weeks_list.txt" as "<1s> 2n";
param numberToWeek[JNumBase] := read "data/Weeks_list.txt" as "<2n> 1s";

set J := union <j> in JNumBase: if j <= 52 then { numberToWeek[j] } else { } end;
set JNum := union <j> in JNumBase: if j <= 52 then { j } else { } end;
do print JNum;

set K := {read "data/Plants_list.txt" as "<1s>"};
set M := {read "data/Families_list.txt" as "<1s>"};

# ---- Parameters -------------------------------------------------------------
param p[S*K] := read "data/p.txt" as "<1s, 2s> 3n";  
param f[S*M] := read "data/f.txt" as "<1s, 2s> 3n";  
param v[S*JBase] := read "data/v.txt" as "<1s, 2s> 3n"; 
param initInv[S] := read "data/initInv.txt" as "<1s> 2n";  
param SafetyStock[S*JNum] := read "data/SafetyStock.txt" as "<1s, 2n> 3n";   
param AvgERate[S*K] := read "data/AvgERate.txt" as "<1s, 2s> 3n";
param EBottle[K] := read "data/EBottle.txt" as "<1s> 2n";

param AvgPRate[S*K] := read "data/AvgPRate.txt" as "<1s, 2s> 3n";
param PBottle[K] := read "data/PBottle.txt" as "<1s> 2n";

param eps := 0.01;
param extMaxCapacity := 144;

#params set by user
param ss_param := read "data/model_multipliers.txt" as "1n" use 1; #between 0 and 100.
param default_sl := read "data/model_multipliers.txt" as "1n" skip 1 use 1; #between 4 and 52
param default_minrun := read "data/model_multipliers.txt" as "1n" skip 2 use 1; #between 0 and 100K
param UseSlacks := read "data/model_multipliers.txt" as "1n" skip 3 use 1; #1 or 0

param ssWeight := read "data/model_multipliers.txt" as "1n" skip 4 use 1; #weight assigned to slack_ss variables in obj function. default 1
param slWeight := read "data/model_multipliers.txt" as "1n" skip 5 use 1;  #weight assigned to slack_sl variables in obj function. default 1
param mrWeight := read "data/model_multipliers.txt" as "1n" skip 6 use 1; #weight assigned to slack_mr variables in obj function. default 1

# ---- Variables -------------------------------------------------------------
var pr[S*J*K];          #pr[s,j,k]: amount produced of product s on week j in plant k
var inv[S*J];           #inv[s,j]: inventario del sku s al final de la semana j
var o[J*K*M] binary;    #auxiliar, whether family is produced or not
var plantSelector[S*J*K] binary; 

#slack variables 
var slack_ss[S*J]; 
var slack_sl[S*J];
var slack_mr[J*K*M];
var productionBuffer;


# ---- Constraints -------------------------------------------------------------

subto SS_SLACKS:
    forall <s,j> in S*J:
        if UseSlacks == 0 then slack_ss[s,j] == 0 end;

subto SL_SLACKS:
    forall <s,j> in S*J:
        if UseSlacks == 0 then slack_sl[s,j] == 0 end;

subto MR_SLACKS:
    forall <j,k,m> in J*K*M:
        if UseSlacks == 0 then slack_mr[j,k,m] == 0 end;

subto CORRECT_PLANT:
	forall <s,j,k> in S*J*K:
        # pr[s,j,k] <= MAX*p[s,k];
        pr[s,j,k] <= p[s,k]*(extMaxCapacity * min(AvgERate[s,k],AvgPRate[s,k]) + 1); 

subto PLANT_UNIQUENESS:
    forall <s,j,k> in S*J*K:
        # pr[s,j,k] <= MAX*plantSelector[s,j,k] and sum <l> in K: plantSelector[s,j,l] <= 1;
        pr[s,j,k] <= (extMaxCapacity * min(AvgERate[s,k],AvgPRate[s,k]) + 1) * plantSelector[s,j,k] and sum <l> in K: plantSelector[s,j,l] <= 1;

subto START_INV: 
    forall <s> in S: 
        inv[s,numberToWeek[0]] == SafetyStock[s,0];  #The beginning of week 1 is considered the "end" of week 0
        #inv[s,numberToWeek[0]] == initInv[s]  ;        # TODO change for real initInv values.

#if the family's total demand between week j and week j + default_sl is greater or equal than the default_minrun, apply the MIN_RUN restriction.                                                     
#(TODO consider if that is necessary if slack variables are used.)
set AuxFam[<s,m> in S*M] := if f[s,m] == 1 then { <s,m> } else { } end;
set SKUsInFam[<m> in M] := union <s> in S: AuxFam[s,m]; 
param limitDemand[<j,k,m> in JNum*K*M] := sum <s> in proj(SKUsInFam[m],<1>): (SafetyStock[s,j] + (sum <i> in JNum with i >= j + 5 and i <= j + default_sl: v[s,numberToWeek[i]]));

subto MIN_RUN: 
	forall <j,k,m> in JNum*K*M:
        if limitDemand[j,k,m] >= default_minrun + eps 
        then sum <s> in S: f[s,m] * pr[s,numberToWeek[j],k] <= o[numberToWeek[j],k,m] * card(SKUsInFam[m]) * (limitDemand[j,k,m] + 1)
        and sum <s> in S: f[s,m] * pr[s,numberToWeek[j],k] >= (default_minrun - slack_mr[numberToWeek[j],k,m]) - (limitDemand[j,k,m] + 1) * card(SKUsInFam[m]) * (1 - o[numberToWeek[j],k,m])
        end; 

        
subto E_BOTTLENECK:
	forall <j,k> in J*K: 
		sum <s> in S with p[s,k] == 1: pr[s,j,k] / AvgERate[s,k] <= (EBottle[k] - productionBuffer);

subto P_BOTTLENECK:
	forall <j,k> in J*K: 
		sum <s> in S with p[s,k] == 1: pr[s,j,k] / AvgPRate[s,k] <= (PBottle[k] - productionBuffer);

subto PR_INICIAL:
	forall<s,k> in S*K:
		pr[s,numberToWeek[0],k] == 0;

subto INV_DEF:
    forall <s,j> in S*JNum with j >= 1:
        inv[s,numberToWeek[j]] == inv[s,numberToWeek[j-1]] + (sum <k> in K: pr[s,numberToWeek[j],k]) - v[s,numberToWeek[j]];

subto SHELF_LIFE_BOUND:
    forall <s,j> in S*JNum with j >= 1:
        inv[s,numberToWeek[j]] <= SafetyStock[s,j] + (sum <i> in JNumBase with i >= j + 5 and i <= j + default_sl: v[s, numberToWeek[i]]) + slack_sl[s,numberToWeek[j]];
        
subto MIN_INV:
    forall <s,j> in S*JNum:
        inv[s,numberToWeek[j]] >= ((ss_param * SafetyStock[s,j]) / 100) - slack_ss[s,numberToWeek[j]]; 
     

# --- objective function -------------------------------------------------------------   
minimize obj: card(S*J*K)*(- productionBuffer + sum <j,k,m> in J*K*M: mrWeight*slack_mr[j,k,m]/100 + sum <s,j> in S*J: slWeight*slack_sl[s,j]/100 + sum <s,j> in S*J: ssWeight*slack_ss[s,j]/100) 
                + sum <s,j,k> in S*J*K: plantSelector[s,j,k]; #this part is the "real" objective function

