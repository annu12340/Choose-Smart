import re
from flask import Flask, render_template, request, redirect, session,  url_for
from flask_sqlalchemy import SQLAlchemy
from bs4 import BeautifulSoup as soup
#from urllib2 import Request, urlopen as uReq as syntax got changed in python3
from urllib.request import urlopen as uReq
import tweepy
import pandas as pd
#to hash the password and to check the password
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SECRET_KEY'] = 'the random string'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50))
    password = db.Column(db.String(50))




def scrapedata(data):
    print("entered scrapedata fn")
    try:
        my_url = 'https://www.goodguide.com/products?filter=' + data
        print(my_url)
        uClient = uReq(my_url)
        page_soup = soup(uClient.read(), "html.parser")
        uClient.close()
        data=page_soup.findAll("a", {"class": "entity-link"})[0:8]

        #print(data)
        name=[]
        link=[]
        for i in data:
            name.append(i.get('title'))
            link.append(i.get('href'))
        return (name,link)
    except:
        print("Error opening the URL")





def ScrapeResult(data):
    print("entered ScrapeResult fn")
    try:
        my_url = 'https://www.goodguide.com' + data
        print(my_url)
        uClient = uReq(my_url)
        page_soup = soup(uClient.read(), "html.parser")
        uClient.close()

        title = page_soup.find("h1")
        print(title.text)

        imgParent=page_soup.find("p", {"class": "text-center product-highlight-image"})
        img= imgParent.find("img")
        i=img['src']


        scoreParent = page_soup.find("p", {"class": "ring-value number"})
        score = scoreParent.find("a")
        print(score.text)

        contentParent = page_soup.find("p", {"class": "rating-explained-ingredient-count number high"})
        HighHazardConcern = contentParent.find("a")
        print(HighHazardConcern.text)

        contentParent2 = page_soup.find("p", {"class": "rating-explained-ingredient-count number medium"})
        MediumHazardConcern = contentParent2.find("a")
        print(MediumHazardConcern.text)

        contentParent3 = page_soup.find("p", {"class": "rating-explained-ingredient-count number low"})
        LowHazardConcern = contentParent3.find("a")
        print(LowHazardConcern.text)

        print("END")
        return (title.text, i,score.text,HighHazardConcern.text ,MediumHazardConcern.text,LowHazardConcern.text)
    except:
        print("Error opening the URL: Error in scrape result")

################################################ Price Scrapper ##############################


def PriceNameSuggestion(name):
    print("entered Price name suggestion fn")
    try:
        my_url = 'http://scandid.in/search?q='+name+'&type=products'
        print(my_url)
        uClient = uReq(my_url)
        page_soup = soup(uClient.read(), "html.parser")
        uClient.close()
        data = page_soup.findAll("a", {"class": "ellipsis multiline"})[0:8]
        name=[]
        link=[]
        for i in data:
            name.append(i.text)
            link.append('http://scandid.in/'+i['href'])
        print("name is ", name )
        print("link is ", link)
        return (name,link)
    except:
        print("Error opening the URL")

def ScrapePrice(data):
    url= data
    print(url)
    #uClient = uReq(url)
    uClient = uReq(url)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, "html.parser")
    print("start flipkart")
    FinalResult=[]
    p = page_soup.find("span", {"id": "best_price"})
    FinalResult.append(p.text)
    seller=page_soup.find("span", {"class": "btn-span"})
    FinalResult.append(seller.text)
    print("found result")
    return FinalResult


########################### Sentimental Analysis ########################################

def sentimentalAnalysis(review):
    print('sa')
    try:
        from textblob import TextBlob
        consumer_key = "Your consmer key "
        consumer_secret = "Your consumer secret key"
        access_token = "Your acess token"
        access_token_secret = "Your access token secret"

        def twitter():
            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)
            api = tweepy.API(auth, wait_on_rate_limit=True)
            return api

        tw = twitter()

        search = tw.user_timeline(screen_name="TheEllenShow", count=200, lang="en")
        #  Printing last 10 tweets
        print("10 recent tweets:\n")
        for tweets in search[:10]:
            print(tweets.text + '\n')
        df = pd.DataFrame([tweets.text for tweets in search], columns=['Tweets'])
        df.head(10)

        polarity = lambda x: TextBlob(x).sentiment.polarity
        subjectivity = lambda x: TextBlob(x).sentiment.subjectivity
        df['polarity'] = df['Tweets'].apply(polarity)
        df['subjectivity'] = df['Tweets'].apply(subjectivity)

    except:
        print("invalid credientials")




################################## ROUTES ###################################

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        email = request.form['email']
        password = request.form['password']
        #query based on email and to check whether the password entered by the user is correct or not
        data = User.query.filter_by(email=email).first()
        if data is not None  and check_password_hash(data.password, password):
            session['user'] = data.id
            print(session['user'])
            return redirect(url_for('home'))
        return render_template('incorrect_login.html')

@app.route('/', methods=['GET', 'POST'])
@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_user = User(email=request.form['email'],
                        password=generate_password_hash(request.form['password'],method='sha256'))
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))



#############################################################################

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/show')
def show():
    show_user = User.query.all()
    return render_template('show.html', show_user=show_user)





@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':

        product = request.form['product']
        print("prodict is ", product)
        try:
            print("fn call")
            suggestions,link= scrapedata(product)
            return render_template('suggestions.html', suggestions=suggestions, link=link)
        except:
            return render_template('404.html', display_content='Invalid symbol. No quote available' )
    else:
    # GET method
        return render_template('search.html')


@app.route('/result', methods=['GET', 'POST'])
def result():
    result =  request.args
    data=result.get('forwardBtn')

    name,img, score,Hconcern, Mconvern, lconcern= ScrapeResult(data)
    return render_template('result.html', name=name, img=img, score=score,Hconcern=Hconcern, Mconvern=Mconvern, lconcern=lconcern)




@app.route('/price', methods=['GET', 'POST'])
def price():
    if request.method == 'POST':
        price = request.form['price']
        print("prodict is ", price)
        try:
            print("price call")
            Listname,link=PriceNameSuggestion(price)
            print("Inside 123 : Listname",Listname,link)
            return render_template('PriceSuggestion.html', l=Listname, link=link)
        except:
            return render_template('404.html', display_content='Invalid symbol. No quote available' )
    else:
    # GET method
        return render_template('price.html')




@app.route('/reviews', methods=['GET', 'POST'])
def reviews():
    if request.method == 'POST':
        review = request.form['review']
        try:
            review= sentimentalAnalysis(review)
            return render_template('Reviews.html', reviews=reviews)
        except:
            return render_template('404.html', display_content='Invalid credientials' )
    else:
    # GET method
        return render_template('Reviews.html')


@app.route('/priceresult', methods=['GET', 'POST'])
def priceresult():
    result =  request.args
    data=result.get('forwardBtn')
    print(data)
    price,seller= ScrapePrice(data)
    return render_template('showLowPrice.html', price=price, seller= seller)



@app.route('/laws')
def laws():
    return render_template('laws.html')

#############################################################################


if __name__ == '__main__':
    #Added secret key that the top app.secret_key = 'super secret key'
    db.create_all()
    app.run(debug=True)