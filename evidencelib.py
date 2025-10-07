#!/usr/bin/python3

import sys, os, json, pprint, glob
from pathlib import Path
import click
import pandas as pd
from settings import *

def make_path_pattern( department, course,pattern):
    """
    Helper function that makes a glob pattern for file listing, using '*'s in place of department and course if they are empty
    User provided 'pattern' is appended at the end
    """
    tmp=Path(storage)/"evidence"
    pattern="*.xlsx"
    if department: 
        tmp=tmp/department
        if course: tmp=tmp/course
        else:pattern="*/"+pattern
    else:
        pattern="*/*/"+pattern
    return tmp,pattern

def require_department_and_course(department, course):
    if not department or not course:raise Exception("Department and course must be provided for this command")

def list_evidence( department, course):
    """
    Helper function that returns a list of evidence file paths for given course
    """
    tmp,pattern=make_path_pattern( department, course,"*.xlsx")
    print("Listing:",tmp)
    evidence_files=[x for x in tmp.glob(pattern)]
    for x in evidence_files: print(x)
    return evidence_files

def has_evidence( department, course):
    tmp=list_evidence( department, course)
    if tmp:return True
    else:return False

def get_evidence( department, course):
    """
    Read and return -only- the first evidence excel file as a pandas data frame. 
    Use with caution: there may be more than one evidence file. Merging them is probably a better option!
    """
    tmp=list_evidence( department, course)
    if not tmp:return None
    else: return pd.read_excel(tmp[0])

def get_matchscheme_path( department, course):
    """
    Helper function to create a path to _matchscheme.json file for the course
    """
    return str(Path(storage)/"evidence"/department/course/"_matching.json")

def get_matchscheme( department, course):
    """
    Read the _matching.json file for a course and return it as a dictionary
    """
    tmp=Path(storage)/"evidence"/department/course/"_matching.json"
    if os.path.exists(tmp):
        retval=json.load(open(tmp,"r"))
        pprint.pp(retval)
        return retval
    else:
        return None
    
def get_crude_matchscheme(department, course):
    """
    Build and return a crude matchscheme for the course
    """
    df=get_alo_matrix( department, course)
    ids=list(df["ID"].dropna().astype(int).unique())
    return {
        "Total": {"from":[-1],"to":ids}
    }

def has_matchscheme( department, course):
    """
    Return true if course has a _matching.json file
    """
    tmp=get_matchscheme( department, course)
    if tmp is not None:return True
    else: return False

def get_alo_matrix( department, course):
    """
    Return the course's A-LO matrix as a pandas data frame or throw an exception if it does not exist
    """
    require_department_and_course(department, course)
    fname=course+".csv"
    df=pd.read_csv(Path(storage)/"a-to-lo"/department/fname)
    return df

def check_match_scheme( department, course,check_evidence=False):
    """
    Checks if matching scheme uses all assessment activities in syllabus and maps all grades in evidence file(s) to some activity 
    (latter if check_evidence is "true").
    if check_evidence is true then evidence files are opened, number of columns checked to match in all, and 
    column ids's are checked, i.e if all grades in evidence file(s) are mapped to some activity.
    The return value is a dictionary
    """
    require_department_and_course(department, course)
    ms=get_matchscheme( department, course)
    if not ms:
        if localsettings["matchschemeSearchStrategy"]=="defaultToCrude":
             ms=get_crude_matchscheme( department, course)
             print("Defaulting to crude match scheme:", ms)
        else:
            return False, "No match scheme"
    df=get_alo_matrix( department, course)
    print("MATCH SCHEME:")
    pprint.pp(ms)
    ids=list(df["ID"].dropna().astype(int).unique())
    anames=["%s (ID:%d)"%(row["Activity"],row["ID"]) for index,row in df.query("ID==ID").iterrows()] #since NaN==NaN is false!
    print("IDs",ids,anames)
    usedids=[x for il in ms.values() for x in il["to"]]
    print("Used ids",usedids)
    retval={}
    retval["IDs_unevidenced"]=list(set(ids)-set(usedids))
    retval["IDs_nonexistent"]=list(set(usedids)-set(ids))
    retval["evidences_inconsistent"]=None
    retval["evidences_unmatched"]=None
    retval["evidences_nonexistent"]=None
    print("Check evidence",check_evidence)
    if check_evidence:
        numcol=None
        ncmap={}
        problems=False
        for fname in list_evidence( department, course):
            print("will read evidence",fname)
            df=pd.read_excel(fname)
            evnames=[x.split("_")[0].replace(' ', '') for x in df.columns[5:-3]]
            #df.columns = df.columns.str.replace(' ', '')
            ncmap[str(fname)]=(len(df.columns)-8,evnames)
            if numcol is None:
                numcol=len(df.columns)
            else:
                if numcol!=len(df.columns):
                    print("Number of columns %d is different from earlier %d"%(len(df.columns),numcol))
                    problems=True
        if problems:
            retval["evidences_inconsistent"]=ncmap
        if numcol is not None:
            print("Numcol",numcol)
            cols=list(range(1,numcol-7))
            print("cols",cols)
            usedevidences=[x for il in ms.values() for x in il["from"]]
            retval["evidences_unmatched"]=list(set(cols)-set(usedevidences))
            retval["evidences_nonexistent"]=list(set(usedevidences)-set(cols))
    print("RETVAL")
    pprint.pp(retval)
    return True, retval

@click.command()
@click.option("--command", default="help", help="Give help")
@click.option("--department", default="")
@click.option("--course", default="")
def rootcmd(command,  department, course):
    """
    evidencelib.py --command <command>  ... --department=... --course=...
    Runs given command:
        list : List evidence
        get-match-scheme: check if match scheme exists and return it
        check-match-scheme: check if match scheme exists and have any errors
        check-evidence-structure: check if evidence structure is compatible with match-scheme
    """
    if command=="help":
        print(rootcmd.__doc__)
    elif command=="list":
        retval=list_evidence(department,course)
    elif command=="get-match-scheme":
        retval=get_matchscheme(department,course)
        if not retval:print("No match scheme found for departmen-course")
    elif command=="check-match-scheme":
        status,retval=check_match_scheme(department,course,check_evidence=False)
        if not status:print("Check failed or not found")
    elif command=="check-evidence-structure":
        status,retval=check_match_scheme(department,course,check_evidence=True)
        if not status:print("Check failed or not found")
    else:
        print("Unknown command:",command)
if __name__ == '__main__':
    rootcmd()