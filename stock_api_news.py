#$ pip install unirest
import unirest
import requests
from datetime import date

response = unirest.get("https://myallies-breaking-news-v1.p.rapidapi.com/GetTopNews",
  headers={
    "X-RapidAPI-Host": "myallies-breaking-news-v1.p.rapidapi.com",
    "X-RapidAPI-Key": "0cc297accemsh4fd1e95e42615b5p12daa0jsnf64484a9ab93"
  }
)