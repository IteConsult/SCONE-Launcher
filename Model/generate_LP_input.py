import pandas as pd
import numpy as np

# ---------- Define column names ---------------------------------------- #
SKU = "Item"
Week = "Week"
Plant = "Plant"
Family = "Formula"
Extruder = "Extruder"
Packline = "Packline"
DemandAmt = "Amount"
SafetyStock = "SafetyStock"
Rate = "Rate"
InitInv = "Initial Inventory"
PlantMinRun = "Minimum Run"
PlantMaxRun =  "Maximum Run"
Description = "Description"
Category = "Category"
Costs = "Costs"


def NumberToWeek(number):
    if number <= 9:
        return "2018-0" + str(number)
    return "2018-" + str(number)

def WeekToNumber(weekString):
    return int(weekString.split("-")[1])

def ListOfWeeks(startWeek, endWeek):
    res = []
    for i in range(startWeek, endWeek, 1):
        value = NumberToWeek(i)
        res.append(value)
    return res

def GetCorrectWeekFormat(badFormat):
    return badFormat[:4] + "-" + badFormat[4:]

# ------------ read excels ----------------------------------------------- #

print("Reading files...")

filepath = ""





#demand = pd.read_excel(filepath + "demand_test.xlsx", dtype=str)
extruders = pd.read_excel(filepath + "extruders_test.xlsx", sheet_name="db_extruders", dtype=str)
packlines = pd.read_excel(filepath + "extruders_test.xlsx", sheet_name="db_packlines", dtype=str)
SKUs = pd.read_excel(filepath + "Skus_test.xlsx", dtype=str)

extruders = extruders.dropna().set_axis([SKU, Plant, Extruder, Rate], axis=1)
packlines = packlines.dropna().set_axis([SKU, Plant, Packline, Rate, PlantMinRun, PlantMaxRun], axis=1)
SKUs = SKUs.dropna().set_axis([SKU, Description, Family, Category, Plant, Costs, InitInv], axis=1)


# ---- read old demand file (temp) ----
Demand = pd.read_excel(filepath + "demand_test.xlsx", dtype=str)

Demand["FCST (Lbs)"] = Demand["FCST (Lbs)"].astype(float)
Demand["FCST (Cs)"] = Demand["FCST (Cs)"].astype(float)
Demand["FCST (Ea)"] = Demand["FCST (Ea)"].astype(float)
Demand["FCST ($)"] = Demand["FCST ($)"].astype(float)
Demand["FCST (Tons)"] = Demand["FCST (Tons)"].astype(float)

Demand = Demand.groupby(by=["DIVISION", "CATEGORY", "PRODUCT FAMILY", "ITEM DESCRIPTION", "ITEM NO", "DT", "MONTH"], as_index=False).agg({"FCST (Lbs)": np.sum, "FCST (Ea)" : np.sum, "FCST ($)" : np.sum, "FCST (Tons)" : np.sum})

auxSKUS = SKUs.copy()[[SKU, Plant]].groupby(by=SKU, as_index=False).first()

Demand = Demand.merge(auxSKUS, left_on="ITEM NO", right_on=SKU, how="left")
Demand.drop(SKU, axis=1,inplace=True)
demand = Demand[["ITEM NO", "Plant", "DT", "FCST (Lbs)"]]
demand[SafetyStock] = 0
print(demand)

demand = demand.dropna().set_axis([SKU, Plant, Week, DemandAmt, SafetyStock], axis=1)
#extruders = extruders.dropna().set_axis([SKU, Plant, Extruder, Rate], axis=1)
#packlines = packlines.dropna().set_axis([SKU, Plant, Packline, Rate, PlantMinRun, PlantMaxRun], axis=1)
#SKUs = SKUs.dropna().set_axis([SKU, Description, Family, Category, Plant, Costs, InitInv], axis=1)

demand[DemandAmt] = demand[DemandAmt].astype(float)
#demand[Week] = demand[Week].transform(GetCorrectWeekFormat)

print(demand)

#to make sure the format is the same as anylogic's tables.
demandForEXP = demand.copy()[[SKU, Week, Plant, DemandAmt, SafetyStock]]
extrudersForEXP = extruders.copy()
packlinesForEXP = packlines.copy()
SKUsForEXP = SKUs.copy()

demandForEXP.to_excel("demand_testUPD.xlsx",index = False)
extrudersForEXP.to_excel("extruder_testUPD.xlsx", index = False, sheet_name = "db_extruders")
packlinesForEXP.to_excel("extruder_testUPD.xlsx", index = False, sheet_name = "db_packlines")
SKUsForEXP.to_excel("Skus_testUPD.xlsx", index = False)



