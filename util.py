import tkinter as tk
from tkinter import END, messagebox

def menu_example(*example):
    main_window = tk.Tk()
    
    menu = tk.Menu(main_window, tearoff=0)

    datos = tk.Menu(menu, tearoff=0)
    datos.add_command(label='Cargar', command=menu_example)
    datos.add_command(label='Listar', command=menu_example)
    datos.add_command(label='Salir', command=lambda: menu_example(main_window))

    menu.add_cascade(label='Datos', menu=datos)

    busc = tk.Menu(menu, tearoff=0)
    busc.add_command(label='Titulo', command=lambda: menu_example('Título: ', menu_example.search_by_title))
    busc.add_command(label='Fecha', command=lambda: menu_example('Fecha: ', menu_example.search_by_date))
    busc.add_command(label='Genero', command=menu_example)

    menu.add_cascade(label='Buscar', menu=busc)
    
    main_window.config(menu=menu)
    main_window.mainloop()

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
            create_search_window(label, command)
    window = tk.Tk()

    entry = create_entry(window, label, listar)
    window.mainloop()

def create_search_window(labels, command) -> None:
    def listar(event):
        args = [entry.get() for entry in entries]
        try:
            window.destroy()
            data = command(*args)
            crear_listbox_con_scrollbar(data)
        except ValueError as e:
            messagebox.showwarning('Warning', str(e))
            create_search_window(labels, command)
    window = tk.Tk()
    entries = check_labels_and_create_entries(labels, window, listar)
    window.mainloop()

def create_search_and_change_window(search_labels, change_labels, search_command, change_command, title: str, question: str) -> None:
    def listar(event):
        search_args = [entry.get() for entry in search_entries]
        change_args = [entry.get() for entry in change_entries]
        try:
            window.destroy()
            data = search_command(*search_args)
            crear_listbox_con_scrollbar(data)
            answer = messagebox.askyesno(title, question.format(*change_args))
            if answer:
                change_command(*search_args, *change_args)

        except ValueError as e:
            messagebox.showwarning('Warning', str(e))
            create_search_and_change_window(search_labels, change_labels, search_command, change_command, title, question)
    window = tk.Tk()

    search_entries = check_labels_and_create_entries(search_labels, window, listar)
    change_entries = check_labels_and_create_entries(change_labels, window, listar)

    window.mainloop()

def check_labels_and_create_entries(labels, window, command):
    if not isinstance(labels, list):
        labels = [labels]

    entries = []
    for label in labels:
        entries.append(create_entry(window, label, command))
    
    return entries

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

def create_radiobutton(window: tk.Tk, option_name: str, command) -> None:
    radiobutton = tk.Radiobutton(window)
    radiobutton['text'] = option_name
    radiobutton['command'] = command
    radiobutton.pack(side='top')

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

### WHOOSH SEARCH UTIL ###
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from whoosh.qparser.default import MultifieldParser

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