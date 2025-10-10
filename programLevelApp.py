#!/usr/bin/python3
import base64
from dash import Dash, html, dcc, Input, Output, State, callback # pyright: ignore[reportMissingImports]
import dash_ag_grid as dag # pyright: ignore[reportMissingImports]
import plotly.express as px # pyright: ignore[reportMissingImports]
import plotly.graph_objs as go # pyright: ignore[reportMissingImports]
import json, pprint, os, time
import pandas as pd
import numpy
from pathlib import Path
from settings import *
import evidencelibSimple, courselib
from settings import *
import evidencelibSimple


gfilepath=Path(storage)/"evidence"/localsettings["evidence_single_filename"]
gfile_mod_time = None
if  os.path.exists(gfilepath):
    gfile_mod_time = os.path.getmtime(gfilepath)

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
    html.H2(children='1 - Evaluation based on course syllabi'), 
    html.Div(id="curriculum-eval-output",children="Program seçin..."),
    html.H2(children='2 - Evaluation based on student grades'), 
    dcc.Upload(
        id='upload-grades',
        children=html.Div([
            "'Drag and Drop' or ",
            html.A('click here to upload student grades file'+f'{" (one already exists and was uploaded on "+time.ctime(gfile_mod_time)+")" if gfile_mod_time is not None else ""}')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        #multiple=True
    ),
    html.Div(id='upload-grades-status'),
    html.Br(),
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
    zero_contrib_courses=[]
    if course and not course=="Tüm dersler":courselist=[course]
    else:courselist=courses[department]
    for course in courselist:
        #print("Adding course:",course)
        tmpcontrib=courselib.total_pocontrib(department,course)
        #print("total contrib:",tmpcontrib)
        if tmpcontrib<=0:
            print(f"zero contrib: {course}")
            zero_contrib_courses.append(course)
            continue
        znorm=courselib.get_pocontrib_from_sylabus(department,course,normalize=True,as_vector=True)
        if total is None:total=znorm
        else:total=total+znorm
    fig = go.Figure(data=[go.Bar(
        #meta={"title":"Evaluation based on syllabi", "xaxis_title":"Level of support", "yaxis_title":"Program outcome no"},
        orientation="h",
        y=list(range(1,len(total)+1)), 
        x=total)])
    tmp=dcc.Graph(
            figure=fig
        )
    return [f"Total contributions  to program outcomes for department: {department}(according to syllabi).", html.Br(),
            f"Courses with empty PO matrix:{zero_contrib_courses}.",html.Br(),
            "Vertical axis: Program outcome  (PO) numbers, Horizontal axis: Level of support for PO in syllabi of core courses.",html.Br(),
            "Contribution of each course is equal to its ECTS.",html.Br(),
            tmp]

@app.callback(
    Output('evidence-eval-output', 'children'),
    Input('dropdown-departments', 'value'),
    Input("dropdown-courses","value"),
    prevent_initial_call=True,
)
def show_evidence_based_eval(department, course):
    if course and not course=="Tüm dersler":courselist=[course]
    else:courselist=courses[department]
    try:
        ed=evidencelibSimple.get_evidence_data(department=localsettings["department_full_names"][department])
    except Exception as e:
        return "AN ERROR OCCURRED WHILE USING THE GRADES FILE:"+str(e)
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
    return (html.H3("Average grades in courses"),
            f"These courses have no grade data: {noGradeCourses}",html.Br(),
            "Average grades in courses (on a scale of 0.0-to-1.0):",
            gr1,
            html.H3("Achievement of program outcomes"),
            f"Average achievement of program outcomes for department: {department}.",html.Br(),
            "Vertical axis is program outcome numbers", html.Br(),
            "Horizontal axis: Achievement of program outcomes considering average student grades in each course (maximum possible contribution of each course is equal to its ECTS, see documentation for details)",html.Br(),
            gr2)

@app.callback(Output('upload-grades-status', 'children'),
              Input('upload-grades', 'contents'),
              State('upload-grades', 'filename'),
              State('upload-grades', 'last_modified'),
              State('passwd', 'value'),
              prevent_initial_call=True,
              )
def upload_grades(fcontent, fname, fdate,passwd):
    if not checkpasswd(passwd):
        return "CANNOT SAVE: Password incorrect"
    content_type, content_string = fcontent.split(',')
    print("FILE SELECTION:",fname,fcontent[:256])
    if fname.split(".")[-1].lower()!="xlsx":
        return("ERROR: Only excel/xlsx files allowed")
    decoded = base64.b64decode(content_string)
    fnametosave=Path(storage)/"evidence"/localsettings["evidence_single_filename"]
    open(fnametosave,"wb").write(decoded)
    return "SAVED. Now refresh page and choose program to analyse"