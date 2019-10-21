#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DM lesson4
Dans ce dataset: https://raw.githubusercontent.com/fspot/INFMDI-721/master/lesson5/products.csv, chaque ligne correspond à un produit alimentaire mis en vente par un utilisateur.

Objectif: cleaner le dataset.

On aimerait avoir une colonne de prix unifiés en euros. 
Problème: la currency n'est pas indiquée pour tous les produits: 
    il va falloir essayer de "deviner" les currency manquantes, 
    en se basant sur l'adresse IP de l'utilisateur.
La colonne "infos" liste des ingrédients présents dans le produit. 
On préfèrerait avoir une colonne de type bool par ingrédient, 
indiquant si le produit contient ou non cet ingrédient.
Voic une liste d'APIs qui peut vous être utile : 
    https://github.com/public-apis/public-apis 
    (mais vous pouvez en utiliser d'autres si vous le voulez).

Created on Fri Oct 18 14:23:23 2019

@author: kaelig castor
"""
import pandas as pd 
#import json
import requests
import time
#import re
#import numpy as np
# import dataset and see some basic caracteristics
df =  pd.read_csv('https://raw.githubusercontent.com/fspot/INFMDI-721/master/lesson5/products.csv', sep=';', engine='python')  ;
df.head()
type(df)
df.shape
df.info()
# get the IP address and use an API to find the associated country
df['price_in_euro'] = df.apply(lambda _: '', axis=1) 
df['ioc'] = df.apply(lambda _: '', axis=1) 
df['currency_code'] = df.apply(lambda _: '', axis=1) 
df['original_price_check'] = df.apply(lambda _: '', axis=1)
urlcurex='https://api.exchangerate-api.com/v4/latest/EUR'
respcurex = requests.get(urlcurex) 
reposcurex = respcurex.json()
# alternative :
token='b0db7d57fdd1d4ce7f0f17747ac518dd'
urlcurexal = 'http://apilayer.net/api/'
urlcurexalt = urlcurexal+'live?access_key='+token+'&format=1'
respcurexalt = requests.get(urlcurexalt) 
reposcurexalt = respcurexalt.json()
df['digit_price']= df['price'].str.isdigit() 
df['infos'] = df.infos.str.replace(',|:|Contains?|May|Ingredients?|and','',case=False, regex=True)
strlist=df.infos.str.split(' ')
ingredients = df['infos'].str.split(expand=True).stack()
for king in ingredients: 
    df[king] = df.apply(lambda x: True if king in x['infos']   else  False , axis=1)
#df.to_csv('Cleaned_products_test.csv', sep=';')
def test_digit(a):   
    newstring = ''      
    indicatedcurrency = ''
    for k in range(len(a)):
        b=a[k]
        if b.isdigit() == True or b == '.': 
            newstring = newstring+b 
        elif b != ' ':
            indicatedcurrency = indicatedcurrency + b
    return newstring, indicatedcurrency
for kIPadd in range(len(df['ip_address'])):
    print('=============================================')
    print(kIPadd)
    print(df['price'][kIPadd])
    pricedig, indicatedcurrency = test_digit(df['price'][kIPadd])
    print(pricedig, indicatedcurrency)
    if indicatedcurrency != '':
        df['currency_code'][kIPadd] = indicatedcurrency
    IPadd = df['ip_address'][kIPadd]
    url = 'https://api.ipgeolocationapi.com/geolocate/'+IPadd
    #print("preparing request to IP API...")
    resp = requests.get(url) 
    time.sleep(.5)    
    #print("request done.")
    print(resp)
    if df['currency_code'][kIPadd] !='':
            convertratio = reposcurexalt['quotes']['USD'+df['currency_code'][kIPadd]]/reposcurexalt['quotes']['USDEUR'] 
            print('convertratio : ',convertratio)
            df['price_in_euro'][kIPadd]='{:.2f}'.format(float(pricedig)/convertratio)
            print('price_in_euro : ',df['price_in_euro'][kIPadd])
    else:    
        if resp.status_code != 200: # unvalid IP request
            print('oooopsssy! Bad Feedback From 1st API!')
        else:  # dump infos from API
                repos = resp.json()
                #print(repos)        
                akeys={'ioc','currency_code'}
                for cle in akeys:
                    if (cle in repos):
                        if df[cle][kIPadd]=='': df[cle][kIPadd]=repos[cle]
                        if cle=='currency_code':
                            df['original_price_check'][kIPadd]=pricedig
                            if  df['currency_code'][kIPadd] == 'EUR':  # repos[cle] == 'EUR': 
                                df['price_in_euro'][kIPadd]='{:.2f}'.format(float(pricedig)) # pas de conversion
                            else:
                                    # if df[cle][kIPadd] in reposcurex['rates']:
                                    #     df['price_in_euro'][kIPadd]='{:.2f}'.format(float(pricedig)/reposcurex['rates'][df[cle][kIPadd]])
                                    # else:
                                    convertratio = reposcurexalt['quotes']['USD'+df[cle][kIPadd]]/reposcurexalt['quotes']['USDEUR'] 
                                    print('convertratio : ',convertratio)
                                    df['price_in_euro'][kIPadd]='{:.2f}'.format(float(pricedig)/convertratio)
                                    print('price_in_euro : ',df['price_in_euro'][kIPadd])
    print(df['original_price_check'][kIPadd],df['currency_code'][kIPadd],df['price_in_euro'][kIPadd],'EUR')
    print('=============================================')
# row = next(df.iterrows())[1]
del df['infos']
#del df['price']
del df['ioc']
del df['original_price_check']
df.to_csv('CleanedProducts.csv', sep=';')
