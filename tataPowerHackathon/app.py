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
app = Flask(__name__)

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

@app.route('/', methods=['GET', 'POST'])
def home():
    views_scores=get_avg_views_per_topic()
    like_scores=get_avg_likes_per_topic()
    comment_scores=get_avg_comments_per_topic()
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
    return render_template('home.html', videos=videos, graphJSON1=graphJSON1,graphJSON2=graphJSON2,graphJSON3=graphJSON3)


@app.route('/topic/<int:topic_id>', methods=['GET', 'POST'])
def topic(topic_id):
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
            desc=vid["items"][0]["snippet"]["description"][:min(100,len(vid["items"][0]["snippet"]["description"]))]+"...."
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
    return render_template('topic.html', videos=videos, graphJSON1=graphJSON1,graphJSON2=graphJSON2)


@app.route('/video/<string:video_id>')
def video(video_id):
    if 0 <= video_id < len(videos):
        data1 = [
            go.Pie(
                labels=["Negative Comments", "Positive Comments"],
                values=[43.2, 57.8]
            )
        ]
        data2 = [
            go.Bar(
                y=["Topic1", "Topic2", "Topic3", "Topic4"],
                x=[43.2, 21.1, 19.5, 16.2],
                orientation='h'
            )
        ]
        graphJSON1 = json.dumps(data1, cls=plotly.utils.PlotlyJSONEncoder)
        graphJSON2 = json.dumps(data2, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template('video.html', video=videos[video_id], graphJSON1=graphJSON1,graphJSON2=graphJSON2)
    else:
        return "Video not found"


if __name__ == '__main__':
    app.run(debug=True)
