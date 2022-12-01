from logging.handlers import DatagramHandler
from flask import Flask, render_template, request, flash, redirect, session, g, abort,jsonify, make_response
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import true, select
from sqlalchemy.exc import IntegrityError, PendingRollbackError
from secretkeys import API_SECRET_KEY
import requests
from forms import RecipeByIngredients, RecipeByNutrients, UserForm
from models import db, connect_db, User, FavoriteRecipe, FoundRecipe
import json

CURR_USER_KEY = "curr_user"

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///recipeapp_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False 
app.config['SECRET_KEY'] = API_SECRET_KEY
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()



BASE_URL = 'https://api.spoonacular.com/recipes'
key = API_SECRET_KEY

    


@app.route('/')
def home_page():
    if 'user_id' in session:
        curr_user_id = session['user_id']
        
        username = db.session.query(User.username).filter_by(id=curr_user_id).first()
        username=str(username)
        print("AHHHHHHHHHHH L000000000000000000k")
        print("*********************************")
        print(username)
        removeables="('',)"
        for char in removeables:
            username = username.replace(char,"")
        print(username)
        
        return render_template('home.html', username=username)
    else:
        return render_template('home.html')
    
    


@app.route('/favoriterecipes', methods=['POST', 'GET'])
def store_fav_recipes():
    if "user_id" not in session:
        flash("Please login to view saved recipes.")
        return redirect('/login')
    userid = session['user_id']

    if request.method=="POST":
        try:
            favrecipedata = request.get_json()
            newfav=FavoriteRecipe(user_id = userid, recipe_id=favrecipedata)
            db.session.add(newfav)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            pass
        return favrecipedata
    return redirect('/favoriterecipe')

@app.route('/deleterecipe', methods=['POST', 'GET'])
def delete_recipe():
    userid=session['user_id']

    if request.method=="POST":
        try:
            deletedEntry = request.get_json()
            todelete=FavoriteRecipe.query.filter_by(recipe_id=deletedEntry, user_id=userid).first()
        
            db.session.delete(todelete)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            pass
        return deletedEntry
    return redirect('/favoriterecipe')



