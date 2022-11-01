import pandas as pd
from dash import html
import dash_bootstrap_components as dbc
from best_features import best_features
import numpy as np
import warnings
warnings.filterwarnings('ignore')
import pathlib

PATH = pathlib.Path(__file__).parent

df1 = pd.read_csv("data_img_1.csv")
df2 = pd.read_csv("data_img_2.csv")

# data_1 = best_features.pre_process(df1)
# data_2 = best_features.pre_process(df2)

print("dataframed are read")

output_file = best_features.best_feature(df1,df2)

print("got best features")
df = output_file.head(20)

df.to_csv("best_features.csv",index= False)
feature_df = pd.read_csv("best_features.csv")

if feature_df["floorplan_1"].sum() > feature_df["floorplan_2"].sum():
    conclusion = "Floor plan 1 is better than Floor plan 2."
if feature_df["floorplan_1"].sum() < feature_df["floorplan_2"].sum():
    conclusion = "Floor plan 2 is better than Floor plan 1."
if feature_df["floorplan_1"].sum() == feature_df["floorplan_2"].sum():
    conclusion = "Floor plan 1 and Floor plan 2 both are same."

summary, df_comp = best_features.comp(df)


# layout = dbc.Container([html.H3("Plan Comparison", className="display-6",
#             style={'textAlign': 'left'}),
#     dbc.Table.from_dataframe(df_comp, bordered=True),
# ])

layout = dbc.Container([html.H3("Plan Comparison", className="display-6",
            style={'textAlign': 'left'}),
    dbc.Table.from_dataframe(df_comp, bordered=True),
    html.H3("Conclusion", className="display-6",
            style={'textAlign': 'left'}),
    dbc.Card(html.P(conclusion), body=True)
])