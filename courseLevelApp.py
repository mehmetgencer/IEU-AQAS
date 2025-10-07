#!/usr/bin/python3
from dash import Dash, html, dcc, Input, Output, State, callback # pyright: ignore[reportMissingImports]
from flask import Flask # pyright: ignore[reportMissingImports]
import dash_ag_grid as dag # pyright: ignore[reportMissingImports]
import plotly.express as px # pyright: ignore[reportMissingImports]
import json, pprint, math
import pandas as pd
from pathlib import Path
from settings import * #localsettings, checkpasswd
import evidencelibSimple, courselib

app = Dash(server=False,routes_pathname_prefix=f"{localsettings['route_prefix']}/course_level/")


app.layout = html.Div([
    html.A(href=localsettings["route_prefix"],children=html.H1(children='IEU İşletme AQAS-Go to main menu', style={'textAlign':'center'})),
    dcc.Input(
            id="passwd",
            type="password",
            placeholder="Enter password here",
        ),
    dcc.Dropdown(dict((d,d) for d in courses.keys()),None , id='dropdown-departments',disabled=True),
    dcc.Dropdown([],None,id='dropdown-courses',disabled=True),
    html.H2(children='1 - Activity to learning outcomes (A-LO) matrix'), #, style={'textAlign':'center'}
    html.Ol(id="los",children="Learning outcomes: (Ders seçtiğinizde burası dolar)"),
    dag.AgGrid(
        id="alo-grid",
        defaultColDef={"editable": True},
        columnSize="autoSize",
        ),
    html.Div(id="alo-output"),
    html.Button('A-LO Değişikliklerini Kaydet', id='save-alo-grid-button', n_clicks=0),
    html.H2(children="2 - Learning outcomes to Program outcomes (LO-PO) matrix"),
    html.Ol(id="pos",children="Program outcomes: ..."),
    dag.AgGrid(
        id="lopo-grid",
        defaultColDef={"editable": True},
        columnSize="autoSize",
    ),
    html.Div(id="lopo-output"),
    html.Button('LO-PO Değişikliklerini Kaydet', id='save-lopo-grid-button', n_clicks=0),
    html.H2(children="3 - Bu LO-PO matrix her PO ne kadar destek veriyor?"),
    html.P("(Course program outcomes matrix burada otomatik oluşacak ama henüz kodlanmadı)"),
    
    ]
)

@callback(
    Output("save-alo-grid-button","disabled"),
    Output("save-lopo-grid-button","disabled"),
    Output('dropdown-departments', 'disabled'),
    Output('dropdown-courses', 'disabled'),
    Input('passwd', 'value'),
    #prevent_initial_call=True
)
def checkpass_and_enable(value):
    if not checkpasswd(value):return True,True,True,True
    return False,False,False,False

@callback(
    Output('dropdown-courses', 'options'),
    Input('dropdown-departments', 'value')
)
def update_courselist_dropdown(department):
    print("Department selected:",department)
    if not department:return []
    opts = [{'label':opt, 'value':opt} for opt in courses[str(department)]]
    #print(department,opts)
    return opts

@callback(
    Output("alo-grid", "rowData"),
    Output("alo-grid", "columnDefs"),
    State('dropdown-departments', 'value'),
    Input("dropdown-courses", "value"),
    prevent_initial_call=True,
)
def load_alo_grid(department,course):
    print("Loading alo grid for",department,"---",course)
    fname=course+".csv"
    df=pd.read_csv(Path(storage)/"a-to-lo"/department/fname)
    coldefs=[{"field":x,"editable":False} for x in list(df.columns)[:3]] +         [{"field":x,'cellStyle': {
            "function": "params.value && {'backgroundColor': 'rgb(255,0,0,0.2)'}"
            }
        } for x in list(df.columns)[3:]]
    print("LOADED A-to-LO grid",department,"-",course)
    return df.to_dict("records"),coldefs

def is_empty(values):
    """Returns True if all values (of a pandas data row/col or row/col segment) are NaN or None or empty"""
    i=0
    for x in values:
        i+=1
        if x is not None and x!='' and not math.isnan(float(x)):
            print(f"Non-empty '{x}' at {i}")
            return False
    return True

def is_all1or0s(values):
    """Returns True if all values (of a pandas data row or row segment) are either 1s or 0s"""
    for x in values:
        if float(x) not in [0.,1.]:return False
    return True

