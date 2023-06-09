from flask import Flask, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restful import Api, Resource
from dotenv import load_dotenv
from os import environ

load_dotenv()

# Create App instance
app = Flask(__name__)

# Add DB URI from .env
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('SQLALCHEMY_DATABASE_URI')

# Registering App w/ Services
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)
CORS(app)
Migrate(app, db)

# Models
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(252), nullable=False)
    price = db.Column(db.Float)
    inventory_quantity = db.Column(db.Integer)

    def __repr__(self):
        return f'{self.name} {self.description} {self.price} {self.inventory_quantity}'
    
  

# Schemas
class ProductSchema(ma.Schema):
    class Meta:
        fields = ("id.", "name", "description", "price", "inventory_quantity")
        

product_schema = ProductSchema() 
products_schema = ProductSchema(many=True)

my_product = Product(id= 2, name="Toaster", description="Toast_buns", price="27.39", inventory_quantity="11")
serialized_product = product_schema.dump(my_product) 
print(serialized_product)

# Resources
class ProductListResource (Resource):
    def get(self):
        all_products = Product.query.all()
        return products_schema.dump(all_products)
    
    def post(self):
        print(request)
        new_product = Product(
            name=request.json['name'],
            description=request.json['description'],
            price=request.json['price'],
            inventory_quantity=request.json['inventory_quantity']
        )
        db.session.add(new_product)
        db.session.commit()
        return product_schema.dump(new_product), 201
    
class ProductResource(Resource):
    def get(self, product_id):
        product_from_db = Product.query.get_or_404(product_id)
        return product_schema.dump(product_from_db)
    
    def delete(self, product_id):
        product_from_db = Product.query.get_or_404(product_id)
        db.session.delete(product_from_db)
        return '', 204
    
    def put(self, product_id):
        product_from_db = Product.query.get_or_404(product_id)
        if 'name' in request.json:
            product_from_db.name = request.json['name']
        if 'description' in request.json:
            product_from_db.description = request.json['description']    
        if 'price' in request.json:
            product_from_db.price = request.json['price']
        if 'inventory_quantity' in request.json:
            product_from_db.inventory_quantity = request.json['inventory_quantity']
        
        db.session.commit()    
        return product_schema.dump(product_from_db)

# Routes
api.add_resource(ProductListResource, '/api/products/')
api.add_resource(ProductResource, '/api/products/<int:product_id>')
