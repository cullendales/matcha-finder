import sqlite3
import requests
import time
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

API_KEY = "..." #Insert your API key here to use program

def check_nltk_data():
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        try:
            nltk.download('punkt_tab')
        except:
            nltk.download('punkt')

    try:
        nltk.data.find('taggers/averaged_perceptron_tagger_eng')
    except LookupError:
        try:
            nltk.download('averaged_perceptron_tagger_eng')
        except:
            try:
                nltk.data.find('taggers/averaged_perceptron_tagger')
            except LookupError:
                nltk.download('averaged_perceptron_tagger')

    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')

check_nltk_data()
stop_words = stopwords.words('english')

class Cafe:
    def __init__(self, place_id, name, address, lon, lat, rating, reviews):
        self.place_id = place_id
        self.name = name
        self.address = address
        self.lon = lon
        self.lat = lat
        self.rating = rating
        self.keywords = []

        if reviews:
            self.extract_keywords(reviews)

    def extract_keywords(self, reviews):
        tokenized = word_tokenize(reviews.lower())

        wordsList = [w for w in tokenized if w not in stop_words and w.isalpha()]
        
        if 'matcha' not in wordsList:
            return

        tagged_reviews = nltk.pos_tag(wordsList)

        for i, (word, tag) in enumerate(tagged_reviews):
            if word == 'matcha':
                if i > 0 and tagged_reviews[i-1][1] in ["JJ", "JJR", "JJS"]:
                    self.keywords.append(tagged_reviews[i-1][0])
                if i < len(tagged_reviews) - 2 and tagged_reviews[i+2][1] in ["JJ", "JJR", "JJS"]:
                    self.keywords.append(tagged_reviews[i+2][0])
                if i < len(tagged_reviews) - 3 and tagged_reviews[i+3][1] in ["JJ", "JJR", "JJS"]:
                    self.keywords.append(tagged_reviews[i+3][0])      
      

