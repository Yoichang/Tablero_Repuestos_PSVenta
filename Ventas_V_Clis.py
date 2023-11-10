
# Importando las bibliotecas necesarias
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from dash import dash_table

# Creando una base de datos de muestra

df = pd.read_excel("ventas_Cls__Art.xlsx")

df['Neto'] = df['Neto'].astype(str).str.replace('.', '').str.replace(',', '.', regex=True)
df['Neto'] = df['Neto'].replace('', '0').astype(float)

app = dash.Dash(__name__)

# Layout de la aplicación
# Layout de la aplicación
app.layout = html.Div([
    html.H1("Tablero de Repuestos - Post Venta Automotriz"),

    # Sección 1: Selección de vendedor y mes, y gráfico de ventas
    html.Div([
        html.Div([
            html.Label("Selecciona un vendedor:"),
            dcc.Dropdown(
                id='vendedor-dropdown',
                options=[{'label': vendedor, 'value': vendedor} for vendedor in df['R_Ventas'].unique()],
                multi=False
            ),
        ],
        style={'width': '30%', 'display': 'inline-block'}),

        html.Div([
            html.Label("Selecciona un mes:"),
            dcc.Dropdown(
                id='mes-dropdown',
                options=[{'label': mes, 'value': mes} for mes in df['Mes'].unique()],
                multi=False
            ),
        ],
        style={'width': '30%', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(id='ventas-graph'),
        ],
        style={'width': '100%', 'float': 'right', 'display': 'inline-block'}),
    ]),

    # Sección 2: Top clients y top articles
    html.Div([
        # Subsección 1: Top clients
        html.Div([
            html.H3("Top 15 Clientes"),
            dash_table.DataTable(id='top-clients-table'),
        ],
        style={'width': '50%', 'display': 'inline-block'}),

        html.Div([
            html.H3("Top 15 Clientes"),
            dcc.Graph(id='top-clients-graph'),
        ],
        style={'width': '50%', 'float': 'right', 'display': 'inline-block'}),

        # Subsección 2: Top articles
        html.Div([
        html.H3("Top 50 Artículos vendidos en el Mes Seleccionado"),
        html.Div(dash_table.DataTable(id='top-articles-table')),
        ], style={'display': 'inline-block', 'flex-direction': 'column', 'align-items': 'flex-start','width': '100%'}),

       
    ]),

 # Sección 3: Top articles
        html.Div([
        html.H3("Top 20 Artículos Más Vendidos en el Año para el Vendedor Seleccionado"),
             
        dcc.Graph(id='top-articles-años-graph'),
            ],
        style={'width': '100%', 'float': 'right', 'display': 'inline-block'}),
        
],

style={
    'backgroundColor': '#ECEFF1',  # Color de fondo oscuro
    'padding': '10px',  # Espaciado interno del contenedor
    'color': '#641E16'  # Color de texto por defecto
})

@app.callback(
    Output('ventas-graph', 'figure'),
    [Input('vendedor-dropdown', 'value'),
     Input('mes-dropdown', 'value')]
)
def update_graph(selected_vendedor, selected_mes):
    filtered_df = df
    
    if selected_vendedor and selected_mes:
        filtered_df = df[(df['R_Ventas'] == selected_vendedor) & (df['Mes'] == selected_mes)]
        fig = px.bar(filtered_df, x='R_Ventas', y='Neto', title=f"Ventas de {selected_vendedor} en el mes de {selected_mes}", color='Mes')
    elif selected_vendedor:
        filtered_df = df[df['R_Ventas'] == selected_vendedor]
        fig = px.bar(filtered_df, x='Mes', y='Neto', title=f"Ventas de {selected_vendedor} por Mes", color='Mes')
    elif selected_mes:
        filtered_df = df[df['Mes'] == selected_mes]
        fig = px.bar(filtered_df, x='R_Ventas', y='Neto', title=f"Ventas en el mes de {selected_mes} por Vendedor", color='R_Ventas')
    else:
        fig = px.bar(df, x='R_Ventas', y='Neto', title="Ventas Totales por Vendedor", color='Mes')
    
    # Añadir estilos oscuros al gráfico:
    fig.update_layout(
        plot_bgcolor='#A9CCE3', #color para dentro delgrafico
        paper_bgcolor='#E5E8E8',# color para fuera el cuadrado fuera del grafico 
        font=dict(color='#C0392B') # color de letra del grafico
    )
    
    return fig

@app.callback(
    [Output('top-clients-table', 'data'),
     Output('top-clients-graph', 'figure')],
    [Input('mes-dropdown', 'value')]
)
def update_top_clients(selected_mes):
    if not selected_mes:
        return [], {}
    
    # Filtrar el dataframe por el mes seleccionado
    filtered_df = df[df['Mes'] == selected_mes]
    
    # Sumar las compras por cliente
    sum_by_client = filtered_df.groupby('Cuenta_Cliente').sum().sort_values('Neto', ascending=False).reset_index()
    
    # Tomar los primeros 15 clientes
    top_clients = sum_by_client.head(15).copy()

    # Convertir los valores en el eje X a tipo numérico con manejo de errores
    top_clients['Cuenta_Cliente'] = pd.to_numeric(top_clients['Cuenta_Cliente'], errors='coerce')

    # Eliminar filas con valores no numéricos después de la conversión
    top_clients = top_clients.dropna(subset=['Cuenta_Cliente'])

    # Crear la tabla
    table_data = top_clients[['Cuenta_Cliente', 'Neto']].to_dict('records')
    
   # Crear el gráfico de barras
    fig = px.bar(top_clients, x='Cuenta_Cliente', y='Neto', title=f"Top 15 Clientes en {selected_mes}")

    # Ajustar la configuración del eje X
    fig.update_layout(xaxis=dict(type='category'), barmode='group')

    return table_data, fig


@app.callback(
    Output('top-articles-table', 'data'),
    [Input('mes-dropdown', 'value')]
)
def update_top_articles(selected_mes):
    # Filtrar el dataframe por el mes seleccionado
    filtered_df = df[df['Mes'] == selected_mes]
    
    # Filtrar para obtener solo los datos de los 15 principales clientes
    top_clients_list = filtered_df.groupby('Cuenta_Cliente').sum().sort_values('Neto', ascending=False).head(15).index.tolist()
    filtered_df = filtered_df[filtered_df['Cuenta_Cliente'].isin(top_clients_list)]
    
    # Sumar las ventas por artículo
    sum_by_article = filtered_df.groupby(['C_Artículo', 'Denominacion_Art']).sum().sort_values('Cantidad_Art', ascending=False).reset_index()
    
    # Tomar los primeros 50 artículos
    top_articles = sum_by_article.head(50).copy()

   
    # Preparar los datos para la tabla
    table_data = top_articles[['C_Artículo', 'Denominacion_Art', 'Cantidad_Art']].to_dict('records')
    
    return table_data

@app.callback( 
    Output('top-articles-años-graph', 'figure'),
    [Input('vendedor-dropdown',"value")]
)
def update_top_articles_años(selected_vendedor):
    # Sumar las ventas por artículo a lo largo del año
    sum_by_article_años = df.groupby(['C_Artículo', 'Denominacion_Art']).sum().sort_values('Cantidad_Art', ascending=False).reset_index()
    
    # Tomar los primeros 20 artículos
    top_articles_años = sum_by_article_años.head(20).copy()
    
    # Crear el gráfico de barras
    fig = px.bar(top_articles_años, x='C_Artículo', y='Cantidad_Art', title="Top 20 Artículos Más Vendidos en el Año")

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)  