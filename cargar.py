#encoding:utf-8
import tkinter
from tkinter import *
from tkinter import messagebox
import os
from whoosh import index
from whoosh.qparser import MultifieldParser


from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.qparser import QueryParser
from whoosh import query
from whoosh.qparser.syntax import OrGroup
from whoosh.qparser.dateparse import DateParseError
from whoosh.qparser import GtLtPlugin

import urllib
from urllib import request
from bs4 import BeautifulSoup
import re
import os, ssl
import shutil

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

import datetime
import locale

locale.setlocale(locale.LC_TIME, "es_ES")
#fecha = "6 de noviembre de 2018"
#t = datetime.datetime.strptime(fecha, "%d de %B de %Y")




#############################################


URLS=["https://www.sensacine.com/noticias/",
    "https://www.sensacine.com/noticias/?page=2"]


def abrirUrl(url):
    try:
        f = urllib.request.urlopen(url)
        return f
    except:
        print("Error al conectarse a la página")
        return None


def soup(url):
    f = abrirUrl(url)
    return BeautifulSoup(f, "html.parser")



def cargar():
    respuesta = messagebox.askyesno(title="Confirmar",message="¿Esta seguro que quiere recargar los datos? \nEsta operación puede ser lenta")
    if respuesta:
        cargarDatos()
  


def cargarDatos():

    #Crear indices Whoosh
    # TEXT no puede llevar unique=True
    schema = Schema(
        categoria=TEXT(stored=True),
        fecha=DATETIME(stored=True),
        titulo=TEXT(stored=True),
        resumen=TEXT(stored=True))

    #eliminamos el directorio del índice, si existe
    if os.path.exists("indexdir"):
        shutil.rmtree("indexdir")
    os.mkdir("indexdir")


    ix = create_in("indexdir", schema=schema)

    writer = ix.writer()
    a=0

    #Por cada una de las 3 páginas
    for i in URLS:
        sopa=soup(i)
        
        noticias = sopa.find("div", class_="sub-body").find("main", class_="content-layout cf").find("div", class_="gd-col-left").find_all("div", class_="card")

        for noticia in noticias:
            meta = noticia.find("div", class_="meta")

            titulo = meta.find("h2").a.string.strip()
            categoria = noticia.find("div", class_="meta-category").string.strip().replace("NOTICIAS - ", "")
            
            fechaStr = noticia.find("div", class_="meta-date").string.strip().split(",")[1].strip()
            fecha = datetime.datetime.strptime(fechaStr, "%d de %B de %Y")

            resumen = "Resumen desconocido"

            if meta.find("div", class_="meta-body"):
                resumen = meta.find("div", class_="meta-body").string.strip()


            writer.add_document(titulo=titulo, categoria=categoria,
                fecha=fecha, resumen=resumen)
            a+=1
                

    writer.commit()
    messagebox.showinfo('Ventana de información', 'Se han almacenado ' + str(a) + ' películas.')
