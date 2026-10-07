import urllib.request
import json

url = "http://localhost:8000/api/v1/people/44cb6ff7-c06c-4c3f-a814-cabdad6b0186/timeline"
# Need auth token!
# Let's bypass auth by calling it directly or getting a token via login.
