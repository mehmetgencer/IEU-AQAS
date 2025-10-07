#!/usr/bin/python3

import sys, os, json, pprint
from pathlib import Path
import numpy
from settings import *

def total_pocontrib(department,course):
    tmp=get_pocontrib_from_sylabus(department,course,as_vector=True)
    #del tmp["ects"]
    #print("Summing vector:",tmp)
    return sum(tmp)

def get_pocontrib_from_sylabus(department,course,normalize=False,as_vector=False):
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

if __name__=="__main__":
    print(get_pocontrib_from_sylabus("dba","BUS 210",normalize=True,as_vector=True))