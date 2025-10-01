# Exploring the music I listen to

Since the start of August 2025, I have been collecting my listening history from Spotify using their API. Using this along with my liked song data, I built a dashboard to display various graphs and stats about the music I listen to, as well as creating a small app to recommend new songs based on the style of other songs.

## Data collection and analysis
The Spotify API only provides listening history for up to 50 songs and within a 24 hour period, which posed a problem for collecting my listening history. To combat this, I wrote a script which every 3 hours will fetch from the API all the songs which have been listened to since the past time the script ran. These songs are then appended to songhistory.csv. This script also ensures the auth token is refreshed since it reguarly expires.

`get_databases` allows me to update all the other csvs, which hold infomation about the songs in my liked songs as well as the artists and albums associated with them. Additional infomation about each artists country of origin is fetched using the MusicBrainz API, and infomation about the musical properties each song has is fetched using the ReccoBeats API.

I cleaned the CSVs then analysed this data to find interesting trends in the sort of music I listen to, when I listen to it, and who it's by. I then organised my findings into the dashboard, which is explained below.

## Song Recommender
As part of the project I also built my own song recommender. The user can pick between 1 and 5 songs, and can then choose how much influence they want each song to have in the final result. Using this influence, a weighted average of 7 numerical features describing the songs is calculated (acousticness, danceability, energy, instrumentalness, liveness, speechiness ,valence). k-Nearest Neighbours is then performed to find 20 of the most similar songs from a large set of songs I have data for. 

I then again use Spotify's API to embed each of the recommended songs, so the user is able to listen to them directly from the website.

## Dashboard
Finally, I presented everything in a single dashboard. I wanted to use this as an opportunity to practice my webdev skills, and so built everything myself using HTML / CSS / Javascript. I then used Flask to serve the site and handle my Python backend, which is where all the analysis took place. I also learnt how to create a Dash App using Plotly, so that I was able to create a listening history calender, which updates as the user select different songs and different months to view.

### Features:
* Graphs showing the hours I mostly commonly listen to music, and how this changes week-on-week
* A world map heatmap showing the origins of my liked artists
* Some quick stats about my listening history, and my top 5 songs / artists / albums in different categories
* A calender showing how many times on each day I listened to the selected song
* A song recommender

## Website
The website upon intially being loaded:

![alt text](https://github.com/annaFlett/spotify-api/blob/main/images/image1.png)

After songs have been selected and submitted to the recommender, the embded player appears and allows users to look through the recommended songs. You can also select a song to see the listening history for it and change the category of the top 5 table:

![alt text](https://github.com/annaFlett/spotify-api/blob/main/images/image2.png)

The site can be run locally by changing directory to `flask_side`, then running `flask --app flaskr run --debug` in terminal.