print("Files read successfully...")



# ------------ create basic index groups and constants------------------- #
Families = SKUs.copy()[[Family]].drop_duplicates().reset_index().drop("index",axis=1)
Products = demand.copy()[[SKU]].drop_duplicates().reset_index().drop("index",axis=1)
Weeks = demand.copy()[[Week]].drop_duplicates().sort_values(by=Week).reset_index().drop("index",axis=1)
aux1 = pd.DataFrame(["2018-00"], columns=[Week])
#aux2 = pd.DataFrame(["2018-53", "2018-54", "2018-55", "2018-56"], columns=[Week])
listofWeeks = ListOfWeeks(53,65)
aux2 = pd.DataFrame(listofWeeks, columns=[Week])
Weeks = aux1.append(Weeks, ignore_index=True)
Weeks = Weeks.append(aux2, ignore_index=True)
Plants = extruders.copy()[[Plant]].drop_duplicates().reset_index().drop("index",axis=1)
ExtCapacity = 144



print ("Basic index groups and constants created...")
# ------------ create family assignation (f_sm)------------- #
FamilyDemand = SKUs.copy()[[SKU, Family]].drop_duplicates()


Families["key"] = 0
Products["key"] = 0
cartesian = Families.merge(Products, how='left', on = 'key')
cartesian.drop('key',1, inplace=True)

family = cartesian.merge(FamilyDemand, left_on=[Family, SKU], right_on = [Family, SKU], how="left", indicator=True)
family["IsFromFamily_sm"] = np.where(family["_merge"] == "both", 1, 0)
family = family.drop("_merge",axis=1)
family = family.set_index([SKU, Family])

print("Family assignation created...")

# ---- create weekly demand amount in Lbs of SKUs (v_sj)---- #


DateDemand = demand.copy()[[SKU, Week, DemandAmt]]
Weeks["key"] = 0
Products["key"] = 0
cartesian = Weeks.merge(Products, on="key", how="left")
cartesian.drop("key", axis=1, inplace=True)

weeklyDemand = cartesian.merge(DateDemand, left_on=[Week, SKU], right_on=[Week, SKU], how="left", indicator=True)

def AverageDemand(skuString):
    ddcopy = weeklyDemand.copy()
    filtDemand = ddcopy[ddcopy[SKU] == skuString][[Week, DemandAmt]]
    filtDemand = filtDemand[filtDemand[Week].transform(WeekToNumber) >= 48][[DemandAmt]]
    filtDemand.fillna(0, inplace=True)
    res = filtDemand.squeeze().mean()
    return res

weeklyDemand["v_sj"] = np.where(weeklyDemand._merge == "both", weeklyDemand[DemandAmt], np.where(weeklyDemand[Week].transform(WeekToNumber) > 52, weeklyDemand[SKU].transform(AverageDemand), 0))
weeklyDemand.drop(DemandAmt, axis=1, inplace=True)
weeklyDemand.drop("_merge", axis=1, inplace=True)
weeklyDemand = weeklyDemand.set_index([SKU, Week])

print("weekly demand amount in Lbs created...")
# ---- decide if a sku can be produced in a plant based on rates (p_sk) ---- #

Plants["key"] = 0

extruders_aux = extruders.copy().groupby(by=[Plant, Extruder], as_index = False).first()
extruders_aux.drop(SKU,axis=1, inplace=True)
extruders_aux.drop(Rate,axis=1,inplace=True)
extruders_aux["key"] = 0

cartesian = Products.merge(extruders_aux, on="key", how="left")
cartesian.drop("key",axis=1,inplace=True)

PlantAvailable = cartesian.merge(extruders, left_on=[SKU, Plant, Extruder], right_on = [SKU, Plant, Extruder], how="left", indicator=True)
PlantAvailable["_merge"] = np.where(PlantAvailable._merge == "both", 1, 0)
PlantAvailable = PlantAvailable.groupby(by=[SKU, Plant], as_index=False).agg({"_merge" : np.sum})

PlantAvailable["p_sk"] = np.where(PlantAvailable._merge > 0, 1, 0)
PlantAvailable.drop("_merge",axis=1,inplace=True)

PlantAvailable = PlantAvailable.set_index([SKU, Plant])

print("Plant availability indicator created...")
# ---- range of weeks that can be produced in advance (r_s) ---- #

