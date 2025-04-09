import os
# import logging
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

# Configure logging (you can use print on Render if needed)
# logging.basicConfig(
#     filename='logs',
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     datefmt='%Y-%m-%d %H:%M:%S'
# )

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
@cross_origin()
def homepage():
    # logging.info("Homepage accessed")
    return render_template("index.html")

@app.route('/review', methods=['POST', 'GET'])
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchstring = request.form['content'].replace(" ", "")
            # logging.info(f"Search request received for product: {searchstring}")

            flipkart_url = "https://www.flipkart.com/search?q=" + searchstring
            uclient = uReq(flipkart_url)
            flipkartpage = uclient.read()
            uclient.close()
            flipkart_html = bs(flipkartpage, "html.parser")

            bigboxes = flipkart_html.find_all("div", {"class": "cPHDOP col-12-12"})
            del bigboxes[0:3]
            if not bigboxes:
                # logging.warning("No product boxes found")
                return "No products found"
            box = bigboxes[0]

            productlink = "https://www.flipkart.com" + box.div.div.div.a["href"]
            # logging.info(f"Product link: {productlink}")

            prodres = requests.get(productlink)
            prodres.encoding = 'utf-8'
            prod_html = bs(prodres.text, "html.parser")

            commentboxes = prod_html.find_all("div", {"class": "col EPCmJX"})
            # filename = searchstring + ".csv"
            
            reviews = []

            for commentbox in commentboxes:
                try:
                    name = commentbox.find_all("p", {"class": "_2NsDsF AwS1CA"})[0].text
                except Exception as e:
                    name = 'No Name'
                   # logging.warning(f"Name not found: {e}")

                try:
                    rating = commentbox.div.div.text
                except Exception as e:
                    rating = 'No rating'
                  #  logging.warning(f"Rating not found: {e}")

                try:
                    commenthead = commentbox.div.p.text
                except Exception as e:
                    commenthead = 'No comment heading'
                   # logging.warning(f"Comment heading not found: {e}")

                try:
                    commenttag = commentbox.find_all("div", {"class": "row"})[1].div.div.div.text
                except Exception as e:
                    commenttag = 'No comment tag found'
                   # logging.error(f"Comment tag error: {e}", exc_info=True)

                mydict = {
                    "Product": searchstring,
                    "Name": name,
                    "Rating": rating,
                    "CommentHead": commenthead,
                    "Comment": commenttag
                }
                reviews.append(mydict)

          #  logging.info(f"Successfully scraped {len(reviews)} reviews")
            return render_template('results.html', reviews=reviews[0:(len(reviews)-1)])

        except Exception as e:
          #  logging.error("Error processing request", exc_info=True)
            return "Something went wrong. Please check the logs for details."
    else:
        return render_template('index.html')

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    #logging.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)
