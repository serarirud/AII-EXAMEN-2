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
from datetime import datetime
import os, ssl
import shutil

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context
