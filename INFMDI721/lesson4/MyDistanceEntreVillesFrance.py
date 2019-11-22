#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 13:29:33 2019

@author: kaelig
"""
import requests
from bs4 import BeautifulSoup
import json
import itertools

# 10 villes de France les plus peuplées
urlinit="https://fr.wikipedia.org/wiki/Liste_des_communes_de_France_les_plus_peuplées"
def get_soup_from_url(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')
    return soup

soup = get_soup_from_url(urlinit)

rows = soup.find("table").find_all("tr")[1:]
def get_crowded_cities(rr,limit):
    cities=[]    
    for kk in rows:
            cells = kk.find_all("td")
            cities.append(cells[1].find('a').text.strip())
    return cities[:limit]

    
cities = get_crowded_cities(rows,10)
print(cities)

ville1='Paris'
ville2='Lyon'

def get_distance(ville1,ville2):
        urlapi="https://fr.distance24.org/route.json?stops="+ville1+"|"+ville2
        response = requests.get(urlapi)
        data = json.loads(response.text)
        return data.get('distance')

for ville1 in cities:
    for ville2 in cities:
        if ville1!=ville2:
            dist = get_distance(ville1,ville2)
            print(ville1,ville2,dist)




