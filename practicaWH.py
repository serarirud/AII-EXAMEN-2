#encoding:utf-8
import tkinter as tk
from tkinter import END, messagebox
from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.qparser import QueryParser
from whoosh.qparser.default import MultifieldParser
import re
from datetime import datetime
import locale
import os, ssl
import shutil
import urllib
from urllib import request
from bs4 import BeautifulSoup

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


locale.setlocale(locale.LC_TIME, "es_ES")

INDEXDIR = 'indexdir'

URLS=["https://www.sensacine.com/noticias/",
    "https://www.sensacine.com/noticias/?page=2"]

def crear_listbox_con_scrollbar(data: list[tuple]) -> None:
    main_window = tk.Tk()
    scrollbar = tk.Scrollbar(main_window)
    scrollbar.pack(side='right', fill='both')
    listbox = tk.Listbox(main_window, yscrollcommand=scrollbar.set, width=200)
    for d in data:
        listbox.insert(END, str(d))
    
    listbox.pack(side='left', fill='both')
    scrollbar.config(command=listbox.yview)
    main_window.mainloop

def create_search_window_one_entry(label, command) -> None:
    def listar(event):
        try:
            data = command(entry.get())
            window.destroy()
            crear_listbox_con_scrollbar(data)
        except ValueError as e:
            messagebox.showwarning('Warning', str(e))
            window.destroy()
            create_search_window_one_entry(label, command)
    window = tk.Tk()

    entry = create_entry(window, label, listar)
    window.mainloop()

def create_search_and_delete_window(search_label, search_command, delete_command, title: str, question: str) -> None:
    def listar(event):
        search_arg = search_entry.get()
        try:
            window.destroy()
            data = search_command(search_arg)
            crear_listbox_con_scrollbar(data)
            answer = messagebox.askyesno(title, question)
            if answer:
                delete_command(data, search_arg)

        except ValueError as e:
            messagebox.showwarning('Warning', str(e))
            create_search_and_delete_window(search_label, search_command, delete_command, title, question)
    window = tk.Tk()

    search_entry = create_entry(window, search_label, listar)
    create_option_button(window, 'Borrar', listar)

    window.mainloop()

def create_entry(window: tk.Tk, label: str, command) -> None:
    label_widget = tk.Label(window)
    label_widget['text'] = label
    label_widget.pack(side='left')
    entry = tk.Entry(window)
    entry.bind("<Return>", command)
    entry.pack(side='left')
    return entry

def create_option_button(window: tk.Tk, text: str, command, side='left') -> None:
    option = tk.Button(window)
    option['text'] = text
    option['command'] = command
    option.pack(side=side)

def create_label(window: tk.Tk, text: str, side='left') -> None:
    label = tk.Label(window)
    label['text'] = text
    label.pack(side=side)

def create_spinbox(label: str, options_command, command):
    def listar(event):
        data = command(spinbox.get())
        window.destroy()
        crear_listbox_con_scrollbar(data)
            
    window = tk.Tk()
    create_label(window, label, side='top')
    spinbox = tk.Spinbox(window, width=200, values=options_command())
    spinbox.pack(side='top')
    spinbox.bind('<Return>', listar)

def search(indexdir: str, fields_to_search, str_query: str, limit: int, return_fields: list) -> list[tuple]:
    ix = open_dir(indexdir)
    with ix.searcher() as searcher:

        results: list[tuple] = list()
        if isinstance(fields_to_search, list):
            query = MultifieldParser(fields_to_search, ix.schema).parse(str_query)
        else:
            query = QueryParser(fields_to_search, ix.schema).parse(str_query)
            
        for hit in searcher.search(query, limit=limit):
            datos = [str(hit[c]) for c in return_fields]
            print(type(datos))
            results.append(tuple(datos))
    
    return results

def start():
    main_window = tk.Tk()

    menu = tk.Menu(main_window, tearoff=0)

    datos = tk.Menu(menu, tearoff=0)
    datos.add_command(label='Cargar', command=cargar )
    datos.add_command(label='Salir', command=main_window.destroy)

    menu.add_cascade(label='Datos', menu=datos)

    busc = tk.Menu(menu, tearoff=0)
    busc.add_command(label='Titulo', command=lambda: create_search_window_one_entry('Título: ', buscar_por_titulo))
    busc.add_command(label='Título o resumen', command=lambda: create_search_window_one_entry('Título o resumen: ', buscar_por_resumen_o_titulo))
    busc.add_command(label='Fecha', command=lambda: create_search_window_one_entry('Fecha (dd MMM aaaa): ', buscar_por_fecha))
    busc.add_command(label='Categorías', command=lambda: create_spinbox('Categorias', get_categorias, buscar_por_categoria))

    menu.add_cascade(label='Buscar', menu=busc)

    
    eliminar = tk.Menu(menu, tearoff=0)
    eliminar.add_command(label='Eliminar noticias', command=lambda: create_search_and_delete_window('Título', buscar_por_titulo
                                                                    , delete_by_titulo, 'Confirmación de borrado'
                                                                    , '¿Estás seguro de borrar los siguientes datos?'))
    menu.add_cascade(label='Eliminar noticias', menu=eliminar)
    
    main_window.config(menu=menu)

    main_window.mainloop()

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
            fecha = datetime.strptime(fechaStr, "%d de %B de %Y")

            resumen = "Resumen desconocido"

            if meta.find("div", class_="meta-body"):
                resumen = meta.find("div", class_="meta-body").string.strip()


            writer.add_document(titulo=titulo, categoria=categoria,
                fecha=fecha, resumen=resumen)
            a+=1
                

    writer.commit()
    messagebox.showinfo('Ventana de información', 'Se han almacenado ' + str(a) + ' películas.')

def buscar_por_titulo(palabras: str) -> list[tuple[str, str, str]]:
    return search(INDEXDIR, 'titulo', palabras.replace(' ', ' OR '), None, ['categoria', 'fecha', 'titulo'])

def buscar_por_resumen_o_titulo(frase: str) -> list[tuple[str, str, str, str]]:
    return search(INDEXDIR, ['titulo', 'resumen'], frase, None, ['categoria', 'fecha', 'titulo', 'resumen'])

def buscar_por_fecha(fecha: str) -> list[tuple[str, str, str]]:
    if not re.fullmatch('\d{2} [a-zA-Z]{3} \d{4}', fecha):
        raise ValueError('La fecha tiene que seguir el formato dd MMM aaaa')

    print(fecha)
    fecha = datetime.strptime(fecha, '%d %b %Y')
    fecha = datetime.strftime(fecha, '%Y%m%d')
    return search(INDEXDIR, 'fecha', '{' + f'{fecha}TO]', None, ['categoria', 'fecha', 'titulo'])

def get_categorias() -> list[str]:
    ix = open_dir(INDEXDIR)
    all_docs = ix.searcher().documents()
    categorias = [hit['categoria'] for hit in all_docs]
    ix.close()
    return categorias

def buscar_por_categoria(categoria: str) -> list[tuple[str, str, str]]:
    return search(INDEXDIR, 'categoria', categoria.capitalize(), None, ['categoria', 'fecha', 'titulo'])

def delete_by_titulo(data, titulo):
    ix = open_dir(INDEXDIR)
    for _, _, titulo in data:
        ix.delete_by_term('titulo', titulo.replace(' ', ' OR '))

start()