# matcha-finder
## About
This program was born out of my girlfriend's need for finding matcha lattes in every city we travel to together and spending way too much time scouring reviews for a hint of how they taste. I set out to make a more convenient format for her to decide on which cafe to go to and skip the time needed to read multiple reviews. This program will list all cafes with matcha lattes within a city searched using Google Places and Geocaching APIs and output their rating, as well as adjectives people wrote in reviews about the matcha lattes in a convenient format underneath the cafes. The user can then further filter based off the keyword adjectives output or rating threshold to decide on the perfect cafe for them.

## Getting Started
#### Installation
1. Clone the repo
```sh
git clone https://github.com/cullendales/matcha-finder
```
2. Replace the ... with your API key for google in matcha-finder.py
```sh
API_KEY = "..."
```
3. Enable Google Places (new) and Google Geocaching APIs on your google account

## Roadmap
- [x] Implement API to make any city searchable for Matcha Lattes
- [x] Implement SQLite to store cafe data
- [x] Finish parser for adjectives in reviews about matcha lattes and display these to the user
- [x] Enable filtering of cafes by keywords and ratings
- [ ] Add working version to my website to allow users to test application without programming knowledge

## Notes
I am in the process of writing another version of this program's code to enable it to run on my website without the need for a user to enter their own API key. I will update this README with a link once it is complete. This will allow for easier access to using this program when travelling. Please be patient as I am still learning front-end development. For now, please enjoy the program and I wish you the best of luck in your search for the best matcha latte!
