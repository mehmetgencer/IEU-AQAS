"""
This file implements 'singleTotal' evidence scheme only.

In addition the scheme in this library skips POcontrib computations (from A-to-LO then LO-to-PO) 
and instead uses the POcontrib values declared in cour syllabi.
"""
import pandas as pd
from pathlib import Path
from settings import *

def _simplify_column_name(x):
    return x.split("_")[0].replace(" ","").replace(".","")

def get_evidence_data(department=None, course=None):
    """
    Read evidence table, filter for department and course if needed
    """
    fname=Path(storage)/"evidence"/localsettings["evidence_single_filename"]
    retval = pd.read_excel(fname)
    colnames=[_simplify_column_name(x) for x in retval.columns]
    print("Simplified column names:",colnames)
    retval.columns=colnames
    retval=retval[["ÖğrenciNo","ÖğrenciProgramı","DKodu","Ort","Harf"]]
    retval.columns=["student_id","program","course","grade","letter_grade"]
    if department:
        if course:
            retval=retval[retval.program==department&retval.course==course]
        else:
            retval=retval[retval.program==department]
    return retval
