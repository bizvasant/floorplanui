import plotly.express as px
from dash import Input, Output, html, dcc, State
import cv2
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
from main import app
import warnings
import base64
from contour import img_contour
from ocr import ocr

warnings.filterwarnings('ignore')
import pathlib

PATH = pathlib.Path(__file__).parent


layout = dbc.Container([
    html.Br(),
    dcc.Upload(id='upload-image_p2',
               children=html.Div(['Drag and Drop or ',
                                  html.A('Select Files')]),
               style={
                   'borderStyle': 'dashed',
                   'borderRadius': '5px',
                   'textAlign': 'center',
                   "height": "60px"
               },
               multiple=True),
    html.Br(),
    html.Div(id='output-image-upload_p2'),
])

def parse_contents(contents,filename):
    # contents = str(contents[0])
    encoded_data = contents.split(',')[1]
    nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    fig = px.imshow(img)
    fig.update_yaxes(tick0=0, dtick=200)
    fig.update_xaxes(tick0=0, dtick=200)
    output = html.Div([dcc.Graph(figure=fig)])
    cv2.imwrite(filename, img)
    try:
        df1 = ocr.ocr_info(filename)
        # df1.to_csv("df1_image.csv", index=False)
        df = df1.sort_values(['Features'],ascending=True)
        df.to_csv("data_img_2.csv", index=False)
        # df = pd.read_csv("data_img_2.csv")
        df['Area in sq. ft.'] = df['Area in sq. ft.'].astype(str)
        df = df.replace('[\([{})\]]','',regex=True)
        table = dbc.Table.from_dataframe(df, bordered=True)
        output = html.Div([dcc.Graph(figure=fig), table])
        try:
            image = cv2.imread(filename)
            contour, th = img_contour.find_contour(image)
            x, y, w, h, cx, cy = img_contour.find_center(img, contour, th)
            qads = img_contour.draw_contour(img, x, y, w, h, cx, cy)
            fig_quad = px.imshow(qads)
            output = html.Div([dcc.Graph(figure=fig), table,
            dcc.Graph(figure=fig_quad)])
            try:
                from quadrants_area_1 import quadrants_area
                qaud_info = quadrants_area.quad_area_info(image,filename)
                qaud_info.to_csv("quads_img_2.csv", index=False)
                qaud_df = pd.read_csv("quads_img_2.csv")
                area_dist_df = qaud_df.groupby('Quadrant').Feature_Quadrant_area.sum().reset_index()
                area_dist_df.rename(columns = {'Feature_Quadrant_area':'Area distribution per quadrant'}, inplace = True)
                area_dist_df['Area distribution per quadrant'] = area_dist_df['Area distribution per quadrant'].astype(int)
                area_dist_df.rename(columns= {'Area distribution per quadrant':'Total Area of Quadrant (Sq. ft.)'},inplace = True)       
                area_dist = dbc.Table.from_dataframe(area_dist_df, bordered=True, style={'textAlign': 'center'})
                qaud_df.rename(columns = 
                {'Actual_area':'Feature Area (Sq. ft.)','Feature_Quadrant_area':'Feature Area in Quadrant (Sq. ft.)' },
                inplace = True)
                qaud_info = dbc.Table.from_dataframe(qaud_df, bordered=True)
                # fig_quad.update_yaxes(visible=False)
                # fig_quad.update_xaxes(visible=False)
                fig_quad.update_yaxes(tick0=0, dtick=200)
                fig_quad.update_xaxes(tick0=0, dtick=200)
                from app import summary
                output = html.Div([dcc.Graph(figure=fig), table,
                        dcc.Graph(figure=fig_quad),area_dist,
                        qaud_info, summary.layout])
            except:
                output = html.Div([dcc.Graph(figure=fig), table,
                dcc.Graph(figure=fig_quad), html.H3("Area distribution is not generated for provided image.")])
        except:
            output = html.Div([dcc.Graph(figure=fig), table,
            html.H3("Quadrants are not drawn correctly for provided image.")])
    except:
        output = html.Div([dcc.Graph(figure=fig), html.H3("OCR code is not working for provided image.")])
    return html.Div([output])         


@app.callback(Output('output-image-upload_p2', 'children'),
              Input('upload-image_p2', 'contents'),
              State('upload-image_p2', 'filename'))
def update_output(list_of_contents, list_of_names):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n)
            for c, n in zip(list_of_contents, list_of_names)
        ]
        return children