@app.route('/showfavoriterecipes', methods=['POST', 'GET'])
def view_fav_recipes():
 
    curr_user_id = session['user_id']
    favoriterecipes= db.session.query(FavoriteRecipe.recipe_id, 
    FoundRecipe.title,
    FoundRecipe.link,
    FoundRecipe.image,
    FoundRecipe.cooktime,
    FavoriteRecipe.user_id).filter_by(user_id=curr_user_id).join(FavoriteRecipe).all()
    

    favoriterecipelinks=[]
    favoriterecipetitles=[]
    favoriterecipeids=[]
    favoriterecipeimages=[]
    favoriterecipetimes=[]
    
    for x in favoriterecipes:
        favoriterecipetitles.append(x.title)
        favoriterecipelinks.append(x.link)
        favoriterecipeids.append(x.recipe_id)
        favoriterecipeimages.append(x.image)
        favoriterecipetimes.append(x.cooktime)


    """
    favoriterecipes = dict(zip(favoriterecipetitles, favoriterecipelinks))
    print(favoriterecipes)
    """

    favoriterecipeinfo ={k: (v1,v2,v3,v4) for k,v1,v2,v3,v4 in zip(favoriterecipeids, favoriterecipelinks, favoriterecipetitles, favoriterecipeimages, favoriterecipetimes) }
            ##this makes dictionary example 146: ('http://link', 'title')
    print(favoriterecipeinfo)
    
    
    
    userid = session['user_id']
    return render_template("viewfavoriterecipes.html", favoriterecipeinfo=favoriterecipeinfo)
        
            

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user: produce form & handle form submission."""

    form = UserForm()

    if form.validate_on_submit():
        try: 
        
            username = form.username.data
            password=form.password.data
            new_user = User.register(username=username, password=password)
        
            db.session.add(new_user)
            db.session.commit()
            
            
        except IntegrityError  as e: 
            form.username.errors = ["Username already taken"]
            return render_template('register.html', form=form )
        session['user_id'] = new_user.id
        session['user_username']=username
        # on successful login, redirect to enter ingredients
        flash('Successfully created your account!')
        return render_template('home.html', username = username)
    else:
        return render_template("register.html", form=form)

@app.route("/login", methods = ["GET", "POST"])
def login():
    """PRoucr loginf orm or handle login"""
    form = UserForm() 
    #This will only run if they've been logged in 
    if form.validate_on_submit():
        name = form.username.data
        pwd = form.password.data
        # authenticate will return a user or False
        user = User.authenticate(username=name, password=pwd)
        if user:
            session["user_id"] = user.id  # keep logged in
            session["user_username"] = user.username  # keep logged in
            return render_template("home.html", username =name)
#If they are not logged in,return to the log in form 
        else:
            form.username.errors = ["Username and password do not match. Please try again."]

    return render_template("login.html", form=form)

@app.route('/logout')
def logout():
    session.pop("user_id")

    return redirect('/')
    


@app.route('/enterIngredients', methods=['GET', 'POST']) 
def enter_ingredients():
    """Send API request based on form entry data """
    form = RecipeByIngredients()
    key = API_SECRET_KEY

    if form.validate_on_submit():
        #send API request from user input
        ingredient1 = form.ingredient1.data
        ingredient2 = form.ingredient2.data
        ingredient3 = form.ingredient3.data
        ingredient4 = form.ingredient4.data
        ingredient5 = form.ingredient5.data
        ingredients = (f"{ingredient1},{ingredient2},{ingredient3},{ingredient4},{ingredient5}")
        response = requests.get(f'{BASE_URL}/findByIngredients', params={'apiKey':key, 'ingredients': ingredients, 'ignorePantry': true, 'number':5, 'ranking': 1})
        data = response.json()
        


        #loop for recipes ids
        recipeid = []
        for i in data:
            recipeid.append(i['id'])

    

        try:
        #Retrieve recipe ids
            recipe1 = recipeid[0]
            recipe2 = recipeid[1]
            recipe3 = recipeid[2]
            recipe4 = recipeid[3]
            recipe5 = recipeid[4]
        except IndexError:
            flash("Sorry, we were unable to find recipes that meet your requirements. Please try again!")
            return redirect('/enterIngredients')    
        recipeids = (f'{recipe1},{recipe2},{recipe3},{recipe4},{recipe5}')
    

        #get recipe details
        recipedetails = requests.get(f'{BASE_URL}/informationBulk', params = {'apiKey':key, 'ids': recipeids, 'includeNutrition': 'false'})
        recipedata = recipedetails.json()

        #loop for recipe details 
        recipetitles=[]
        recipelinks = []
        recipeimages = []
        recipetime=[]
        recipecost=[]
        defaultimage='https://img.freepik.com/free-vector/casserole-pot_1284-11444.jpg?w=740&t=st=1669852437~exp=1669853037~hmac=10d88910916cbabb2bbb69a3641298e03e8d899de4666292f126faefeaa2847f'
        for i in recipedata:
            recipetitles.append(i['title'])
            recipelinks.append(i['spoonacularSourceUrl'])
            
            if 'image' not in i:
                recipeimages.append(defaultimage)

            else:
                recipeimages.append(i['image'])
          
            recipetime.append(i['readyInMinutes'])
            recipecost.append(i['pricePerServing'])
            

        #recipes = dict(zip(recipetitles, recipelinks))
        recipes={k: (v1,v2,v3) for k,v1,v2,v3 in zip(recipetitles, recipelinks, recipeimages,recipetime) }
        print('****************AHH RECIPES******************')
        print(recipes)

        if 'user_id' not in session:
                return render_template('/anon-recipes.html', recipebase = 'ingredients',
        recipes=recipes)

        curr_user_id = session['user_id']
        print(curr_user_id)

        if 'user_id' in session:
            # loop recipes and save to db
            for key, values in recipes.items():
                try:
                    new_entry=FoundRecipe(user_id=curr_user_id, title=key, link=values[0],image=values[1],cooktime=values[2])
                    db.session.add(new_entry)
                    db.session.commit()
                  
            
                except IntegrityError as e:
                    db.session.rollback()
                    pass


            storedrecipes = db.session.query(FoundRecipe).filter(FoundRecipe.user_id == curr_user_id).order_by(FoundRecipe.id.desc()).limit(5)
            print(storedrecipes)
            
            storedrecipelinks=[]
            storedrecipetitles=[]
            storedrecipeids=[]
            storedrecipeimages=[]
            storerecipetimes=[]

            for x in storedrecipes:
                storedrecipeids.append(x.id)
                storedrecipelinks.append(x.link)
                storedrecipetitles.append(x.title)
                storedrecipeimages.append(x.image)
                storerecipetimes.append(x.cooktime)

            storedrecipeinfo ={k: (v1,v2,v3,v4) for k,v1,v2,v3,v4 in zip(storedrecipeids, storedrecipelinks, storedrecipetitles, storedrecipeimages, storerecipetimes) }
            ##this makes dictionary example 146: ('http://link', 'title')
            print(storedrecipeinfo)


            


        return render_template('/logged-recipes.html', recipebase = 'ingredients',
        recipes=recipes, storedrecipeinfo=storedrecipeinfo, user_id=curr_user_id
        )
    else:
        return render_template("enter_ingredients.html", form=form)



@app.route('/enterNutrients', methods = ["GET", "POST"])
def enter_nutrients(): 
    form = RecipeByNutrients()
    key = API_SECRET_KEY

    if form.validate_on_submit():
        
        
        minProtein = form.minProtein.data
        minCalories = form.minCalories.data
        maxCalories = form.maxCalories.data
        minFat = form.minFat.data
        maxFat = form.maxFat.data
        maxCarbs = form.maxCarbs.data
        maxSugar = form.maxSugar.data
        response = requests.get(f'{BASE_URL}/findByNutrients', params={'apiKey': key, 'minProtein':minProtein, 'minCalories':minCalories, 'maxCalories': maxCalories, 'minFat':minFat,'maxFat': maxFat, 'maxCarbs':maxCarbs, 'maxSugar':maxSugar   })
        data = response.json()
        
            
        recipeid = []
        for i in data:
            recipeid.append(i['id'])

    

        try:
        #Retrieve recipe ids
            recipe1 = recipeid[0]
            recipe2 = recipeid[1]
            recipe3 = recipeid[2]
            recipe4 = recipeid[3]
            recipe5 = recipeid[4]
        except IndexError:
            flash("Sorry, we were unable to find recipes that meet your requirements. Please try again!")
            return redirect('/enterIngredients')    
        recipeids = (f'{recipe1},{recipe2},{recipe3},{recipe4},{recipe5}')
    

        #get recipe details
        recipedetails = requests.get(f'{BASE_URL}/informationBulk', params = {'apiKey':key, 'ids': recipeids, 'includeNutrition': 'false'})
        recipedata = recipedetails.json()

        #loop for recipe details 
        recipetitles=[]
        recipelinks = []
        recipeimages = []
        recipetime=[]
        recipecost=[]
        defaultimage='https://img.freepik.com/free-vector/casserole-pot_1284-11444.jpg?w=740&t=st=1669852437~exp=1669853037~hmac=10d88910916cbabb2bbb69a3641298e03e8d899de4666292f126faefeaa2847f'
        for i in recipedata:
            recipetitles.append(i['title'])
            recipelinks.append(i['spoonacularSourceUrl'])
            if 'image' not in i:
                recipeimages.append(defaultimage)
                
            else:
                recipeimages.append(i['image'])
            recipetime.append(i['readyInMinutes'])
            recipecost.append(i['pricePerServing'])

        #recipes = dict(zip(recipetitles, recipelinks))
        recipes={k: (v1,v2,v3) for k,v1,v2,v3 in zip(recipetitles, recipelinks, recipeimages,recipetime) }
        print('****************AHH RECIPES******************')
        print(recipes)

        if 'user_id' not in session:
                return render_template('/anon-recipes.html', recipebase = 'ingredients',
        recipes=recipes)

        curr_user_id = session['user_id']
        print(curr_user_id)

        if 'user_id' in session:
            # loop recipes and save to db
            for key, values in recipes.items():
                try:
                    new_entry=FoundRecipe(user_id=curr_user_id, title=key, link=values[0],image=values[1],cooktime=values[2])
                    db.session.add(new_entry)
                    db.session.commit()
                  
            
                except IntegrityError as e:
                    db.session.rollback()
                    pass


            storedrecipes = db.session.query(FoundRecipe).filter(FoundRecipe.user_id == curr_user_id).order_by(FoundRecipe.id.desc()).limit(5)
            print(storedrecipes)
            
            storedrecipelinks=[]
            storedrecipetitles=[]
            storedrecipeids=[]
            storedrecipeimages=[]
            storerecipetimes=[]

            for x in storedrecipes:
                storedrecipeids.append(x.id)
                storedrecipelinks.append(x.link)
                storedrecipetitles.append(x.title)
                storedrecipeimages.append(x.image)
                storerecipetimes.append(x.cooktime)

            storedrecipeinfo ={k: (v1,v2,v3,v4) for k,v1,v2,v3,v4 in zip(storedrecipeids, storedrecipelinks, storedrecipetitles, storedrecipeimages, storerecipetimes) }
            ##this makes dictionary example 146: ('http://link', 'title')
            print(storedrecipeinfo)


            


        return render_template('/logged-recipes.html', 
        recipes=recipes, storedrecipeinfo=storedrecipeinfo, user_id=curr_user_id
        )
    else:
        return render_template("enter_nutrients.html", form=form)


       



    






    

