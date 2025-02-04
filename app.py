from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from catboost import CatBoostClassifier, Pool
from sklearn.ensemble import VotingClassifier, RandomForestClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import joblib

app = Flask(__name__)

# Load the dataset and pre-trained models
df = pd.read_csv('Welltrain.csv')

cat_model = CatBoostClassifier()
cat_model.load_model("catboost_model.cbm")
voting_clf = joblib.load("voting_clf.pkl")

def get_user_info(username):
    user_row = df[df['Username'] == username]
    if user_row.empty:
        return None
    
    return {
        "user_id": int(user_row['UserID'].values[0]),  # Convert to Python int
        "username": str(user_row['Username'].values[0]),
        "creation_date": str(user_row['CreationDate'].values[0]),  # Convert date to string
        "following_count": int(user_row['FollowingCount'].values[0]),
        "follower_count": int(user_row['FollowersCount'].values[0]),
        "tweet_timestamp" : str(user_row['TweetTimestamp'].values[0]),
        "location" : str(user_row['Location'].values[0])
    }

@app.route('/get_user_info', methods=['POST'])
def get_user_info_route():
    data = request.get_json()
    name = data.get("name", "")
    user_info = get_user_info(name)
    
    if user_info:
        return jsonify(user_info)
    else:
        return jsonify({"status": "not found"}), 404

# Specify the criteria for identifying bots
import re
#if you want more bio and tweet get it from Bio&Tweet.txt file
bot_bio = [
    "Click here for the best investment tips! 💸 Follow for financial freedom! #InvestSmart",
    "💥 Discover hot new trends every hour! 🚨 Follow me for more updates & amazing deals! #TrendingNow",
    "Earn cash by following me and retweeting! ✨💵 #Follows #RT4RT",
    "Join me in discovering secret hacks for life! 🌟 Follow to get tips! #LifeHacks",
    "🚀 Bringing you the latest news in tech & finance! DM for collaborations! #PublicRelations",
    "🔔 Always on the lookout for new followers! Follow me for tips on living your best life! 🌟 #LifeGoals",
    "🌐 Automating success! Get exclusive content and tips by following! #MarketingStrategy",
    "Discover the secrets of smart investing! 💸 Follow for exclusive tips. #InvestSmart",
    "🚨 Hot trends & amazing deals right here! Follow to stay updated! 💥 #Trending",
    "Turn those follows into cash! 💵✨ #Follows #Retweet",
    "Learn life’s hidden hacks! 🌟 Follow for fresh tips every day! #LifeHacks",
    "Latest in tech & finance delivered! 🚀 DM for collabs! #PublicRelations",
    "Follow to unlock exclusive lifestyle tips! 🌟 #LifeGoals",
    "📈 Master your strategy! Automated success tips await. #MarketingMagic",
    "For top investing tips, follow now! 💸 Financial freedom is just a click away. #InvestSmart"
]
bot_urls = [
    "http://best-offer-2023.win/redeem-now",
    "http://limited-time-offer.com/claim-your-gift",
    "http://login-secure-verify.bankconfirm.com/user-confirm",
    "http://giftcard-survey.com/win-a-gift",
    "http://miracle-cure-health.com/order-today",
    "http://free-software-hub.com/download-now",
    "http://quick-cash-growth.com/invest-now",
    "http://exclusive-event-invite.com/register",
    "http://paypa1-secure.com/login",
    "http://fileshare-portal.com/download-file",
    "http://limited-time-promo.com/claim-your-gift"
]

def classify_bot(row):
    bio = row['Bio']
    tweet = row['Tweets']
    
    # Remove hashtags from the tweet
    tweet_without_hashtags = re.sub(r'#\S+', '', tweet)  # Remove any hashtag (e.g., #InvestSmart)
    
    if any(bio in bot_bio for bot_bio in bot_bio) or \
       any(url in tweet_without_hashtags for url in bot_urls):
        return 1  # bot
    else:
        return 0  # human

# Apply the classification function to the DataFrame
df['is_bot'] = df.apply(classify_bot, axis=1)
X = df[['Bio', 'Tweets']]
y = df['is_bot']
X['Bio_length'] = X['Bio'].apply(len)
X['Tweet_length'] = X['Tweets'].apply(len)
X_train, X_test, y_train, y_test = train_test_split(X[['Bio_length', 'Tweet_length']], y, test_size=0.2, random_state=42)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()  # Get JSON data
    bio = data.get('bio', '')
    tweet = data.get('tweet', '')
    bio_length = len(bio)
    tweet_length = len(tweet)

    # Simple bot classification based on bio and tweet text
    is_bot_simple = classify_bot({'Bio': bio, 'Tweets': tweet})

    if is_bot_simple == 0:
        features = np.array([[bio_length, tweet_length]])
        is_bot_cat = cat_model.predict(features)[0]
        is_bot_svm = voting_clf.predict(features)[0]
        is_bot_final = int(is_bot_cat or is_bot_svm)
    else:
        is_bot_final = is_bot_simple

    return jsonify({'result': 'Spam Bot Detected' if is_bot_final else 'Genuine User'})

if __name__ == '__main__':
    app.run(debug=True)
