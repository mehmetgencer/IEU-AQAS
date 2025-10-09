#!/usr/bin/python3

import sys, os, json, pprint
from pathlib import Path
import numpy
import pandas as pd
from settings import *

def total_pocontrib(department,course):
    tmp=get_pocontrib_from_sylabus(department,course,as_vector=True)
    #del tmp["ects"]
    #print("Summing vector:",tmp)
    return sum(tmp)

def get_pocontrib_from_sylabus(department,course,normalize=False,as_vector=False):
    """
    Normalize: so that toal contrib is equal to course ECTS
    vector: return as a list rather than a dict
    """
    fname=course+".json"
    retvaltmp= json.load(open(Path(storage)/"pocontrib-in-syllabus"/department/fname,"r"))
    #print("Loaded pocontrib:",retvaltmp)
    ects=retvaltmp["ects"]
    del retvaltmp["ects"]
    retval={}
    for k,v in retvaltmp.items():retval[int(k)]=v
    retval_vec=[retval[i+1] for i in range(len(retval))]
    if normalize:
        factor=ects/sum(retval_vec)
        if as_vector:
            return numpy.multiply(factor,retval_vec)
        else:
            retval_norm={}
            for i in range(len(retval)):
                retval_norm[i+1]=factor*retval[i+1]
            return retval_norm
    else:
        if as_vector:return retval_vec
        return retval

def get_alo(department,course):
    """
    Returns a tuple: activity weights (pandas series, nulls replaced with zeros, weights in range 0-1), and
    activity-to-learning-outcome matrix (pandas data frame, nulls replaced with zeros)
    """
    fname=Path(storage)/"a-to-lo"/department/f"{course}.csv"
    df=pd.read_csv(fname)
    df.fillna(0, inplace=True)
    activity_weights=df["Weighting"]/100
    alo=df.iloc[:,3:]
    return activity_weights,alo

def get_lopo(department,course):
    """
    Gets LO-to-PO matrix.
    """
    fname=Path(storage)/"lo-to-po"/department/f"{course}.csv"
    df=pd.read_csv(fname)
    df.fillna(0, inplace=True)
    return(df.iloc[:,1:])

def get_course_contrib_to_po(department,course,normalize=True):
    """
    Returns znorm
    """
    activity_weights,alo=get_alo(department,course)
    lopo=get_lopo(department,course)
    tmp1=numpy.matmul(activity_weights,alo)
    #print("ALO",activity_weights,alo)
    #print("LOPO",lopo)
    #print("TMP1:",numpy.asmatrix(tmp1))
    tmp2=numpy.matmul(numpy.asmatrix(tmp1),lopo)
    #print("TMP2:",tmp2)
    pocontrib=tmp2
    if normalize:
        fname=course+".json"
        retvaltmp= json.load(open(Path(storage)/"pocontrib-in-syllabus"/department/fname,"r"))
        ects=retvaltmp["ects"]
        pocontrib=pocontrib*(ects/total_pocontrib(department,course))
    return pocontrib

def get_total_po_support(department):
    courselist=courses[department]
    total=None
    zero_contrib_courses=[]
    for course in courselist:
        tmpcontrib=total_pocontrib(department,course)
        #print("total contrib:",tmpcontrib)
        if tmpcontrib<=0:
            print(f"zero contrib: {course}")
            zero_contrib_courses.append(course)
            continue
        znorm=get_course_contrib_to_po(department,course)
        if total is None:total=znorm
        else:total=total+znorm
    return total

if __name__=="__main__":
    #print(get_pocontrib_from_sylabus("dba","BUS 210",normalize=True,as_vector=True))
    #print(get_alo("dba","BUS 210"))
    #print(get_lopo("dba","BUS 210"))
    print("POcontrib return val:",get_course_contrib_to_po("dba","BUS 210"))
    print("TOTAL PO SUPPORT for dba:",get_total_po_support("dba"))