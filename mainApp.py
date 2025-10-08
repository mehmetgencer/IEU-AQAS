#!/usr/bin/python3
from dash import Dash, html, dcc, Input, Output, State, callback # pyright: ignore[reportMissingImports]
from flask import Flask # pyright: ignore[reportMissingImports]
import dash_ag_grid as dag # pyright: ignore[reportMissingImports]
import plotly.express as px # pyright: ignore[reportMissingImports]
import json, pprint
from pathlib import Path
from settings import localsettings, checkpasswd
import courseLevelApp
import programLevelApp

server = Flask(__name__)
courseLevelApp.app.init_app(server)
programLevelApp.app.init_app(server)

main_menu=f"""
    <h1>IEU-AQAS</h1>
    <h2><a href="help">Documentation</a></h2>
    <h2><a href="course_level/">Course Level App</a></h2> 
    <h2><a href="program_level/">Program Level App</a></h2>
"""

@server.route(f"{localsettings['route_prefix']}/")
def home():
    return main_menu

@server.route(f"{localsettings['route_prefix']}/help")
def help():
    return main_menu+open("IEU-AQAS-Scheme.html","r").read()

if __name__ == "__main__":
    server.run(host="127.0.0.1",port=8080,debug=True)