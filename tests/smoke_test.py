import os,sys,io
os.environ['SECRET_KEY']='local-validation-secret-value-at-least-32-characters'
os.environ['DATABASE_URL']='sqlite:///:memory:'
os.environ['COOKIE_SECURE']='false'
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[1]))
from shop import app,db,bcrypt
from shop.user.models import User
from shop.products.models import Product,Category,Cart,Order
app.config.update(TESTING=True)
with app.app_context():
 runner=app.test_cli_runner()
 for command in ['init-db','seed-demo','seed-demo','check-db']:
  r=runner.invoke(args=[command]);assert r.exit_code==0,(command,r.output,r.exception)
 assert Product.query.count()==3
 admin=User(username='Admin',email='admin@example.test',password=bcrypt.generate_password_hash('TestAdmin_2026').decode(),role='admin')
 db.session.add(admin);db.session.commit()
 c=app.test_client()
 assert c.get('/healthz').status_code==200
 for path in ['/','/login','/admin_login','/filter_product','/single_product/1']:
  r=c.get(path);assert r.status_code==200,(path,r.status_code)
 assert c.get('/admin_home').status_code==302
 r=c.post('/',data=dict(username='Student',email='student@example.test',password='Student_2026',repassword='Student_2026'));assert r.status_code==302
 r=c.post('/',data=dict(username='',email='bad',password='x',repassword='x'));assert User.query.count()==2
 assert c.post('/login',data=dict(email='student@example.test',password='wrong')).status_code==200
 assert c.post('/login',data=dict(email='student@example.test',password='Student_2026')).status_code==302
 assert c.get('/admin_home').status_code==302
 assert c.post('/add-to-cart/1',headers={'Referer':'http://localhost/'}).status_code==302
 cart=Cart.query.first();assert cart.quantity==1
 assert c.get('/pluscart?cart_id='+str(cart.id)).status_code==200
 assert c.get('/minuscart?cart_id='+str(cart.id)).status_code==200
 assert c.get('/view_cart').status_code==200
 assert c.get('/place-order').status_code==302
 order=Order.query.first();assert order and Cart.query.count()==0
 assert c.get('/invoice-details/'+order.invoice).status_code==200
 r=c.get('/get_pdf/'+order.invoice);assert r.status_code==200 and r.data.startswith(b'%PDF')
 assert c.get('/orders').status_code==200
 assert c.post('/update_password',data=dict(password='BadReset2026',repassword='BadReset2026')).status_code==302
 assert c.post('/initkhalti').status_code==503
 c.get('/logout')
 assert c.post('/admin_login',data=dict(email='admin@example.test',password='TestAdmin_2026')).status_code==302
 for path in ['/admin_home','/view_category','/view_user','/view-orders','/add']:
  assert c.get(path).status_code==200,path
 category=Category.query.first()
 im=(__import__('pathlib').Path('shop/static/images/item1.jpg')).read_bytes()
 r=c.post('/add',data=dict(name='CRUD Test',price='5.00',category=str(category.id),desc='Test product',tag='test',pic=(io.BytesIO(im),'test.jpg')),content_type='multipart/form-data');assert r.status_code==200
 product=Product.query.filter_by(name='CRUD Test').one()
 r=c.post('/update_product/'+str(product.id),data=dict(name='CRUD Updated',price='6.00',category=str(category.id),desc='Updated',tag='test'));assert r.status_code==302
 assert c.get('/delete_product/'+str(product.id)).status_code==302
 assert Product.query.count()==3
 assert c.get('/admin_logout').status_code==302
 print('PASS: source import; DB setup and repeatable seed; public pages; registration and login; role protection; cart; ordering; PDF; disabled reset/payment; admin product CRUD and logout.')
