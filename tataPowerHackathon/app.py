from flask import Flask, render_template, request, redirect, url_for
import plotly
import plotly.graph_objs as go
import plotly.express as px
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
import json
import pickle
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
import googleapiclient.discovery
import requests
app = Flask(__name__)
API_KEY = "AIzaSyDN8fDz5RO83ESiCTu4cQXp8QrWfJJtycg"
base_url = "https://www.googleapis.com/youtube/v3/"
youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=API_KEY)
videos = [
    {
        'id': 1,
        'title': 'Video 1',
        'description': 'Description for Video 1',
        'url': 'https://www.youtube.com/watch?v=video1',
        'views': 1500
    },
    {
        'id': 2,
        'title': 'Video 2',
        'description': 'Description for Video 2',
        'url': 'https://www.youtube.com/watch?v=video2',
        'views': 3500
    },
    {
        'id': 3,
        'title': 'Video 3',
        'description': 'Description for Video 3',
        'url': 'https://www.youtube.com/watch?v=video2',
        'views': 2500
    },
    {
        'id': 4,
        'title': 'Video 4',
        'description': 'Description for Video 4',
        'url': 'https://www.youtube.com/watch?v=video2',
        'views': 500
    },
    {
        'id': 5,
        'title': 'Video 5',
        'description': 'Description for Video 5',
        'url': 'https://www.youtube.com/watch?v=video2',
        'views': 150
    }
]
topics=["Renewable Energy","Sustainable Energy","Renewable and Sustainable Energy","Solar Energy","Wind Energy","Biogas Energy","Conservable Resources","Hydro Power","Clean Energy","Green Energy"]
def get_avg_views_per_topic():
    scores=[]
    for i in range(10):
        with open(f"./data/Cache/{i}.json","r") as f:
            data=json.load(f)

        sum=0
        for i in range(min(10,len(data))):
            data[i]["items"]
            sum+=int(data[i]["items"][0]["statistics"]["viewCount"])

        scores.append(sum/10)
    return scores
def get_avg_likes_per_topic():
    scores=[]
    for i in range(10):
        with open(f"./data/Cache/{i}.json","r") as f:
            data=json.load(f)

        sum=0
        count=0
        for i in range(min(10,len(data))):
            data[i]["items"]
            if "likeCount" in data[i]["items"][0]["statistics"].keys():
                sum+=int(data[i]["items"][0]["statistics"]["likeCount"])
                count+=1
        if count==0:
            scores.append(0)
        else:
            scores.append(sum/10)

    return scores

def get_avg_comments_per_topic():
    scores=[]
    for i in range(10):
        with open(f"./data/Cache/{i}.json","r") as f:
            data=json.load(f)

        sum=0
        count=0
        for i in range(min(10,len(data))):
            data[i]["items"]
            if "commentCount" in data[i]["items"][0]["statistics"].keys():
                sum+=int(data[i]["items"][0]["statistics"]["commentCount"])
                count+=1
        if count==0:
            scores.append(0)
        else:
            scores.append(sum/10)
    return scores
    
def find_best_match(input_query,topics):
    input_query=input_query.lower()
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform([input_query] + topics)
    cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    # Find the topic with the highest similarity
    max_index = cosine_similarities.argmax()
    max_score = cosine_similarities[max_index]
    matched_topic = topics[max_index]
    return [max_score,max_index]

