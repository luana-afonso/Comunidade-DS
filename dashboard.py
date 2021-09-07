
import folium
import geopandas
import numpy      as np
import pandas       as pd
import plotly.express   as px
import streamlit    as st

from datetime       import datetime
from folium.plugins   import MarkerCluster
from streamlit_folium   import folium_static

# ------------------------------------------
# Settings
# ------------------------------------------

# definição de layout para ele ficar um pouco mais comprido/amplo
st.set_page_config( layout='wide' )

# ------------------------------------------
# Helper Functions
# ------------------------------------------
# função para carregar os dados que estão salvos no arquivo
@st.cache( allow_output_mutation=True )
def get_data( path ):
    data = pd.read_csv( path )
    return data

# função para ler o arquivo geopandas onde vai ter as coordenadas para poder fazer as densidades por preço
@st.cache( allow_output_mutation=True )
def get_geofile( url ):
    geofile = geopandas.read_file( url )
    return geofile

def set_feature( data ):
  #add new feature
  data['price_m2'] = data['price'] / data['sqft_lot']

  return data

# uma função responsável por plotar as tabelas
def overview_data( data ):
  f_attributes = st.sidebar.multiselect( 'Enter columns', data.columns )
  f_zipcode = st.sidebar.multiselect('Enter zipcode',data['zipcode'].unique() )
  st.title( 'Data Overview' )

  # attributes + zipcode = selecionar colunas e linhas
  # Se o f_zipcode e f_attributes forem diferente de vazio (ou seja, se tiver esses filtros aplicados)
  if ( f_zipcode != [] ) & ( f_attributes != [] ):
    data = data.loc[data['zipcode'].isin( f_zipcode ), f_attributes]

  # zipcode = selecionar linhas
  elif ( f_zipcode != [] ) & ( f_attributes == [] ):
    data = data.loc[data['zipcode'].isin( f_zipcode ), :]

  # attributes = selecionar colunas
  elif ( f_zipcode == [] ) & ( f_attributes != [] ):
    data = data.loc[:, f_attributes]
  # se o usuario nao quiser filtrar nada retornamos o dataset original
  # 0 + 0 = retorno o dataset original (não filtro nada)
  else:
    data = data.copy()

  st.dataframe( data )
  # criando layout lado a lado
  # função beta_columns que pode receber um tuple: a quantidade de numeros é quantas colunas voce quer e o valor indica a largura
  c1, c2 = st.beta_columns((1, 1))

  # Average metrics
  # Observar o número total de imóveis, a média de preço, a média da sala de estar e também a média do preço por metro quadrado em cada um dos códigos postais
  df1 = data[['id','zipcode']].groupby( 'zipcode' ).count().reset_index()
  df2 = data[['price','zipcode']].groupby( 'zipcode').mean().reset_index()
  df3 = data[['sqft_living','zipcode']].groupby( 'zipcode').mean().reset_index()
  df4 = data[['price_m2','zipcode']].groupby( 'zipcode').mean().reset_index()

  # merge
  # Juntando as average metrics em uma tabela
  m1 = pd.merge( df1, df2, on='zipcode', how='inner' )
  m2 = pd.merge( m1, df3, on='zipcode', how='inner' )
  df = pd.merge( m2, df4, on='zipcode', how='inner' )
  # Renomeando as colunas
  df.columns = ['ZIPCODE', 'TOTAL HOUSES', 'PRICE', 'SQRT LIVING','PRICE/M2']

  # Plotando tabelas dessas médias...

  # Pode mostrar com write ou dataframe
  # Com dataframe mais fácil de alterar os tamanhos
  # st.write( df.head() )
  # st.dataframe( df, width=600. height=600 )
  # st.dataframe( df, height=600 )
  c1.header( 'Average Values' )
  c1.dataframe( df, height=400 )

  # Visualizar métricas descritivas de cada de atributos escolhidos
  # Descriptive Statistics

  # tendencia central
  num_attributes = data.select_dtypes( include=['int64', 'float64'] )
  media = pd.DataFrame( num_attributes.apply( np.mean ) )
  mediana = pd.DataFrame( num_attributes.apply( np.median ) )

  # dispersão
  std = pd.DataFrame( num_attributes.apply( np.std ) )
  max_ = pd.DataFrame( num_attributes.apply( np.max ) )
  min_ = pd.DataFrame( num_attributes.apply( np.min ) )

  # concatenando
  df1 = pd.concat([max_, min_, media, mediana, std], axis=1 ).reset_index()
  df1.columns = ['attributes', 'max', 'min', 'mean', 'median', 'std']
  #df1.columns = ['attributes','max','mean','median','std','teste']

  #st.dataframe( df1, height=600 )
  c2.header( 'Descriptive Analysis' )
  c2.dataframe( df1, height=400 )

  #a função não retorna nada, apenas faz os gráficos para visualização
  return None