def check_alo_grid_data(row_data):
    """
    Check an A-LO grid dat aso that (1) non-used activities have no LO contribution and
    (2) contribution values are either 1 or 0
    """
    df=pd.DataFrame(row_data)
    for i,row in df.iterrows():
        #print("row:",i,row)
        if row[1]>=0:
            if not is_all1or0s(row[3:]):return False, f"Values different from 0 or 1 in row {i+1} which is a used activity"
        else:
            if not is_empty(row[2:]):return False, f"Nonzero values in row {i+1}, which is not a used activity in course"
    return True,"No errors in A-LO grid"

@callback(
    Output("alo-output", "children"), 
    Input("save-alo-grid-button","n_clicks"),
    State('passwd', 'value'),
    State("dropdown-departments", "value"),
    State("dropdown-courses", "value"),
    State("alo-grid", "rowData"),

    prevent_initial_call=True,
)
def save_alo_grid(n_clicks, passwd,department,course,row_data):
    if not checkpasswd(passwd):return "INVALID PASSWORD"
    df=pd.DataFrame(row_data)
    print("Attempting to save A-LO",department,course)
    if len(df)==0:return "No data to save"
    check_status,check_results=check_alo_grid_data(row_data)
    if not check_status:
        return f"ERROR in A-LO matrix: {check_results}"
    fname=course+".csv"
    df.to_csv(Path(storage)/"a-to-lo"/department/fname,index=False)
    return "A-LO data saved"

@callback(
    Output("lopo-grid", "rowData"),
    Output("lopo-grid", "columnDefs"),
    State('dropdown-departments', 'value'),
    Input("dropdown-courses", "value"),
    prevent_initial_call=True,
)
def load_lopogrid(department,course):
    print("Loading lopo grid for",department,"---",course)
    pocontrib=courselib.get_pocontrib_from_sylabus(department,course)
    fname=course+".csv"
    df=pd.read_csv(Path(storage)/"lo-to-po"/department/fname)
    cols=list(df.columns)
    coldefs=[{"field":x,"editable":False} for x in cols[:1]] \
        + [{"field":cols[i],
            "editable":True if pocontrib[i] else False,
            'cellStyle': {"function": "params.value && {'backgroundColor': 'rgb(255,0,0,0.2)'}"}
            } for i in range(1,len(cols))]
    return df.to_dict("records"),coldefs

def check_lopo_grid_data(row_data):
    """
    Check an A-LO grid dat aso that (1) non-used activities have no LO contribution and
    (2) contribution values are either 1 or 0
    """
    df=pd.DataFrame(row_data)
    for colname,col in df.items():
        if colname=="LO_ID":continue
        print("colname:",colname)
        if is_empty(col):
            print("all empty")
            continue
        elif is_all1or0s(col):
            print("All 1s or 0s",col[1:])
            continue
        return False, f"Values different from 0 or 1 in column {colname}"
    return True,"No errors in LO-PO grid"

@callback(
    Output("lopo-output", "children"), 
    Input("save-lopo-grid-button", "n_clicks"),
    State('passwd', 'value'),
    State("lopo-grid", "rowData"),
    State("dropdown-departments", "value"),
    State("dropdown-courses", "value"),
    prevent_initial_call=True,
)
def save_lopo_grid(n_clicks,passwd,row_data,department,course):
    if not checkpasswd(passwd):return "INVALID PASSWORD"
    df=pd.DataFrame(row_data)
    #print("LENDF",len(df))
    #if not cell_changed:return "PASSWORD OK"
    if len(df)==0:return "No data to save"
    print("SAVING LOPO",department,course)
    check_status,check_results=check_lopo_grid_data(row_data)
    if not check_status:
        return f"ERROR in LO-PO matrix: {check_results}"
    fname=course+".csv"
    df.to_csv(Path(storage)/"lo-to-po"/department/fname,index=False)
    return f"LO-PO data saved"

@callback(
    Output("los", "children"),
    State('dropdown-departments', 'value'),
    Input("dropdown-courses", "value"),
    prevent_initial_call=True,
)
def load_courselos(department,course):
    fname=course+".json"
    los=json.load(open(Path(storage)/"lo-list"/department/fname,"r"))
    return [html.H3(children="Learning outcomes list for course %s"%course)]+[html.Li(children=x) for x in los]

@callback(
    Output("pos", "children"),
    Input('dropdown-departments', 'value'),
    #Input("dropdown-courses", "value"),
    prevent_initial_call=True,
)
def load_departmentpos(department):
    pos=program_outcomes[department]
    return [html.H3(children="Program outcomes list for department %s"%department)]+[html.Li(children=x) for x in pos]



#server = app.server #see https://community.plotly.com/t/how-to-add-your-dash-app-to-flask/51870/2
#@server.route("/hello")
#def home():
#    return "Hello, Flask!"

if __name__ == "__main__":
    server = Flask(__name__)
    app.init_app(server)
    app.run(debug=True)