Range = Products.copy()
Range["r_s"] = 5
Range.drop("key",axis=1,inplace=True)
Range = Range.set_index(SKU)
print("Range created...")
# ---- starting inventory for each plant and SKU ---- #
StartingInventory = SKUs.copy()[[SKU, InitInv]].set_index([SKU])

print("Starting inventory read...")

# ---- min WOS for each SKU ---- #
MinWOS = Products.copy()
MinWOS["minWOS_s"] = 4
MinWOS.drop("key",axis=1,inplace=True)
MinWOS = MinWOS.set_index(SKU)

print("Min WOS created...")
# ---- min capacity for each family in each plant ---- #
Families["key"] = 0
MinCapacity = Plants.merge(Families, on="key", how="left")
MinCapacity.drop("key",axis=1,inplace=True)
MinCapacity["c_km"] = 100000
MinCapacity = MinCapacity.set_index([Plant, Family])

print("Min Capacity created...")

# ---- Average extrusion rate for sku for each plant (AvgErate_sk) ----#
cartesian = Products.merge(Plants, on="key", how="left")
cartesian.drop("key",axis=1,inplace=True)
ERate = cartesian.merge(extruders, left_on=[SKU, Plant], right_on=[SKU, Plant], how="left")

ERate[Rate].fillna(0, inplace=True)
ERate[Rate] = ERate[Rate].astype(float)
ERate = ERate.groupby(by=[SKU, Plant], as_index=False).agg({Rate : np.mean})
ERate.rename({Rate : "AvgERate_sk"},axis=1,inplace=True)
ERate = ERate.set_index([SKU, Plant])

print("Average extrusion rate created...")

# ---- Average packing rate for sku for each plant (AvgPrate_sk) ----#
cartesian = Products.merge(Plants, on="key", how="left")
cartesian.drop("key",axis=1,inplace=True)
PRate = cartesian.merge(packlines, left_on=[SKU, Plant], right_on=[SKU, Plant], how="left")
PRate.drop([PlantMinRun, PlantMaxRun],axis=1,inplace=True)

PRate[Rate].fillna(0, inplace=True)
PRate[Rate] = PRate[Rate].astype(float)
PRate = PRate.groupby(by=[SKU, Plant], as_index=False).agg({Rate : np.mean})
PRate.rename({Rate : "AvgPRate_sk"},axis=1,inplace=True)
PRate = PRate.set_index([SKU, Plant])

print("Average packing rate created...")

# --- Maximum amount of extrusion hours in each plant (EBottle_k) --- #
extruders_aux = extruders.copy().groupby(by=[Plant, Extruder], as_index = False).first()
extruders_aux.drop(SKU,axis=1, inplace=True)
extruders_aux.drop(Rate,axis=1,inplace=True)

EBottle = extruders_aux.groupby(by=Plant, as_index=False).count()
EBottle["EBottle_k"] = EBottle[Extruder]*ExtCapacity
EBottle.drop(Extruder,axis=1,inplace=True)
EBottle = EBottle.set_index(Plant)
eBottle = EBottle.copy()
print("Extruder bottleneck created...")

# --- Maximum amount of packlines hours in each plant (PBottle_k) --- #
pline_aux = packlines.copy().groupby(by=[Plant, Packline], as_index = False).first()
pline_aux.drop([SKU, Rate, PlantMaxRun, PlantMinRun], axis=1, inplace=True)

PBottle = pline_aux.groupby(by=Plant, as_index=False).count()
PBottle["PBottle_k"] = PBottle[Packline]*ExtCapacity
PBottle.drop(Packline,axis=1,inplace=True)
PBottle = PBottle.set_index(Plant)
pBottle = PBottle.copy()
print("Packline bottleneck created...")


# ------------ version "real" ----------

print("Exporting data...")

Products_list = Products[SKU].to_list()
Weeks_list = Weeks[Week].to_list()
Plants_list = Plants[Plant].to_list()
Families_list = Families[Family].to_list()

EXPORT = ""

def list_to_txt(lst, name):
    res = ''
    i = 0
    for elem in lst:
        res += f'{str(elem)} {str(i)} \n'
        i += 1
    file = open("data/" + f'{name}.txt', 'w')
    file.write(res)
    file.close()

list_to_txt(Products_list, 'Products_list')
list_to_txt(Weeks_list, 'Weeks_list')
list_to_txt(Plants_list, 'Plants_list')
list_to_txt(Families_list, 'Families_list')


# # ----- add parameters -----
# # --- family

EXPORT = ''
for s in Products_list:
    for m in Families_list:
        EXPORT += f'"{s}", "{m}", {family.squeeze().loc[(s,m)]}\n'
file = open('data/f.txt', 'w')
file.write(EXPORT)
file.close()