# função para criar os mapas
def portfolio_density( data, geofile ):
  # Mapa onde o CEO consegue ver onde está a disponibilidade de imoveis por região
  st.title( 'Region Overview' )

  # Criando 2 colunas para colocar os mapas lado a lado
  c1, c2 = st.beta_columns( ( 1, 1 ) )
  c1.header( 'Portfolio Density' )

  # Selecionando apenas 10 para o for ficar mais rápido
  df = data.sample( 10 )

  # Base Map - Folium
  # Defino um mapa base (vazio) e depois uso a classe MarkerCluster para ir adicionando os pontos no mapa
  density_map = folium.Map( location=[data['lat'].mean(), data['long'].mean() ], default_zoom_start=15 )
  # assim consigo adicionar alguns marcadores
  marker_cluster = MarkerCluster().add_to( density_map )

  # iterrows é um objeto para fazer iteração com o for
  # popup é um 'card' que pode aparecer uma mensagem
  # E então podemos criar a função popup para criar cards para o usuário clicar
  for name, row in df.iterrows():
      folium.Marker( [row['lat'], row['long'] ],
                     popup='Sold R${0} on: {1}. Features: {2} sqft, {3} bedrooms,{4} bathrooms, year built: {5}'.format( row['price'],
                                                                                                                         row['date'],
                                                                                                                         row['sqft_living'],
                                                                                                                         row['bedrooms'],
                                                                                                                         row['bathrooms'],
                                                                                                                         row['yr_built'] ) ).add_to( marker_cluster )

  # Clause with com o folium é uma definição do proprio streamlit. O streamlit nao tem suporte nativo para o folium (só para o plotly)
  # Para usar esse folium_static precisamos do with
  with c1:
      folium_static( density_map )

  # Region Price Map
  c2.header( 'Price Density' )
  df = data[['price','zipcode']].groupby( 'zipcode' ).mean().reset_index()
  df.columns = ['ZIP', 'PRICE']

  #df = df.sample( 10 )
  # Filtrando o geofile, para ter só os ZIPs que temos no dataframe
  geofile = geofile[geofile['ZIP'].isin( df['ZIP'].tolist() )]
  # criando mapa base com o folium
  region_price_map = folium.Map( location=[data['lat'].mean(),data['long'].mean() ],default_zoom_start=15 )

  # para fazer plot de densidade por cor
  # key_on faz um 'join' das colunas
  # 'YlOrRd': degradê de cores (yellow, orange, red)
  region_price_map.choropleth( data = df,
                               geo_data = geofile,
                               columns=['ZIP', 'PRICE'],
                               key_on='feature.properties.ZIP',
                               fill_color='YlOrRd',
                               fill_opacity = 0.7,
                               line_opacity = 0.2,
                               legend_name='AVG PRICE' )

  with c2:
      folium_static( region_price_map )

  return None

