# Class 01
# Answers to the CEO

# command: loading dataset "kc_house_data.csv"
# function: read_csv()
# library: Pandas

import pandas as pd

# Save dataset in a variable called data
data = pd.read_csv("datasets/kc_house_data.csv")

# Show the 5 first rows of the dataset
# print( data.head() )

# Show the number of rows and columns of the dataset
# function: shape
#print( data.shape )

# Show names of the columns of the dataset
# function: columns
# print ( data.columns )

# Show ordered data of the "price" column
# function: sort_values(), this function receives a reference column to be sorted
# with [[]] I can pick the columns I want
#print( data[["id","price"]].sort_values( "price" ) )

# Show descending ordered data of the "price" column
#print( data[["id","price"]].sort_values( "price", ascending=False ) )

# Exercises
#Quantas casas estão disponíveis para compra?
# Assumindo que todas as casas estão disponíveis para compra, são quantos "ids" temos
# R: data["id"].nunique()

#Quantos atributos as casas possuem?
# Número de colunas?
# R: 21 atributos - data e id = 19 atributos

#Quais são os atributos das casas?
# O nome das colunas (mas algumas colunas não possuem um significado muito claro)
# print ( data.columns )
# Mas id e data não são atributos!
# função drop para remover colunas

# data.drop( ["id", "date"], axis=1 )
# R: os atributos das casas são: 'price', 'bedrooms', 'bathrooms', 'sqft_living',
#        'sqft_lot', 'floors', 'waterfront', 'view', 'condition', 'grade',
#        'sqft_above', 'sqft_basement', 'yr_built', 'yr_renovated', 'zipcode',
#        'lat', 'long', 'sqft_living15', 'sqft_lot15'

#Qual a casa mais cara ( casa com o maior valor de venda )?
# print( data[["id","price"]].sort_values( "price", ascending=False ) )
# R: A casa mais cara é a de id "6762700020"

#Qual a casa com o maior número de quartos?
# print( data[["id","bedrooms"]].sort_values( "bedrooms", ascending=False ) )
# R: A casa com maior número de quartos é a de id "2402100895"

#Qual a soma total de quartos do conjunto de dados?
# total_quartos = data[["bedrooms"]].sum()
# print( total_quartos )
# R: A soma total de quartos do conjunto de dados é 72854

#Quantas casas possuem 2 banheiros?
print ( data.columns )
# print( data[["bathrooms"]]==2 )
# o comando acima mostra uma tabela com True or False para a condição
# print ( data.groupby(["bathrooms"]==2).sum() )
# o comando acima deu erro
# print ( data[["bathrooms"]].groupby(["bathrooms"]==2).sum() )
# o comando acima deu erro

# print( data[ data[ "bathrooms" ]==2 ].groupby( ["bathrooms"] ).sum() )

# print( data[ [ "bathrooms" ] == 2 ].groupby( [ "bathrooms" ] ).sum() )

# print( data[ [ "bathrooms" ] == 2 ].sum()

#Qual o preço médio de todas as casas no conjunto de dados?

# print( data[["price"]].mean() )
# R: O preço médio de todas as casas é 540088.14

#Qual o preço médio de casas com 2 banheiros?

#Qual o preço mínimo entre as casas com 3 quartos?

#Quantas casas possuem mais de 300 metros quadrados na sala de estar?
#Quantas casas tem mais de 2 andares?
#Quantas casas tem vista para o mar?

print( data[["waterfront"]] == 1)

#Das casas com vista para o mar, quantas tem 3 quartos?
#Das casas com mais de 300 metros quadrados de sala de estar, quantas tem mais de 2 banheiros?