# # --- weeklyDemand

EXPORT = ''
for s in Products_list:
    for j in Weeks_list:
        EXPORT += f'"{s}", "{j}", {weeklyDemand.squeeze().loc[(s,j)]} \n'
file = open('data/v.txt', 'w')
file.write(EXPORT)
file.close()

# # --- plantAvailable
EXPORT = ''
for s in Products_list:
    for k in Plants_list:
        EXPORT += f'"{s}", "{k}", {PlantAvailable.squeeze().loc[(s,k)]} \n'
file = open('data/p.txt', 'w')
file.write(EXPORT)
file.close()

# # --- Range
EXPORT = ''
for s in Products_list:
    EXPORT += f'{s}, {Range.squeeze().loc[(s)]} \n'
file = open('data/r.txt', 'w')
file.write(EXPORT)
file.close()

# # --- StartingInventory
EXPORT = ''
for s in Products_list:
    EXPORT += f'"{s}", {StartingInventory.squeeze().loc[(s)]} \n'
file = open('data/initInv.txt', 'w')
file.write(EXPORT)
file.close()


# # --- MinWos
EXPORT = ''
for s in Products_list:
    EXPORT += f'"{s}", {MinWOS.squeeze().loc[(s)]} \n'
file = open('data/minWOS.txt', 'w')
file.write(EXPORT)
file.close()

# # --- MinCapacity
EXPORT = ''
for k in Plants_list:
    for m in Families_list:
        EXPORT += f'"{k}", "{m}", {MinCapacity.squeeze().loc[(k,m)]} \n'
file = open('data/c.txt', 'w')
file.write(EXPORT)
file.close()


# # --- ERate
EXPORT = ''
for s in Products_list:
    for k in Plants_list:
        EXPORT += f'"{s}", "{k}", {ERate.squeeze().loc[(s,k)]} \n'
file = open('data/AvgERate.txt', 'w')
file.write(EXPORT)
file.close()

# # --- EBottle
EXPORT = ''
for k in Plants_list:
    EXPORT += f'"{k}", {eBottle.squeeze().loc[(k)]} \n'
file = open('data/EBottle.txt', 'w')
file.write(EXPORT)
file.close()

# # --- PRate
EXPORT = ''
for s in Products_list:
    for k in Plants_list:
        EXPORT += f'"{s}", "{k}", {PRate.squeeze().loc[(s,k)]} \n'
file = open('data/AvgPRate.txt', 'w')
file.write(EXPORT)
file.close()

# # --- PBottle
EXPORT = ''
for k in Plants_list:
    EXPORT += f'"{k}", {pBottle.squeeze().loc[(k)]} \n'
file = open('data/PBottle.txt', 'w')
file.write(EXPORT)
file.close()


# # --- WeekNumber
# EXPORT = ''
# i = 0
# week_to_number = {}
# for j in Weeks_list:
    # EXPORT += f'{j}, {i} \n'
    # week_to_number[j] = i
    # i += 1
# file = open('data/Weeks_list.txt', 'w')
# file.write(EXPORT)
# file.close()

# # -- SafetyStock

def CalcSafetyStock(s,j): #s string product, j number of week
    if j==len(Weeks_list) - len(listofWeeks) - 1:
        return CalcSafetyStock(s, j-1)
    res = 0
    counter = 0
    for i in range(len(Weeks_list)):
        if i>=j+1 and i<=j+4 and i <= (len(Weeks_list) - len(listofWeeks) - 1):
            counter += 1
            res += weeklyDemand.squeeze().loc[(s,Weeks_list[i])]* MinWOS.squeeze().loc[(s)]
    return (res/counter)
    # return "sum <i> in JNum with i >= " + str(j) + " and i <= " + str(j) + "+3: v[\"" + s + "\",weekNumber[i]]" 

EXPORT = ''
ss_dict = {}
ss_max = 0
for s in Products_list:
    for j in range(len(Weeks_list) - len(listofWeeks)):
        ss_dict[(s,j)] = CalcSafetyStock(s,j)
        if ss_dict[(s,j)] > ss_max:
            ss_max = ss_dict[(s,j)]
        EXPORT += f'"{s}", {j}, {ss_dict[(s,j)]} \n'
file = open('data/SafetyStock.txt', 'w')
file.write(EXPORT)
file.close()

print("Done!")

# c_max = MinCapacity.squeeze().max()
# EXPORT = str(c_max) + '\n' + str(ss_max)
# file = open('Constants.txt', 'w')
# file.write(EXPORT)
# file.close()
