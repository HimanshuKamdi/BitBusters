from flask import Flask, render_template, request
import plotly
import plotly.graph_objs as go
import plotly.express as px
import json
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


@app.route('/', methods=['GET', 'POST'])
def home():
    search_query = request.form.get('search_query')
    data1 = [
        go.Bar(
            y=["Topic1", "Topic2", "Topic3", "Topic4"],
            x=[45.2, 19.1, 19.5, 16.2],
            orientation='h'
        )
    ]
    data2 = [
        go.Bar(
            x=["Vid1", "Vid2", "Vid3", "Vid4"],
            y=[43, 21, 19, 16],
        )
    ]
    graphJSON1 = json.dumps(data1, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON2 = json.dumps(data2, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('home.html', videos=videos, graphJSON1=graphJSON1,graphJSON2=graphJSON2, search_query=search_query)


@app.route('/video/<int:video_id>')
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
