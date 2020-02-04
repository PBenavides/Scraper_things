import requests
import datetime
import re
import time
import pandas as pd

from datetime import timedelta
from bs4 import BeautifulSoup

def pass_datetimes_make_links(initial_time, final_time):
    # A este función se le deben de pasar dos objetos datetime.datetime especificados respectivamente
    date_list = [] #Aca pondre las fechas que generaré
    time_obj = initial_time #Es mi tiempo inicial
    while time_obj <= final_time:  #Si tengo la fecha inicial menor que la final
        fecha_formateada = time_obj.strftime("%Y-%m-%d") #formateo mi tiempo
        date_list.append(fecha_formateada)
        time_obj += timedelta(days=1) #Voy aumentando los días hasta que cumpla la condicion
    #Haré los links finalmente y los pondré denuevo en una lista.
    lista_links_dias = ['https://www.enlima.pe/calendario-cultural/dia/'+fecha+'?page=1' for fecha in date_list]
    return lista_links_dias

#Esto me botará una lista con todos los links padres a los que entraré primero.

#Tengo una lista de links en general de los dias
def scrap_me_internal_links(lista_links_dias):
    #creo el diccionario final
    dict_fecha_links_internos = {}
    #Para cada dia dentro de la lista de los links del dia
    for link_del_dia in lista_links_dias:
        time.sleep(1)
        #crea la conexion
        response = requests.get(link_del_dia)
        soup = BeautifulSoup(response.text,"html.parser")
        #crea una lista para los links de los eventos del dia
        lista_links_eventos_del_dia = []
        #para cada coneccions, hay varios links internos
        for i in soup.find('div',{'class':'innera'}).find_all('td',{'class':'views-field views-field-title views-align-left'}):
            #Pondré esos links internos en la lista anteriormente creda
            for a in i.find_all('a',href=True):
                lista_links_eventos_del_dia.append('https://www.enlima.pe' + str(a['href']))
            #hasta acá tengo una lista de todos los links internos por dia.
        dict_por_dia = scrap_me_los_eventos(lista_links_eventos_del_dia,i=0)
        #Para toda la data generada por dia, ponmela en un diccionario aparte.
        dict_fecha_links_internos[link_del_dia[46:56]] = dict_por_dia
    return dict_fecha_links_internos

#Esta funcion está hecha para scrapear una lista de links internos (de eventos) y
#botar la data que se obtenga dentro de un dict. 
def scrap_me_los_eventos(lista_links_eventos_del_dia,i=0):
    dict_scrap_final = {}
    dict_scrap_interno = {}
    for link_evento in lista_links_eventos_del_dia:
        i+=1
        response = requests.get(link_evento)
        soup = BeautifulSoup(response.text,"html.parser")
        titulo = soup.find('h1',{'class':'page__title title'}).text
        basic_info = [div.text for div in soup.find_all('div',{'class':'field-item even'})[2:7]]
        tipo, lugar, intervalo_fecha, precio, descripcion_basica = map(str,basic_info)
        to_parse = [elem.text for elem in soup.find('div',{'class':
                                                           'ds-1col node node-lugar view-mode-reference clearfix'}).find_all('div',
                                                                                                                             {'class':'field-item even'})]
        pattern = re.compile(r'-\d*.\d*,-\d*.\d*',re.MULTILINE|re.DOTALL) #Tengo el patron de las coordenadas
        script = soup.find_all('script',text=pattern) #saco el script que contiene el patron
        try: 
            coordenadas_list = re.findall(pattern,str(script))[0].split(',') #Lo obtengo y lo pongo dentro de una lista.
        except:
            coordenadas_list = ['nohay','nohay']
        dict_scrap_final['evento'+str(i)] = {'nombre_evento':titulo,'tipo_evento':tipo,'lugar_evento':lugar,
                                        'intervalo_fecha':intervalo_fecha,'precio':precio,
                                         'descripcion_basica':descripcion_basica,'data_extra':to_parse,
                                         'coordenadas':coordenadas_list}
    return dict_scrap_final

#Genero segun dos dias:
initial_time = datetime.datetime(2019,1,2)
final_time = datetime.datetime(2019,1,4)

lista_links_dias = pass_datetimes_make_links(initial_time,final_time)
dict_final3 = scrap_me_internal_links(lista_links_dias)

#Finalmente los pongo dentro de un csv

for k,v in dict_final3.items():
    df = pd.DataFrame().from_dict(v,orient='index')
    df.to_csv('enlima_'+k+'.csv',index=False)