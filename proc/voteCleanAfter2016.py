# must be executed in its directory or at least outside raw/
import csv
import os
import sys
import numpy as np
import pandas as pd
import re

path = sys.argv[1] # argv[0] is filename
votename = sys.argv[2] # president
voteid = sys.argv[3] # 201801
year = voteid[0:4]

to_path = re.sub("raw/.*", "proc/", path)
to_path = to_path + year + "/" + votename + "/"
if not os.path.exists(to_path):
    os.makedirs(to_path)

# elbase.csv

# Some datasets were modified and renames as format like: elbase_P1.to_csv
# Check the name first
basefile = "elbase.csv"
if not os.path.exists(path+basefile):
    for filename in os.listdir(path):
        if re.match("elbase", filename):
            basefile = filename

# Columns:
# 省市, 縣市, 選區, 鄉鎮市區, 村里, 名稱
base_names = ["provinceID", "cityID", "districtID", "townID", "villageID", "name"]
base_raw_df = pd.read_csv(path+basefile, header = None, names = base_names, dtype = str)
base_raw_df = base_raw_df.replace(r"'", "", regex=True)

high_level_df = base_raw_df[base_raw_df.villageID == "0000"]

# town
town_df = high_level_df.drop("villageID", axis = 1)
base_df = pd.merge(base_raw_df, town_df, \
on = ["provinceID", "cityID", "districtID", "townID"], \
suffixes = ("Village","Town"), how = "left")
# district
district_df = high_level_df[high_level_df["townID"] == "000"].drop(["villageID", "townID"], axis = 1)
base_df = pd.merge(base_df, district_df, \
on = ["provinceID", "cityID", "districtID"], \
suffixes = ("","District"), how = "left")
# city
city_df = high_level_df[(high_level_df["districtID"] == "00") & (high_level_df["townID"] == "000")] \
.drop(["villageID", "townID", "districtID"], axis = 1)
base_df = pd.merge(base_df, city_df, \
on = ["provinceID", "cityID"], \
suffixes = ("","City"), how = "left")

# When there is no distrct differences within city,
# name of district column will be only "name" not "nameDistrict"
# to unify the names, change it as "nameDistrict"
base_df = base_df.rename(columns={"name": "nameDistrict"})

base_df = base_df.assign(id = lambda x: x.provinceID + x.cityID + x.townID + x.villageID)
base_df.id = base_df.id.str[0:8]+base_df.id.str[9:12]
base_df = base_df.assign(voteID = voteid)

id_df = base_df[["provinceID", "cityID", "districtID", "townID", "villageID", "id", "voteID"]]

base_df = base_df[base_df.villageID != "0000"]
base_df = base_df.assign(oldID = "")
base_output_names = ["provinceID", "cityID", "districtID", "townID", "villageID", \
"nameVillage", "nameTown", "nameDistrict", "nameCity", "oldID", "voteID", "id"]

base_df[base_output_names].to_csv(to_path+"elbase.csv", index=False)

# elcand.csv
candfile = "elcand.csv"
if not os.path.exists(path+candfile):
    for filename in os.listdir(path):
        if re.match("elcand", filename):
            candfile = filename
# Columns:
# 省市, 縣市, 選區, 鄉鎮市區, 村里, 號次, 名字, 政黨代號, 性別, 出生日期, 年齡, 出生地, 學歷,
# 現任, 當選註記, 副手
cand_names = ["provinceID", "cityID", "districtID", "townID", "villageID", "no",
"name", "partyID", "gender", "birthday", "age", "birthCity", "education", "isCurrent",
"isElected", "vice"]
cand_raw_df = pd.read_csv(path+candfile, header = None, names = cand_names, dtype = str)
cand_raw_df = cand_raw_df.replace(r"'", "", regex=True)

dist = base_df.districtID.drop_duplicates()
if next(iter(dist), 'x') == "00":
    cand_raw_df.districtID = "00"

cand_df = pd.merge(cand_raw_df, id_df, how = "left")
cand_df.to_csv(to_path+"elcand.csv", index=False)

# elctks.csv
cktsfile = "elctks.csv"
if not os.path.exists(path+cktsfile):
    for filename in os.listdir(path):
        if re.match("elctks", filename):
            cktsfile = filename
# Columns:
# 省市, 縣市, 選區, 鄉鎮市區, 村里, 投開票所, 候選人號次, 得票數, 得票率, 當選註記
ckts_names = ["provinceID", "cityID", "districtID", "townID", "villageID", "pollStationID",
"no", "vote", "votePercentage", "isElected"]
ckts_raw_df = pd.read_csv(path+cktsfile, header = None, names = ckts_names, dtype = str)
ckts_raw_df = ckts_raw_df.replace(r"'", "", regex=True)

if next(iter(dist), 'x') == "00":
    ckts_raw_df.districtID = "00"

ckts_df = pd.merge(ckts_raw_df, id_df, how = "left")
ckts_df.to_csv(to_path+"elckts.csv", index=False)

# elpaty.csv
# 政黨代號, 政黨名稱
# paty_names = ["partyID", "partyName"]

# elprof.csv
proffile = "elprof.csv"
if not os.path.exists(path+proffile):
    for filename in os.listdir(path):
        if re.match("elprof", filename):
            proffile = filename
# Columns:
# 省市, 縣市, 選區, 鄉鎮市區, 村里, 投開票所, 有效票, 無效票, 投票數, 選舉人數, 人口數, 候選人合計,
# 當選人數合計, 候選人數男, 候選人數女, 當選人數男, 當選人數女, 選舉人數對人口數, 投票數對選舉人數,
# 當選人數對候選人數
prof_names = ["provinceID", "cityID", "districtID", "townID", "villageID", "pollStationID",
"validVote", "invalidVote", "totalVotes", "voters", "population", "totalCandidates",
"totalElected", "maleCandidates", "femaleCandidates", "maleElected", "femaleElected",
"votersOverPopulation", "votesOverVoters", "electedOverCandidates"]
prof_raw_df = pd.read_csv(path+proffile, header = None, names = prof_names, dtype = str)
prof_raw_df = prof_raw_df.replace(r"'", "", regex=True)

if next(iter(dist), 'x') == "00":
    prof_raw_df.districtID = "00"

prof_df = pd.merge(prof_raw_df, id_df, how = "left")
prof_df.to_csv(to_path+"elprof.csv", index=False)