search_query=""
@app.route('/', methods=['GET', 'POST'])
def home():
    views_scores=get_avg_views_per_topic()
    like_scores=get_avg_likes_per_topic()
    comment_scores=get_avg_comments_per_topic()
    global search_query 
    search_query = request.form.get('search_query')
    print(search_query)
    small_topics=[x.lower() for x in topics]
    if search_query is not None:
        res=find_best_match(search_query,small_topics)
        print(res[0],res[1])
        if res[0]<0.35:
            print("Nothing Found")
        else:
            print(f"Matched with {topics[res[1]]}")
            return redirect(url_for('topic',topic_id=res[1]))
    
    data1 = [
        go.Bar(
            x=topics,
            y=views_scores
        )
    ]
    data2 = [
        go.Bar(
            x=topics,
            y=like_scores
        )
    ]
    data3 = [
        go.Bar(
            x=topics,
            y=comment_scores
        )
    ]
    graphJSON1 = json.dumps(data1, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON2 = json.dumps(data2, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON3 = json.dumps(data3, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('home.html', videos=videos, graphJSON1=graphJSON1, graphJSON2=graphJSON2,graphJSON3=graphJSON3)


@app.route('/topic/<int:topic_id>', methods=['GET', 'POST'])
def topic(topic_id):
    global search_query
    srq=search_query
    global video_title
    top_few=[]
    with open(f'./data/Cache/{topic_id}.json', 'r') as f:
        data = json.load(f)
    for vid in data[:5]:
        id=vid["items"][0]["id"]
        if "title" in vid["items"][0]["snippet"].keys():
            title=vid["items"][0]["snippet"]["title"]
            
        else:
            title=None
        if "description" in vid["items"][0]["snippet"].keys():
            desc=vid["items"][0]["snippet"]["description"][:min(180,len(vid["items"][0]["snippet"]["description"]))]+"...."
        else:
            desc=None
        if "thumbnails" in vid["items"][0]["snippet"].keys():
            img=vid["items"][0]["snippet"]["thumbnails"]["medium"]["url"]
        else:
            img=None
        
        if "viewCount" in vid["items"][0]["statistics"].keys():
            viewCount=vid["items"][0]["statistics"]["viewCount"]
        else:
            viewCount=None
        if "likeCount" in vid["items"][0]["statistics"].keys():
            likeCount=vid["items"][0]["statistics"]["likeCount"]
        else:
            likeCount=None
        
        if "commentCount" in vid["items"][0]["statistics"].keys():
            commentCount=vid["items"][0]["statistics"]["commentCount"]
        else:
            commentCount=None
        
        top_few.append({"id":id,"title":title,"desc":desc,"img":img,"views":viewCount,"likes":likeCount,"comments":commentCount})
    
    videos=top_few
    with open(f'./data/Cache/{topic_id}tags.pkl', 'rb') as f:
        tags = pickle.load(f)
    
    df_topic_model=pd.read_csv(f"./data/Cache/{topic_id}topicmodel.csv")
    df_topic_model.columns=["Topic","Presence%"]

    tags= dict(sorted(tags.items(), key=lambda item: item[1],reverse=True))
    df_tags=pd.Series(tags)
    top_tags=df_tags[:min(len(df_tags),10)]

    data1 = [
        go.Bar(
            y=top_tags,
            x=top_tags.index
        )
    ]
    data2 = [
        go.Bar(
            y=df_topic_model['Topic'],
            x=df_topic_model['Presence%'],
            orientation='h',
        )
    ]
    graphJSON1 = json.dumps(data1, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON2 = json.dumps(data2, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('topic.html', videos=videos, graphJSON1=graphJSON1,graphJSON2=graphJSON2,topic_id=topic_id, search_query=srq)


def gen_word_cloud(key,data):
    obj=data[key]
    comments=""
    if "items" in obj.keys():
        for item in obj["items"]:
            comments+=((item['snippet']['topLevelComment']['snippet']['textDisplay']))

    wordcloud = WordCloud(width = 400, height = 400, 
                background_color ='white', 
                stopwords = None, 
                min_font_size = 10).generate(comments)
    image_path = "static/wordcloud.png"
    wordcloud.to_file(image_path)
    
video_title=""

@app.route('/video/<int:topic_id>/<string:video_id>')
def video(topic_id,video_id):
    with open(f"./data/Cache/{topic_id}_video_sentanal.json","r") as f:
        sentiments=json.load(f)
    sentiment=sentiments[video_id]
    print(sentiment)
    file='./static/wordcloud.png'
    if os.path.exists(file):
        os.remove(file)
        
    with open(f"./data/Cache/{topic_id}_comments.json","r") as f:
        data=json.load(f)

    gen_word_cloud(video_id,data)
    data1 = [
            go.Pie(
                labels=list(sentiment.keys()),
                values=list(sentiment.values())
            )
        ]
    
    graphJSON1 = json.dumps(data1, cls=plotly.utils.PlotlyJSONEncoder)
  
    return render_template('video.html',graphJSON1=graphJSON1,title=f"Analytics for {video_title}")




def get_video_stats(video_url):
    video_id = video_url.split("?v=")[1]
    endpoint = "commentThreads"

    params = {
        "key": API_KEY,
        "part": "snippet",
        "video_id":video_id,
        "maxResults":20,
    }

    response = requests.get(base_url + endpoint, params=params)
    data = response.json()
    return data


def get_video_info(video_url, api_key):
    video_id = video_url.split("?v=")[1]
    base_url = "https://www.googleapis.com/youtube/v3/"
    endpoint = "videos"

    params = {
        "key": api_key,
        "part": "snippet,statistics",
        "id": video_id
    }

    response = requests.get(base_url + endpoint, params=params)
    data = response.json()

    # Extract and return the information
    if 'items' in data and len(data['items']) > 0:
        video_info = {
            "title": data['items'][0]['snippet']['title'],
            "description": data['items'][0]['snippet']['description'],
            "statistics": data['items'][0]['statistics'],
            "thumbnail_medium": data['items'][0]['snippet']['thumbnails']['medium']['url']
        }
        return video_info
    else:
        return None


def get_commenter_comments(api_key, channel_id):
      comment_params = {
          "key": api_key,
          "part": "snippet",
          "channelId": channel_id,
          "maxResults": 10
      }
      comment_endpoint = "search"
      comment_response = requests.get(base_url + comment_endpoint, params=comment_params)
      comment_data = comment_response.json()
      return comment_data

@app.route('/url_analysis',methods=['GET', 'POST'])
def url_analysis():
    search_query = request.form.get('search_query')
    res=None
    stats=None
    if search_query is not None:
        data=get_video_stats(search_query)
        commentors=[]
        for i in range(min(5,len(data['items']))):
            commentors.append(data['items'][i]['snippet']['topLevelComment']['snippet']['authorChannelId']['value'])
        
        res={x:[] for x in commentors}
        for comm in commentors:
            commdata=get_commenter_comments(API_KEY,comm)
            for i in range(min(5,len(commdata['items']))):
                vid_title=commdata['items'][i]['snippet']['title']
                channel=commdata['items'][i]['snippet']['channelTitle']
                res[comm].append({"title":vid_title,"channel":channel})

        stats=get_video_info(search_query,API_KEY)
    
    return render_template('url_analysis.html',res=res,stats=stats)

if __name__ == '__main__':
    app.run(debug=True)
