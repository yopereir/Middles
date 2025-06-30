import os, requests, json
from createOptionsTrade import create_option_order
from getTopMovers import get_top_movers


gainers, losers = get_top_movers()
