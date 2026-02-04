import pandas as pd
import plotly.express as px
import sqlite3 as sql

conn = sql.connect("data/complete_data.db")
plot_df = pd.read_sql_query(
"""
SELECT *
FROM players_teams_colors
"""
, conn)
conn.close()

scatter = px.scatter(plot_df, title = 'OPS vs Predicted OPS', x='Predicted_OPS', y='OPS', color='Color', color_discrete_map="identity", hover_data=['Player', 'Team'])
scatter.add_shape(
    type="line", x0 = plot_df['Predicted_OPS'].min(),
    y0 = plot_df['Predicted_OPS'].min(), x1 = plot_df['Predicted_OPS'].max(),
    y1 = plot_df['Predicted_OPS'].max(), line = dict(color = 'gray')
)
scatter.update_yaxes(scaleanchor="x",scaleratio=.25)
scatter.show()