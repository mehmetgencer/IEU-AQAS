import json
from pathlib import Path

localsettings ={
    "route_prefix":"/ieuaqas",
    "storage": "data",
    "matchschemeSearchStrategy":"defaultToCrude",
    "excel_decimal":",",
    "evidence_scheme":"singleTotal",
    "evidence_single_filename":"grades.xlsx",
    "department_full_names":{"dba":"İşletme",
                             "itf":"Uluslararası Ticaret ve Finansman",
                             "dlm":"Lojistik Yönetimi",
                             "eco":"Ekonomi",
                             "ireu":"Siyaset Bilimi ve Uluslararası İlişkiler"
                             }
}
storage=localsettings["storage"]
courses=json.load(open(Path(localsettings["storage"])/"courselist.json","r"))
departments=list(courses.keys())
program_outcomes=json.load(open(Path(localsettings["storage"])/"pos.json","r"))

def checkpasswd(token,username=None):
    return token in ["111"]