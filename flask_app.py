import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs

app = Flask(__name__)
CORS(app)

# Define headers for requests to avoid 529 errors
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

@app.route('/', methods=['GET'])
@cross_origin()
def homepage():
    return render_template("index.html")

@app.route('/review', methods=['POST', 'GET'])
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchstring = request.form['content'].replace(" ", "")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchstring

            # Updated with headers and requests instead of uReq
            flipkartpage = requests.get(flipkart_url, headers=headers).text
            flipkart_html = bs(flipkartpage, "html.parser")

            bigboxes = flipkart_html.find_all("div", {"class": "cPHDOP col-12-12"})
            del bigboxes[0:3]
            if not bigboxes:
                return "No products found"

            box = bigboxes[0]
            productlink = "https://www.flipkart.com" + box.div.div.div.a["href"]

            prodres = requests.get(productlink, headers=headers)
            prodres.encoding = 'utf-8'
            prod_html = bs(prodres.text, "html.parser")

            commentboxes = prod_html.find_all("div", {"class": "col EPCmJX"})
            reviews = []

            for commentbox in commentboxes:
                try:
                    name = commentbox.find_all("p", {"class": "row gHqwa8"})[0].text
                except:
                    name = 'No Name'

                try:
                    rating = commentbox.div.div.text
                except:
                    rating = 'No rating'

                try:
                    commenthead = commentbox.div.p.text
                except:
                    commenthead = 'No comment heading'

                try:
                    commenttag = commentbox.find_all("div", {"class": "row"})[1].div.div.div.text
                except:
                    commenttag = 'No comment'

                mydict = {
                    "Product": searchstring,
                    "Name": name,
                    "Rating": rating,
                    "CommentHead": commenthead,
                    "Comment": commenttag
                }
                reviews.append(mydict)

            return render_template('results.html', reviews=reviews)

        except Exception as e:
            return f"Something went wrong: {e}"

    else:
        return render_template('index.html')

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
