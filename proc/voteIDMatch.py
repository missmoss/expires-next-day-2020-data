# must be executed in its directory or at least outside raw/
import csv
import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import re

path = sys.argv[1] # argv[0] is filename
votename = sys.argv[2] # president
voteid = sys.argv[3] # 201801
id_match_path = "../data/vote/proc/"
matchfile = "id_match.csv"
pattern = "縣|市|區|鄉|鎮|村|里$"

year = int(voteid[0:4])

# elbase.csv

# Some datasets were modified and renames as format like: elbase_P1.to_csv
# Check the name first
basefile = "elbase.csv"
if not os.path.exists(path+basefile):
    for filename in os.listdir(path):
        if re.match("elbase", filame):
            basefile = filename
            if voteid == "200401":
                basefile = "elbase20160523.csv"

# Columns:
# 省市, 縣市, 選區, 鄉鎮市區, 村里, 名稱
base_names = ["provinceID", "cityID", "districtID", "townID", "villageID", "name"]
base_raw_df = pd.read_csv(path+basefile, header = None, names = base_names, dtype = str)
base_raw_df = base_raw_df.replace(r"'", "", regex=True)
base_raw_df = base_raw_df.replace(" ", "", regex=True)
# for 200501 only
if voteid == "200501":
    base_raw_df.districtID = "00"
if voteid == "200401":
    lost_data = [["03","018","00","014","0000","峨眉鄉"], \
    ["03","018","00","015","0000","尖石鄉"], \
    ["03","018","00","016","0000","五峰鄉"]]
    base_raw_df = base_raw_df.append(pd.DataFrame(lost_data, columns=base_raw_df.columns))

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

base_df = base_df.assign(oldID = lambda x: x.provinceID + x.cityID + x.townID + x.villageID)
base_df.oldID = base_df.oldID.str[0:8]+base_df.oldID.str[9:12]
base_df = base_df.assign(voteID = voteid)

oldid_df = base_df[["provinceID", "cityID", "districtID", "townID", "villageID", "oldID", "voteID"]]

base_df = base_df[base_df.villageID != "0000"]
base_df2 = base_df.assign(trimVillage = base_df.nameVillage.str.slice(stop=3))
base_df2 = base_df2.assign(names = lambda x: x.nameCity + x.nameTown + x.trimVillage)

id_match_df = pd.DataFrame(columns = ["id", "names", "voteID"])
if os.path.exists(id_match_path+matchfile):
    id_match_raw_df = pd.read_csv(id_match_path+matchfile, dtype = str)
    id_match_df = pd.merge(base_df2, id_match_raw_df, on = ["names"], suffixes = ("_base", "_id"), how = "left")
    no_match_df = id_match_df[id_match_df.id.isnull()]
    # check town upgrade
    no_match_agg_df = no_match_df.groupby(["nameTown"]).count() \
    .sort_values(by=["villageID"], ascending = False)
    if no_match_agg_df.reset_index().at[0, "villageID"] > 10:
        if year <= 2008:
            id_match_raw_df.names = id_match_raw_df.names.str.replace("新北市", "臺北縣")
            # for 200801 only
            # id_match_raw_df.names = id_match_raw_df.names.str.replace("臺西鄉", "台西鄉")
            # id_match_raw_df.names = id_match_raw_df.names.str.replace("臺東市", "台東市")
        id_match_df = id_match_raw_df
        id_match_df = id_match_df.assign(trimNames = id_match_df.names.replace(pattern, "", regex=True))
        no_match_df = no_match_df.assign(trimNames = no_match_df.names.replace(pattern, "", regex=True))
        id_match_df = pd.merge(no_match_df, id_match_df, on = ["trimNames"], suffixes = ("_no", "_id2"), how = "left")
        no_match_df = id_match_df[id_match_df.id_id2.isnull()]
        id_match_df = id_match_df[id_match_df.id_id2.notnull()]
        id_match_df = id_match_df[["id_id2", "names_no", "voteID_base"]] \
        .rename(columns = {"id_id2": "id", "names_no": "names", "voteID_base": "voteID"}) \
        .sort_values(by=["id", "names", "voteID"], ascending = False)
        id_match_df.to_csv(id_match_path+matchfile, index = False, header = False, mode = "a")

    no_match_df.to_csv(id_match_path+"check/no_match_"+voteid+".csv", index = False)
    # 2014 only
    # check names consistent
    # no = pd.merge(no_match_df, id_match_raw_df, left_on = ["oldID"], right_on = ["id"])
    # no[["oldID", "names_x", "names_y"]].to_csv(id_match_path+"check_"+voteid+".csv", index = False)
    # copy/paste
    # no = pd.merge(no_match_df, id_match_raw_df, left_on = ["oldID"], right_on = ["id"])
    # no[["oldID", "names_x"]].to_csv(id_match_path+"check_"+voteid+".csv", index = False)
else:
    # read newid data
    newbasefiles = ["../data/vote/proc/2016/president/elbase.csv", \
    "../data/vote/proc/2018/direct_city_mayor/elbase.csv", \
    "../data/vote/proc/2018/city_mayor/elbase.csv"]

    newbase_names = ["provinceID", "cityID", "districtID", "townID", "villageID", \
    "nameVillage", "nameTown", "nameDistrict", "nameCity", "id", "voteID"]

    newbase_df = pd.DataFrame(columns = newbase_names)
    for basefile in newbasefiles:
        tmp_df = pd.read_csv(basefile, dtype = str)
        newbase_df = pd.concat([newbase_df, tmp_df])

    new_df = newbase_df[["id", "voteID", "nameCity", "nameTown", "nameVillage"]]
    new_df = new_df.assign(trimVillage = new_df.nameVillage.str.slice(stop=3))
    new_df = new_df.assign(names = lambda x: x.nameCity + x.nameTown + x.trimVillage)
    new_df2 = new_df.drop_duplicates(subset=["id", "trimVillage"])
    # id is not unique in new_df2 because there are "same character differenct writings" issues
    # in the datasets
    # the duplicate ids are:
    # 10009010018 雲林縣斗六市崙"峯"里 雲林縣斗六市崙"峰"里
    # 10009160001 雲林縣臺西鄉"台"西村 雲林縣臺西鄉"臺"西村
    # 10014030005 臺東縣關山鎮里""里 臺東縣關山鎮里"壠"里
    # 65000030054 新北市中和區灰"瑤"里 新北市中和區灰"磘"里
    # 65000120027 新北市瑞芳區"濂"新里 新北市瑞芳區"濓"新里
    # 65000120028 新北市瑞芳區"濂"洞里 新北市瑞芳區"濓"洞里
    # 67000070004 臺南市麻豆區"晉"江里 臺南市麻豆區"晋"江里
    # I'll keep both writings for better match

    id_match_df = pd.merge(base_df2, new_df2, on = ["names"], suffixes = ("Old", "New"), how = "outer")
    no_match_df = id_match_df[id_match_df.id.isnull()]
    no_match_df.to_csv(id_match_path+"no_match_"+voteid+".csv", index = False)
    id_match_df = id_match_df[id_match_df.id.notnull()]
    id_match_df = id_match_df[["id", "names", "voteIDNew"]] \
    .rename(columns = {"voteIDNew": "voteID"}) \
    .sort_values(by=["id", "names", "voteID"], ascending = False)
    id_match_df.to_csv(id_match_path+matchfile, index = False, mode = "w")