# função para criar os gráficos de variação
def commercial_distribution( data ):
  st.sidebar.title( 'Commercial Options' )
  st.title( 'Commercial Attributes' )

  # ---------- Average Price per year built

  # setup filters (tem alguns 'truques' para setar filtros
  min_year_built = int( data['yr_built'].min() )
  max_year_built = int( data['yr_built'].max() )

  # tipo de filtro e o subheader escreve um texto para indicar ao usuário o que fazer
  st.sidebar.subheader( 'Select Max Year Built' )
  # retorna o filtro em uma variavel
  # f_year_built é a variável que vai ser passada via filtro
  f_year_built = st.sidebar.slider( 'Year Built', min_year_built,
                          max_year_built,
                          min_year_built )

  st.header( 'Average price per year built' )

  # get data

  # Para a data ficar em um formato mais bonitinho
  data['date'] = pd.to_datetime( data['date'] ).dt.strftime( '%Y-%m-%d' )

  # data selection
  data = data.loc[data['yr_built'] < f_year_built]
  df = data[['yr_built','price']].groupby( 'yr_built' ).mean().reset_index()

  # plot
  fig = px.line( df, x='yr_built', y='price' )
  st.plotly_chart( fig, use_container_width=True )

  ## ---------- Average Price per day

  st.header( 'Average Price per day' )
  st.sidebar.subheader( 'Select Max Date' )

  # load data
  data = get_data( path='datasets/kc_house_data.csv' )
  data['date'] = pd.to_datetime( data['date'] ).dt.strftime( '%Y-%m-%d' )

  # setup filters
  min_date = datetime.strptime( data['date'].min(), '%Y-%m-%d' )
  max_date = datetime.strptime( data['date'].max(), '%Y-%m-%d' )

  # o sidebar recebe dados numericos (data não)
  f_date = st.sidebar.slider( 'Date', min_date, max_date, min_date )
  #??? Pq fica aparecendo datas somente entre 2014 e 2015?

  # filter data
  # convertendo para datetime senão fica em formato string e não é possível fazer a comparação no proximo comando
  data['date'] = pd.to_datetime( data['date'] )
  # f_date é a variável que vai ser passada via filtro
  data = data[data['date'] < f_date]
  df = data[['date', 'price']].groupby( 'date' ).mean().reset_index()

  # plot
  fig = px.line( df, x='date', y='price' )
  st.plotly_chart( fig, use_container_width=True )

  # ---------- Histogram -----------
  st.header( 'Price Distribution' )
  st.sidebar.subheader( 'Select Max Price' )

  data = get_data( path='datasets/kc_house_data.csv' )
  print( data[data['price'].isnull()] )

  # filters
  min_price = int( data['price'].min() )
  max_price = int( data['price'].max() )
  avg_price = int( data['price'].mean() )

  # o default agora sendo a média dos preços
  # data filtering
  f_price = st.sidebar.slider( 'Price', min_price, max_price, avg_price )
  df = data[data['price'] < f_price]

  # plot
  # nbins são quantas barras queremos no histograma
  fig = px.histogram( df, x='price', nbins=50 )
  st.plotly_chart( fig, use_container_width=True )

  return None

def attributes_distribution( data ):

  st.title( 'House Attributes' )
  st.sidebar.title( 'Attributes Options' )

  # filters
  f_bedrooms = st.sidebar.selectbox( 'Max number of bedrooms', sorted( set( data['bedrooms'].unique() ) ) )
  f_bathrooms = st.sidebar.selectbox( 'Max number of bathrooms', sorted( set( data['bathrooms'].unique() ) ) )

  c1, c2 = st.beta_columns( 2 )

  # Houses per bedrooms
  c1.header( 'Houses per bedrooms' )
  # obs: esse tipo de filtragem dos dados relacionado ao valor inserido no filtro, faz o mesmo ser funcional!
  df = data[data['bedrooms'] < f_bedrooms]
  # plot
  fig = px.histogram( df, x='bedrooms', nbins=19 )
  c1.plotly_chart( fig, use_container_width=True )

  # Houses per bathrooms
  c2.header( 'Houses per bathrooms' )
  df = data[data['bathrooms'] < f_bathrooms]
  # plot
  fig = px.histogram( df, x='bathrooms', nbins=10 )
  c2.plotly_chart( fig, use_container_width=True )

  # filters
  f_floors = st.sidebar.selectbox( 'Max number of floors', sorted( set( data['floors'].unique() ) ) )
  f_waterview = st.sidebar.checkbox( 'Only Houses with Water View' )

  c1, c2 = st.beta_columns( 2 )

  # Houses per floors
  c1.header( 'Houses per floors' )
  df = data[data['floors'] < f_floors]
  # plot
  fig = px.histogram( df, x='floors', nbins=10 )
  c1.plotly_chart( fig, use_container_width=True )

  # Houses per water view
  # Atenção! 'waterfront' é uma variável categórica
  c2.header( 'Houses per Water View' )

  if f_waterview:
    df = data[data['waterfront'] == 1]
  else:
    df = data.copy()

  fig = px.histogram( df, x='waterfront', nbins=10 )
  c2.plotly_chart( fig, use_container_width=True )

  return None

if __name__ == '__main__':
  # ETL
  # data Extraction
  # data Transformation
  # data Loading (no caso não temos, mas poderia ter)

  # extraction
  path = 'datasets/kc_house_data.csv'
  url='https://opendata.arcgis.com/datasets/83fc2e72903343aabff6de8cb445b81c_2.geojson'

  # load data
  data = get_data( path )
  geofile = get_geofile( url )

  # transformation

  # criar nova feature (novo data vindo com nova feature)
  data = set_feature( data )

  overview_data( data )

  portfolio_density( data, geofile )

  commercial_distribution( data )

  attributes_distribution( data )
