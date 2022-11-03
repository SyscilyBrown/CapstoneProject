"""Seed file to make sample data for pets db."""

from models import User, Recipe, FavoriteRecipe, db
from app import app

# Create all tables
db.drop_all()
db.create_all()

bubba = User(username='Sydney123', password='12345')
mama = User(username='Teresa123', password='12345')
syssy = User(username='Syscily123', password='12345')


# Add new objects to session, so they'll persist
db.session.add_all([bubba, mama, syssy])


# Commit--otherwise, this never gets saved!
db.session.commit()

"""
recipe1=Recipe(title='turkeywings', link='turkeyhut.org')
recipe2=Recipe(title='chittlerings', link='highbloodpressure.org')
recipe3=Recipe(title='lamb', link='lammylammylamb.org')

db.session.add([recipe1, recipe2, recipe3])
db.session.commit()
"""

turkeylovers = Recipe(title='turkeywings', link = 'turkeyhut.org',savedrecipes=[FavoriteRecipe(user_id=bubba.id),
FavoriteRecipe(user_id=mama.id)])

chitlinlovers = Recipe(title='chitlins', link = 'highbloodpressure.org',savedrecipes=[FavoriteRecipe(user_id=bubba.id),
FavoriteRecipe(user_id=syssy.id)])

watermelonlovers = Recipe(title='junglemelon', link = 'junglemelon.org',savedrecipes=[FavoriteRecipe(user_id=bubba.id),
FavoriteRecipe(user_id=syssy.id), FavoriteRecipe(user_id=mama.id)])



db.session.add_all([turkeylovers, chitlinlovers, watermelonlovers])
db.session.commit()