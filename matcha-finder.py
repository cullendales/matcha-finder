import sqlite3
import requests
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

stop_words = set(stopwords.words('english'))
nltk.download('punkt')

API_KEY = "..." #Insert your API key here to use program

class Cafe:
    def __init__(self, name, address, lon, lat, rating, has_matcha, reviews):
        self.name = name
        self.address = address
        self.lon = lon
        self.lat = lat
        self.rating = rating
        self.has_matcha = has_matcha
        self.keywords = []

    def extract_keywords(self, reviews):
        tokenized = nltk.word_tokenize(reviews.lower())

        wordsList = [w for w in wordsList if not w in stop_words]
        matcha_reviews = [w for w in wordsList if 'matcha' in wordsList]

        tagged_reviews = nltk.pos_tag(matcha_reviews)

        for i, (word, tag) in enumerate(tagged_reviews):
            if word == "matcha":
                if i > 0 and word[i-1][1] == "JJ":
                    self.keywords.append(word[i-1][0])
                if i > 0 and word[i+2][1] == "JJ":
                    self.keywords.append(word[i+2][0])      

class MatchaFinder:
    def __int__(self, city):
        self.api_key = API_KEY
        self.conn = sqlite3.connect('matcha_lattes.db')
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS matcha_lattes(
            NAME TEXT,
            ADDRESS TEXT,
            LON FLOAT,
            LAT FLOAT,
            RATING REAL,
            HAS_MATCHA BOOL,
            KEYWORDS TEXT                                                            
        );''')
        self.conn.commit()

    def get_city_coords(self, city):
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {"address": city, "key": self.api_key}
        res = requests.get(url, params=params)
        data = res.json()
        if data['status'] == 'OK':
            loc = data['results'][0]['geometry']['location']
            return loc['lat'], loc['lon']
        else:
            raise Exception(f"Failed to get coordinates: {data['status']}")

    def search_matcha_cafes(self, lat, lon, radius=5000):
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "key": self.api_key,
            "location": f"{lat},{lon}",
            "radius": radius,
            "type": "cafe",
            "keyword": "matcha latte"
        }

