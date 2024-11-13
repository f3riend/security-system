from pyngrok import ngrok

# Flask uygulamanızı çalıştırmadan önce ngrok tünelini başlatın
public_url = ngrok.connect(5000)
print(public_url.public_url)


# Flask uygulamanızı başlatın
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello World!"

if __name__ == '__main__':
    app.run(port=5000)
