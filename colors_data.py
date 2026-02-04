import requests
import pandas as pd

url = 'https://teamcolorcodes.com/mlb-color-codes/'
html = requests.get(url).content
df_list = pd.read_html(html)
colors_df = df_list[-2]
colors_df.columns = ["Team", "color1", "color2", "color3", "color4", "color5"]
colors_df[['color1', 'hex']] = colors_df['color1'].str.split(n=1, expand=True)
colors_df['hex'] = colors_df['hex'].str.split().str[-1]
colors_df = colors_df.drop(columns=['color1', 'color2', 'color3', 'color4', 'color5'])
colors_df.loc[len(colors_df)] = ["2 Team", "#808080"]
colors_df.to_csv("data/colors.csv", index=False)