class MatchaFinder:
    def __init__(self, api_key):
        self.api_key = api_key
        self.conn = sqlite3.connect('matcha_lattes.db')
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS matcha_lattes(
            ID TEXT PRIMARY KEY,
            NAME TEXT,
            ADDRESS TEXT,
            LON FLOAT,
            LAT FLOAT,
            RATING REAL,
            KEYWORDS TEXT
        );''')
        self.conn.commit()

    def coordinates(self, city):
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {"address": city, "key": self.api_key}

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data['status'] == 'OK':
            loc = data['results'][0]['geometry']['location']
            return loc['lat'], loc['lng']
        else:
            raise Exception (f"Coordinates could not be retrieved: {data['status']}")
        

    def get_reviews(self, place_id):
        url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            "key": self.api_key,
            "place_id": place_id,
            "fields": "reviews"
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
            
        if data.get("status") == "OK" and "result" in data:
            reviews = data["result"].get("reviews", [])
            review_text = " ".join([review.get("text", "") for review in reviews])
            return review_text if review_text.strip() else None
        else:
            raise Exception (f"Error: {data['status']}")

    def find_cafes(self, lat, lon):
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "key": self.api_key,
            "location": f"{lat},{lon}",
            "radius": 10000,
            "type": "cafe",
            "keyword": "matcha latte"           
        }

        cafes = []
        max_cafes = 50

        while len(cafes) < max_cafes:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get("status") != "OK":
                print("There is an API error: ", data.get("status"))
                if data.get("status") == "ZERO_RESULTS":
                    print("There are unfortunately no cafes serving a matcha latte in your area")
                break

            for result in data.get("results", []):
                reviews = self.get_reviews(result["place_id"])
                cafe = Cafe(
                    place_id = result["place_id"],
                    name = result.get("name", ""),
                    address = result.get("vicinity", ""),
                    rating = result.get("rating", 0),
                    lat = result["geometry"]["location"]["lat"],
                    lon = result["geometry"]["location"]["lng"],
                    reviews = reviews
                )
                cafes.append(cafe)
                self.add_cafe(cafe)

                time.sleep(0.1)

            if 'next_page_token' in data and len(cafes) < max_cafes:
                time.sleep(2)
                params['pagetoken'] = data['next_page_token']

                if 'location' in params:
                    del params['location']
                if 'radius' in params:
                    del params['radius']
                if 'type' in params:
                    del params['type']
                if 'keyword' in params:
                    del params['keyword']
            else:
                break

        return cafes
    
    def add_cafe(self, cafe):
        keywords_res = ", ".join(cafe.keywords) if cafe.keywords else ""
        self.cursor.execute('''INSERT OR IGNORE INTO matcha_lattes (ID, NAME, ADDRESS, LON, LAT, RATING, KEYWORDS)
                            VALUES (?,?,?,?,?,?, ?)''',
                            (cafe.place_id, cafe.name, cafe.address, cafe.lon, cafe.lat, cafe.rating, keywords_res))
        self.conn.commit()


if __name__ == "__main__":
    search = MatchaFinder(API_KEY)
    city = input("Please enter the city you would like to search in the format \"city, country\": ")
    print()
    print(f"Loading all cafes in {city} with delicious matcha lattes...")
    print()
    lat, lon = search.coordinates(city)
    cafes = search.find_cafes(lat, lon)

    for cafe in cafes:
        print(f"{cafe.name}\nAddress: {cafe.address}\nRating: {cafe.rating}")
        if cafe.keywords:
            print(f"What people are saying about their Matcha Lattes: {', '.join(cafe.keywords)}")
        print()

    answer = ""
    rating_filter = "1"
    user_keywords = []
    all_ratings = []
    correct_option = True

    while answer != "4":

        if correct_option:
            print("Would you like to filter results more?")

        print("1. Filter by adjectives in reviews describing a cafe's Matcha Latte")
        print("2. Filter by rating threshold")
        print("3. Reset all previous filters")
        print("4. Exit")
        print()

        correct_option = True

        answer = input("Enter 1, 2, 3, or 4: ")
        print()

        if answer == "1":
            user_keywords = input("Enter keywords to filter by seperated by a space: ").split()
            print()
            cafe_list = []
    
            for cafe in cafes:
                for key in user_keywords:            
                    if key in cafe.keywords and cafe.rating >= float(rating_filter):
                        if cafe.name not in cafe_list:
                            cafe_list.append(cafe.name)
            
            if not cafe_list:
                user_keywords.clear()
                print("No cafes match criteria.")
                print()
            else:
                for cafe in cafes:
                    if cafe.name in cafe_list and cafe.rating >= float(rating_filter):
                        print(f"{cafe.name}\nAddress: {cafe.address}\nRating: {cafe.rating}")
                        if cafe.keywords:
                            print(f"What people are saying about their Matcha Lattes: {', '.join(cafe.keywords)}")
                        print()
                    
        elif answer == "2":
            rating_filter = input("Enter a number from 1 - 5 to only see cafes with that rating or higher: ")
            print()
            contains_cafe = False
            all_ratings.append(rating_filter)


            if not user_keywords:      
                for cafe in cafes:
                    if cafe.rating >= float(rating_filter):
                            print(f"{cafe.name}\nAddress: {cafe.address}\nRating: {cafe.rating}")
                            if cafe.keywords:
                                print(f"What people are saying about their Matcha Lattes: {', '.join(cafe.keywords)}")
                            print()
                            contains_cafe = True

            else:
                for cafe in cafes:
                    for key in user_keywords:            
                        if key in cafe.keywords and cafe.rating >= float(rating_filter):
                            if cafe.name not in cafe_list:
                                cafe_list.append(cafe.name)
                                contains_cafe = True
                
                for cafe in cafes:
                    if cafe.name in cafe_list and cafe.rating >= float(rating_filter):
                        print(f"{cafe.name}\nAddress: {cafe.address}\nRating: {cafe.rating}")
                        if cafe.keywords:
                            print(f"What people are saying about their Matcha Lattes: {', '.join(cafe.keywords)}")
                        print()

                if not contains_cafe:
                    rating_filter = all_ratings[len(all_ratings) - 2]
                    print("No cafes match criteria.")
                    print()

        elif answer == "3":
            user_keywords.clear()
            rating_filter = "1"
                
        elif answer == "4":
            print("Thank you for using Matcha Finder")

        else:
            print("The number you entered was not an option. Please enter one of the options below:")
            correct_option = False

   








        
     
 