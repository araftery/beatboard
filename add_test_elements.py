from app import app, db
from app.models import Post, Upvote, Star
import datetime

posts = [
		['Infinite Headbands (B.O.B. ft. 2 Chainz vs. Baauer & RL Grime)', 'https://soundcloud.com/quizzicalproductions/infinite-headbands-b-o-b-ft-2']
		["Can't Hold Us Can't Stop Us (Macklemore vs Miley Cyrus Mashup) by devcam22", 'https://soundcloud.com/devcam/cant-hold-us-cant-stop-us'],
		["If You Ain't First, You're Last (Van Halen x Imagine Dragons x John Mayer x Eminem....) by FBG$", 'https://soundcloud.com/fbgmoney-1/if-you-aint-first-youre-last'],
		['Best I Ever Had (matamatics remix) by D.Drizzy', 'https://soundcloud.com/d-drizzy-1/best-i-ever-had-matamatics'],
		['Touch the Sky (matamatics remix) by matamaticsmusic', 'https://soundcloud.com/matamaticsmusic/touch-the-sky-matamatics-remix']

for i in posts:
	title = i[0]
	url = i[1]

    post = Post(title = title, content = '', song_url = url, timestamp = int(datetime.datetime.utcnow().strftime("%s")), author_id = 1)
    db.session.add(post)

    upvote = Upvote(voter_id = 1, post = post)
    db.session.add(upvote)

db.session.commit()