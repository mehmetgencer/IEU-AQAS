#!/usr/bin/python3
from dash import Dash, html, dcc, Input, Output, State, callback # pyright: ignore[reportMissingImports]
import dash_ag_grid as dag # pyright: ignore[reportMissingImports]
import plotly.express as px # pyright: ignore[reportMissingImports]
import plotly.graph_objs as go # pyright: ignore[reportMissingImports]
import json, pprint
import pandas as pd
import numpy
from pathlib import Path
from settings import *
import evidencelibSimple, courselib
from settings import *
import evidencelibSimple



app = Dash(server=False,routes_pathname_prefix=f"{localsettings['route_prefix']}/program_level/")
#app = Dash(server=False,routes_pathname_prefix=f"/program_level/")
app.layout = html.Div([
    html.A(href=localsettings["route_prefix"],children=html.H1(children='IEU İşletme AQAS-Go to main menu', style={'textAlign':'center'})),
    dcc.Input(
            id="passwd",
            type="password",
            placeholder="Enter password here",
        ),
    dcc.Dropdown(dict((d,d) for d in courses.keys()),None , id='dropdown-departments',disabled=True),
    dcc.Dropdown([],None,id='dropdown-courses',disabled=True),
    html.H2(children='1 - Curriculum level evaluation'), 
    html.Div(id="curriculum-eval-output",children="Program seçin..."),
    html.H2(children='2 - Evidence based evaluation'), 
    html.Div(id="evidence-eval-output",children="Program seçin..."),
])

@app.callback(
    Output('dropdown-departments', 'disabled'),
    Output('dropdown-courses', 'disabled'),
    Input('passwd', 'value'),
)
def checkpass_and_enable(value):
    print("Checking passwd")
    if not checkpasswd(value):
        print("Enabling")
        return True,True
    print("NOT Enabling")
    return False,False

@app.callback(
    Output('dropdown-courses', 'options'),
    Input('dropdown-departments', 'value')
)
def update_courselist_dropdown(department):
    print("Department selected:",department)
    if not department:return []
    opts = [{'label':"Tüm dersler", 'value':"Tüm dersler"}]+[{'label':opt, 'value':opt} for opt in courses[str(department)]]
    return opts

@app.callback(
    Output('curriculum-eval-output', 'children'),
    Input('dropdown-departments', 'value'),
    Input("dropdown-courses","value"),
    prevent_initial_call=True,
)
def show_curriculum_eval(department,course):
    #curriculum sum
    total=None
    if course and not course=="Tüm dersler":courselist=[course]
    else:courselist=courses[department]
    for course in courselist:
        #print("Adding course:",course)
        tmpcontrib=courselib.total_pocontrib(department,course)
        #print("total contrib:",tmpcontrib)
        if tmpcontrib<=0:
            print(f"zero contrib: {course}")
            continue
        znorm=courselib.get_pocontrib_from_sylabus(department,course,normalize=True,as_vector=True)
        if total is None:total=znorm
        else:total=total+znorm
    fig = go.Figure(data=[go.Bar(
        orientation="h",
        y=list(range(1,len(total)+1)), 
        x=total)])
    tmp=dcc.Graph(
            figure=fig
        )
    return [f"Total contributions  to program outcomes (according to syllabi). Courses contributing:{courselist}",tmp]

@app.callback(
    Output('evidence-eval-output', 'children'),
    Input('dropdown-departments', 'value'),
    Input("dropdown-courses","value"),
    prevent_initial_call=True,
)
def show_evidence_based_eval(department, course):
    if course and not course=="Tüm dersler":courselist=[course]
    else:courselist=courses[department]
    ed=evidencelibSimple.get_evidence_data(department=localsettings["department_full_names"][department])
    courseAverages=[]
    courseCodes=[]
    total=None
    noGradeCourses=[]
    for course in courselist:
        ced=ed[ed.course==course]
        if courselib.total_pocontrib(department,course)<=0:
            print(f"zero contrib: {course}")
            continue
        if not ced.grade.mean()>0:
            print(f"No grade for course: {course}, mean grade:{ced.grade.mean()}")
            noGradeCourses.append(course)
            continue
        znorm=courselib.get_pocontrib_from_sylabus(department,course,normalize=True,as_vector=True)
        print(f"Mean: {ced.grade.mean()}, znorm: {znorm}, mult:{numpy.multiply(ced.grade.mean(),znorm)}")
        if total is None:total=numpy.multiply(ced.grade.mean()/100.,znorm)
        else:total=total+numpy.multiply(ced.grade.mean()/100.,znorm)
        courseCodes.append(course)
        courseAverages.append(ced.grade.mean()/100)
    fig1 = go.Figure(data=[go.Bar(
        orientation="h",
        y=courseCodes, 
        x=courseAverages)])
    gr1=dcc.Graph(
            figure=fig1
        )
    print(f"Total: {total}")
    fig2 = go.Figure(data=[go.Bar(
        orientation="h",
        y=list(range(1,len(total)+1)), 
        x=total)])
    gr2=dcc.Graph(
            figure=fig2
        )
    return (f"Courses considered: {courselist}\n These courses have no grade data: {noGradeCourses}\nAverage grades in courses:",
            gr1,
            "Average achievement of program outcomes:",gr2)