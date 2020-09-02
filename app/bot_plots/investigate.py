#import sqlite3, sys, os, string
from collections import Counter
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

import networkx as nx
from networkx.algorithms import community
import scipy.sparse
import sklearn.datasets
import sklearn.feature_extraction.text

import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

import umap
import umap.plot

import holoviews as hv
from holoviews import opts
from bokeh.plotting  import show
from bokeh.models import HoverTool

hv.extension("bokeh")

defaults = dict(width=600, height=600)
hv.opts.defaults(
    opts.EdgePaths(**defaults), opts.Graph(**defaults), opts.Nodes(**defaults))
