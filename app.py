
import base64
from io import BytesIO
from flask import Flask
import numpy as np
from caelus.math_core.fields import make_random_psi
from caelus.math_core.operators import laplacian
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = Flask(__name__)

@app.route('/')
def plot():
    psi = make_random_psi((64, 64))
    lap = laplacian(psi)

    fig, ax = plt.subplots()
    ax.imshow(lap.real)
    
    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"<img src='data:image/png;base64,{data}'/>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
