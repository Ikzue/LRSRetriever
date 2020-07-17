from flask import send_file
import io, os
import matplotlib.pyplot as plt
from PIL import Image


def image_circular_diagram(data):
    labels = []
    sizes = []
    for k, v in data.items():
        labels.append(k)
        sizes.append(v)


    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.savefig(os.path.join('flaskr', 'img', 'line_plot.png'))
    #return send_file(os.path.join('img','line_plot.png'), mimetype='image/jpeg')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return send_file(buf, mimetype='image/jpeg', cache_timeout=0)