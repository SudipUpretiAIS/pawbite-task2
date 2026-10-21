"""Explicit database setup commands; never initialise schema in web workers."""
import base64
from decimal import Decimal
from pathlib import Path
import click
from sqlalchemy import text
from shop import app, db, bcrypt
from shop.products.models import Category, Product, InvoiceCounter
from shop.user.models import User

SAMPLES = [
    ('Puppy', 'Puppy Chicken Recipe', '24.90', 'Complete dry food for growing puppies.', 'puppy,chicken', 'item1.jpg'),
    ('Adult', 'Adult Salmon Recipe', '39.90', 'Dry food formulated for adult dogs.', 'adult,salmon', 'item2.jpg'),
    ('Senior', 'Senior Lamb Recipe', '34.90', 'Daily food for older dogs.', 'senior,lamb', 'item3.jpg'),
]

@app.cli.command('init-db')
def init_db():
    """Create missing tables only. This does not migrate existing schemas."""
    db.create_all()
    if db.session.get(InvoiceCounter, 1) is None:
        db.session.add(InvoiceCounter(id=1, current_number=0))
    db.session.commit()
    click.echo('Database tables and invoice counter ready.')

@app.cli.command('seed-demo')
def seed_demo():
    """Insert fictitious demonstration products if they are absent."""
    for cat_name, name, price, desc, tag, image in SAMPLES:
        category = Category.query.filter_by(name=cat_name).first()
        if category is None:
            category = Category(name=cat_name)
            db.session.add(category)
            db.session.flush()
        if Product.query.filter_by(name=name).first() is None:
            image_bytes = (Path(app.static_folder) / 'images' / image).read_bytes()
            db.session.add(Product(name=name, price=Decimal(price), description=desc, tag=tag,
                                   category_id=category.id,
                                   image_file=base64.b64encode(image_bytes).decode('ascii')))
    db.session.commit()
    click.echo('Demo catalogue ready. Images are sample assets from the supplied project.')

@app.cli.command('create-admin')
@click.option('--email', prompt=True)
@click.option('--name', default='PawBite Admin', prompt=True)
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
def create_admin(email, name, password):
    """Create a new admin; never promotes or overwrites an existing customer."""
    email = email.strip().lower()
    if len(password) < 12 or len(password.encode('utf-8')) > 72:
        raise click.ClickException('Use a password of 12 or more characters, at most 72 UTF-8 bytes.')
    if not name.strip() or len(name) > 50 or '@' not in email or len(email) > 254:
        raise click.ClickException('Enter a valid name and email.')
    if User.query.filter_by(email=email).first():
        raise click.ClickException('That email already exists; it was not modified.')
    db.session.add(User(username=name.strip(), email=email,
                        password=bcrypt.generate_password_hash(password).decode('utf-8'), role='admin'))
    db.session.commit()
    click.echo('Admin created. No default admin credentials are supplied.')

@app.route('/healthz')
def healthz():
    """Process health for hosting startup probes; no credentials or DB details."""
    return {'status': 'ok'}, 200

@app.cli.command('check-db')
def check_db():
    db.session.execute(text('SELECT 1'))
    click.echo('Database connected; catalogue contains %s products.' % Product.query.count())
