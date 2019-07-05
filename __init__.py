from flask import render_template, jsonify, Flask, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
from werkzeug import secure_filename
import firebase
import pyrebase
import random
import string
import datetime


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/CSV'


config = {
	"apiKey": "AIzaSyBL0pyCJDim2GvtSTdXJiAvV25FJnPrsJc",
    "authDomain": "stockdemo-4ad4b.firebaseapp.com",
    "databaseURL": "https://stockdemo-4ad4b.firebaseio.com",
    "projectId": "stockdemo-4ad4b",
    "storageBucket": "stockdemo-4ad4b.appspot.com",
    "messagingSenderId": "181090953713",
    "appId": "1:181090953713:web:40fd94f08cbe0f10"
}

firebase = pyrebase.initialize_app(config);
# Use a service account
cred = credentials.Certificate(r'C:\Users\engsa\Desktop\Code\Demo\k.json')
firebase_admin.initialize_app(cred)

#firebase = pyrebase.initialize_app(cred);
db = firestore.client()

storage = firebase.storage()


@app.route('/')
def home():
	experts_info = get_all_Expert()[:4]
	posts_info = get_all_Posts()
	companies_info = get_all_Companies()[:9]
	news = get_news()
	if 'mail' in session :
		com_follow = get_your_companies_follow()
		ex_follow = get_your_expert_follow()
		return render_template('index.html', experts_info = experts_info, posts_info = posts_info, companies_info = companies_info,com_follow=com_follow,ex_follow=ex_follow,news=news,share_values=v())
	return render_template('index.html', experts_info = experts_info, posts_info = posts_info, companies_info = companies_info,com_follow=[],ex_follow=[],news=news,share_values=v())

@app.route('/login', methods=['GET', 'POST'])
def login():
	session.clear()
	if request.method == 'POST':
		mail = request.form['mail']
		password = request.form['pass']
		expert_mode = request.form.getlist("mode")
		if expert_mode:
			session['mode'] = 'expert'
			users_ref = db.collection(u'Experts')
			query = users_ref.where(u'mail', u'==', mail).where(u'password', u'==', password)
			x = ''
			docs = query.get()
			for doc in docs:
				x = x+(u'{} => {}'.format(doc.id, doc.to_dict()))
	        
			if x :
				flash('You Successfully logged in')
				session['mail'] = mail
				return redirect(url_for('home'))
			else:
				flash('Not registered please sign up')
				return redirect(url_for('signup'))
		else:
			session['mode'] = 'user'
			users_ref = db.collection(u'Users')
			query = users_ref.where(u'mail', u'==', mail).where(u'password', u'==', password)
			x = ''
			docs = query.get()
			for doc in docs:
				x = x+(u'{} => {}'.format(doc.id, doc.to_dict()))
	        
			if x :
				flash('You Successfully logged in')
				session['mail'] = mail
				return redirect(url_for('home'))
			else:
				flash('Not registered please sign up')
				return redirect(url_for('signup'))

	else:
		return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
	session.clear()
	if request.method == 'POST':
		fname = request.form['fname']
		lname = request.form['lname']
		username = fname +' '+ lname
		mail = request.form['mail']
		bio = request.form['bio']
		password = request.form['pass']
		mode = request.form['radio']
		if mode == 'user':
			session['mode'] = 'user'
			users_ref = db.collection(u'Users')
			query = users_ref.where(u'mail', u'==', mail)
			x = ''
			docs = query.get()
			for doc in docs:
				x = x+(u'{} => {}'.format(doc.id, doc.to_dict()))
			if x :
				flash(' Mail is used before !!!!')
				return redirect(url_for('login'))
			else:
				db.collection(u'Users').add({

			    	'mail': mail,
			    	'name': username,
			    	'bio': bio,
			    	'password': password
				})
		else:
			session['mode'] = 'expert'
			expert_ref = db.collection(u'Experts')
			query = expert_ref.where(u'mail', u'==', mail)
			x = ''
			docs = query.get()
			for doc in docs:
				x = x+(u'{} => {}'.format(doc.id, doc.to_dict()))
			if x :
				flash(' Mail is used before !!!!')
				return redirect(url_for('login'))
			else:
				#picture = request.files['pic']
				#new_name = ''.join(random.choice(letters) for i in range(12))
				db.collection(u'Experts').add({

			    	'mail': mail,
			    	'name': username,
			    	'bio': bio,
			    	'password': password,
			    	'rate': '20'
				})
				expert_ref = db.collection(u'Experts')
				query = expert_ref.where(u'mail', u'==', mail).get()
				e_id = ""
				for e in query:
					e_id = e.id
				picture = request.files['pic']
				(storage.child('UsersImages/' + e_id+'.png')).put(picture)
				city_ref = db.collection(u'Experts').document(e_id)
				city_ref.set({
    				u'image': 'UsersImages/'+ e_id + '.png'
					}, merge=True)

		
			flash('You Successfully signed up ...')
			
			return redirect(url_for('login'))
			
	else :
		return render_template('new-registration.html')




@app.route('/add_company', methods=['GET', 'POST'])
def add_company():
	if request.method == 'POST':
		stockname = request.form['stockname']
		stockplace = request.form['stockplace']
		country = request.form['country']
		ceo = request.form['ceo']
		info = request.form['info']
		db.collection(u'Companies').add({
		    'CEO': ceo,
		    'country': country,
		    'description': info,
		    'stock_name': stockname,
		    'stock_place': stockplace
		})
		file = request.files['file']
		file.save(secure_filename(file.filename))
		flash('You Successfully Added this company')
		return render_template('add_company.html')
	else :
		return render_template('add_company.html')


@app.route('/Experts')
def showExpert():
	experts_info =get_all_Expert()
	if 'mail' in session :
		ex_follow = get_your_expert_follow()
		return render_template('experts.html', experts_info = experts_info ,ex_follow=ex_follow)
	return render_template('experts.html', experts_info = experts_info)


@app.route('/Experts/<path:ex_name>')
def get_ex(ex_name):
	ex_ref = db.collection(u'Experts').where(u'name', u'==', ex_name).get()
	ex_info = []
	ex_id = ''
	ex_mail = ''
	posts_info = []
	for ex in ex_ref:
		ex_mail = (ex.to_dict())['mail']
		ex_bio = (ex.to_dict())['bio']
		ex_rate = (ex.to_dict())['rate']
		#ex_mail = session['mail']
		ex_img = storage.child((ex.to_dict())['image']).get_url(None)
		follower_ref = db.collection(u'Experts').document(ex.id).collection(u'Follower').get()
		numfer = 0
		ex_id = ex_img
		for flow in follower_ref:
			numfer = numfer +1
		ex_info.append(dict(ex_name=ex_name, ex_mail=ex_mail,ex_rate=ex_rate,ex_img=ex_img,ex_bio=ex_bio,ex_follow=numfer))
	for p in get_all_Posts():
		if p['p_img']==ex_id:
			p_time = p['p_time']
			p_title = p['p_title']
			p_content = p['p_content']
			posts_info.append(dict(p_time=p_time,p_title=p_title,p_content=p_content))
	pre_ref = db.collection(u'test_1').where(u'mail', u'==', ex_mail).get()
	pre_info = []
	for pre in pre_ref:
		pre_company = (pre.to_dict())['company']
		pre_date = (pre.to_dict())['date']
		pre_trend = (pre.to_dict())['trend']
		pre_info.append(dict(com=pre_company,date=pre_date,trend=pre_trend))

	return render_template('profile-expert - show.html',ex_info=ex_info,posts_info=posts_info,pre_info=pre_info)


@app.route('/Companies')
def showComanies():
	companies_info = get_all_Companies()
	if 'mail' in session :
		com_follow = get_your_companies_follow()
		return render_template('companies.html', companies_info = companies_info,com_follow=com_follow,share_values=v())
	return render_template('companies.html', companies_info = companies_info,share_values=v())
@app.route('/companies/<path:company>' , methods=['GET', 'POST'])
def get_company_by_name(company):
	if request.method =='POST':
		company_ref = db.collection(u'Companies').where(u'stock_name', u'==', company)
		company = company_ref.get()
		com_name = ''
		for com in company:
			com_name = (com.to_dict())['company_name']
		option = request.form['switch']
		trend = ''
		if option =='up':
			trend = True
		else :
			trend = False
		pre_time = datetime.datetime.now()
		db.collection(u'test_1').add({
		    'company': com_name,
		    'date': pre_time,
		    'mail': session['mail'],
		    'trend': trend
		})
		return redirect(url_for('Profile'))
	else :
		company_ref = db.collection(u'Companies').where(u'stock_name', u'==', company)
		company = company_ref.get()
		com_ceo = ''
		com_name = ''
		com_stock_name = ''
		com_desc = ''
		com_country = ''
		com_img = ''
		for com in company:
			com_ceo = (com.to_dict())['CEO']
			com_name = (com.to_dict())['company_name']
			com_stock_name = (com.to_dict())['stock_name']
			com_desc = (com.to_dict())['description']
			com_country = (com.to_dict())['country']
			com_stock_place = (com.to_dict())['stock_place']
			com_img = storage.child((com.to_dict())['company_image']).get_url(None)
			#Expert_Prediction_ref = db.collection(u'Companies').document(com.id).collection(u'Expert-Prediction').get()
			#docs = {el.id: el.to_dict() for el in Expert_Prediction_ref}
			#docs = Expert_Prediction_ref.to_dict()
			#ex_predict = []
			#for ex_pre in Expert_Prediction_ref:
				#ex_id = (ex_pre.to_dict())['expert_id']
				#duration = (ex_pre.to_dict())['duration']
				#trend = (ex_pre.to_dict())['trend']
				#ex_predict.append(dict(ex_id = ex_id , duration = duration , trend = trend))
			#System_Prediction_ref = db.collection(u'Companies').document(com.id).collection(u'System-Prediction').get()
			#sy_predict = []
			#for sy_pre in System_Prediction_ref:
				#sy_value = (sy_pre.to_dict())['value']
				#duration = (sy_pre.to_dict())['duration']
				#trend = (sy_pre.to_dict())['trend']
				#sy_predict.append(dict(sy_value =sy_value , duration = duration , trend = trend))

			#company_info.append(dict(com_ceo=com_ceo, com_name=com_name, com_stock_name=com_stock_name, com_desc=com_desc, com_country=com_country, com_stock_place=com_stock_place, com_img=com_img))
		real_values = v()
		share = ''
		ratio = ''
		rate = ''
		for i in real_values:
		 	if i['stock_name'] ==com_stock_name:
		 		share =i['sh_value']
		 		rate=i['rate']
		 		ratio=i['ratio']
		news_info = []
		news = get_news()
		for n in news:
			if (n['n_company']).lower()==(com_name).lower():
				news_info.append(n)
		sys_pre_ref = db.collection(u'test_2').where(u'company', u'==', com_stock_name).get()
		trend = ''
		for p in sys_pre_ref:
			trend = (p.to_dict())['trend']
		if 'mail' in session and session['mode']=='expert':
			return render_template('company.html', com_name=com_name,com_stock_name=com_stock_name,com_img=com_img,share=share,rate=rate,ratio=ratio,news_info=news_info,trend=trend)
		return render_template('company - show.html', com_name=com_name,com_stock_name=com_stock_name,com_img=com_img,share=share,rate=rate,ratio=ratio,news_info=news_info,trend=trend)
	

''' appear on expert mode only '''
@app.route('/Profile', methods=['GET', 'POST'])
def Profile():
	if session['mode']== 'user':
		user_ref = db.collection(u'Users').where(u'mail', u'==', session['mail']).get()
		user_info =[]
		for user in user_ref:
			user_name = (user.to_dict())['name']
			user_pass = (user.to_dict())['password']
			user_info.append(dict(user_name=user_name,user_pass=user_pass,user_mail=session['mail']))
		return render_template('profile.html',user_info=user_info)
	else :
		if request.method=='POST':
			content = request.form['inbox']
			ex_ref = db.collection(u'Experts').where(u'mail', u'==', session['mail']).get()
			post_time = datetime.datetime.now()
			ex_id = ''
			ex_name = ''
			ex_img = ''
			for ex in ex_ref:
				ex_name = (ex.to_dict())['name']
				ex_img = (ex.to_dict())['image']
				ex_id = ex.id

			db.collection(u'Posts').add({
		    	'author_id': ex_id,
		    	'author_image': ex_img,
		    	'author_name': ex_name,
		    	'post_content': content,
		    	'post_image': '',
		    	'post_likes':0,
		    	'post_time':post_time,
		    	'post_title':'new post'
			})
			return redirect(url_for('Profile'))
		else:
			ex_ref = db.collection(u'Experts').where(u'mail', u'==', session['mail']).get()
			ex_info = []
			ex_id = ''
			posts_info = []
			for ex in ex_ref:
				ex_name = (ex.to_dict())['name']
				ex_bio = (ex.to_dict())['bio']
				ex_rate = (ex.to_dict())['rate']
				ex_mail = session['mail']
				ex_img = storage.child((ex.to_dict())['image']).get_url(None)
				follower_ref = db.collection(u'Experts').document(ex.id).collection(u'Follower').get()
				numfer = 0
				ex_id = ex_img
				for flow in follower_ref:
					numfer = numfer +1
				ex_info.append(dict(ex_name=ex_name, ex_mail=ex_mail,ex_rate=ex_rate,ex_img=ex_img,ex_bio=ex_bio,ex_follow=numfer))
			for p in get_all_Posts():
				if p['p_img']==ex_id:
					p_time = p['p_time']
					p_title = p['p_title']
					p_content = p['p_content']
					posts_info.append(dict(p_time=p_time,p_title=p_title,p_content=p_content))
			pre_ref = db.collection(u'test_1').where(u'mail', u'==', session['mail']).get()
			pre_info = []
			for pre in pre_ref:
				pre_company = (pre.to_dict())['company']
				pre_date = (pre.to_dict())['date']
				pre_trend = (pre.to_dict())['trend']
				pre_info.append(dict(com=pre_company,date=pre_date,trend=pre_trend))

			return render_template('profile-expert.html',ex_info=ex_info,posts_info=posts_info,pre_info=pre_info)

	



''' structue of post that will be returned to page
    posts_info =	{
	  "name": "",
	  "time": "",
	  "title": "",
	  "img":"",
	  "content":"",
	  "ex_id":""
	}
	'''
def get_all_Posts():
    posts_ref = db.collection(u'Posts')
    posts = posts_ref.get()
    posts_info = []
    for post in posts:
    	p_name = (post.to_dict())['author_name']
    	p_time = (post.to_dict())['post_time']
    	p_title = (post.to_dict())['post_title']
    	p_content = (post.to_dict())['post_content']
    	p_img = storage.child((post.to_dict())['author_image']).get_url(None)
    	ex_id = (post.to_dict())['author_id']
    	posts_info.append(dict(P_name=p_name, p_time=p_time, p_title=p_title, p_content=p_content, p_img=p_img, ex_id=ex_id))
    	
    return posts_info
    
def get_news():
	news_ref = db.collection(u'Sentiment')
	news = news_ref.get()
	news_info = []
	for n in news:
		n_company = (n.to_dict())['Company']
		n_sub = (n.to_dict())['Subjectivity']
		n_text = (n.to_dict())['Text']
		n_trend = (n.to_dict())['Trend']
		news_info.append(dict(n_company=n_company, n_sub=n_sub, n_text=n_text, n_trend=n_trend))
	return news_info
   
    	
    	
    	
    	
    	
    	
    

''' structure of expert that will be returned to page 
    exs_info =	{
	  "name": "",
	  "mail": "",
	  "rate": "",
	  "img":"",
	  "bio":"",
	  "follower":1,
	  "following":1
	}
	'''
def get_all_Expert():
    expert_ref = db.collection(u'Experts')
    experts = expert_ref.get()
    experts_info = []
    for ex in experts:
    	ex_name = (ex.to_dict())['name']
    	ex_mail = (ex.to_dict())['mail']
    	ex_rate = (ex.to_dict())['rate']
    	ex_bio = (ex.to_dict())['bio']
    	ex_id = ex.id
    	ex_img = storage.child((ex.to_dict())['image']).get_url(None)
    	follower_ref = db.collection(u'Experts').document(ex.id).collection(u'Follower').get()
    	following_ref = db.collection(u'Experts').document(ex.id).collection(u'Following').get()
    	numfer = 0
    	numf = 0

    	for flow in follower_ref:
    		numfer = numfer +1

    	for foww in following_ref:
    		numf = numf +1
    	experts_info.append(dict(e_name=ex_name, e_mail=ex_mail, e_follower=numfer, e_following=numf, e_img=ex_img, e_bio=ex_bio, e_rate=ex_rate,ex_id=ex_id))
    return experts_info


def get_all_Companies():
    companies_ref = db.collection(u'Companies')
    companies = companies_ref.get()
    companies_info = []
    for com in companies:
    	com_ceo = (com.to_dict())['CEO']
    	com_name = (com.to_dict())['company_name']
    	com_stock_name = (com.to_dict())['stock_name']
    	com_desc = (com.to_dict())['description']
    	com_country = (com.to_dict())['country']
    	com_id = com.id
    	com_stock_place = (com.to_dict())['stock_place']
    	com_img = storage.child((com.to_dict())['company_image']).get_url(None)
    	Expert_Prediction_ref = db.collection(u'Companies').document(com.id).collection(u'Expert-Prediction').get()
    	System_Prediction_ref = db.collection(u'Companies').document(com.id).collection(u'System-Prediction').get()
    	# code to get prediction of system and expert for company 
    	share_value =  random.choice([168.48, 120.31, 124.40,133.81,169.80,144.80,190.30])
    	share_rate = random.choice([48, 31, 40,81,80])
    	share_ratio = random.choice([-2, 5, 7,-1,-9])
    	companies_info.append(dict(com_ceo=com_ceo, com_name=com_name, com_stock_name=com_stock_name, com_desc=com_desc, com_country=com_country, com_stock_place=com_stock_place, com_img=com_img,com_id=com_id,share_value=share_value,share_rate=share_rate,share_ratio=share_ratio))
    return companies_info


def get_your_companies_follow():
	if session['mode']=='expert':
		expert_ref = db.collection(u'Experts')
		expert = expert_ref.where(u'mail', u'==', session['mail']).get()
		companies_follow = []
		for e in expert:
			expert_com_follow = db.collection(u'Experts').document(e.id).collection(u'companies').get()
			for fol in expert_com_follow:
				com_id = (fol.to_dict())['company id']
				companies_follow.append(com_id)

		return companies_follow
	elif session['mode'] =='user':
		user_ref = db.collection(u'Users')
		user = user_ref.where(u'mail', u'==', session['mail']).get()
		companies_follow = []
		for e in user:
			companies_follow = (e.to_dict())['company_follow']
			#companies_follow.append(com_id)

		return companies_follow



def get_your_expert_follow():
	if session['mode']=='expert':
		expert_ref = db.collection(u'Experts')
		expert = expert_ref.where(u'mail', u'==', session['mail']).get()
		expert_follow = []
		for e in expert:
			expert_ex_follow = db.collection(u'Experts').document(e.id).collection(u'Following').get()
			for fol in expert_ex_follow:
				ex_id = (fol.to_dict())['userid']
				expert_follow.append(ex_id)

		return expert_follow
	elif session['mode'] =='user':
		user_ref = db.collection(u'Users')
		user = user_ref.where(u'mail', u'==', session['mail']).get()
		expert_follow = []
		for e in user:
			#user_ex_follow = db.collection(u'users').document(e.id).get()
			expert_follow = (e.to_dict())['expert_follow']
				#expert_follow.append(ex_id)

		return expert_follow

#c = []
#@app.route('/v')
def v():
	v_ref = db.collection(u'RealTimeValues').get()
	#get_share_values_realtime()
	c =[]
	for b in v_ref:
		#doc_ref = db.collection(u'RealTimeValues').document(b.id).on_snapshot(on_snapshot)
		c.append(dict(sh_value=(b.to_dict())['company_share_value'],stock_name=(b.to_dict())['stock_name'],date=(b.to_dict())['date'],rate=(b.to_dict())['rate'],ratio=(b.to_dict())['ratio']))
	return c


def get_share_values_realtime():
	doc_ref = db.collection(u'RealTimeValues').on_snapshot(on_snapshot)
	

'''
# Create a callback on_snapshot function to capture changes
def on_snapshot(doc_snapshot, changes, read_time):
	v_ref = db.collection(u'RealTimeValues').get()
	c.clear()
	for b in v_ref:
		c.append(dict(sh_value=(b.to_dict())['company_share_value'],com_id=(b.to_dict())['company_id'],date=(b.to_dict())['date']))

'''


'''
@app.route('/real')
def real():
	companies_info = get_all_Companies()[:9]
	return render_template('widght.html',share_values=v(),companies_info=companies_info)

	#n = []
	#for doc in doc_snapshot:
	#	n.append((doc.to_dict())['company_share_value'])
	#c = n
'''
#simulation

@app.route('/sim')
def sim():
	if request.method == 'POST':
		return '...'
	else :
		users_ref = db.collection(u'simulation_1')
		query = users_ref.where(u'user_mail', u'==', session['mail']).get()
		balance=0
		for p in query:
			balance = float((p.to_dict())['total_money'])
		sim_ref = db.collection(u'simulation_2')
		query = sim_ref.where(u'user_mail', u'==', session['mail']).get()
		sim_list = []
		for s in query:
			stockname=(s.to_dict()['stock_name'])
			b_price = float((s.to_dict())['price'])
			l_price = float((s.to_dict())['price'])+25
			amount = float((s.to_dict())['amount']) /float((s.to_dict())['price'])
			amountvalue = amount * l_price
			sim_list.append(dict(stockname=stockname,b_price=b_price,l_price=l_price,amount=amount,amountvalue=amountvalue))
		return render_template('table.html',sim_list=sim_list,balance=balance,overall_value=0)


@app.route('/simulation/com/<path:stockname>', methods=['GET', 'POST'])
def simulate(stockname):
	if request.method == 'POST':
		balance = 10000
		amount = request.form['amount']
		usermail = session['mail']
		users_ref = db.collection(u'simulation_1')
		get_sim = users_ref.where(u'user_mail', u'==', usermail)
		x = ''
		docs = get_sim.get()
		for doc in docs:
			x = x+(u'{} => {}'.format(doc.id, doc.to_dict()))
		if x :
			query = users_ref.where(u'user_mail', u'==', usermail).get()
			for p in query:
				balance = float((p.to_dict())['total_money'])
		else:
			db.collection(u'simulation_1').add({

			    	'total_money': 10000,
			    	'user_mail': usermail
				})
		
				
		real_ref = db.collection(u'RealTimeValues').get()
		#query = real_ref.where(u'company_id', u'==', u'8T2oNGIDwyCUU6GCfWyf').get()
		company_share_value =''
		date_share=''
		real=[]
		for r in real_ref:
			#x = str((r.to_dict())['company_id'])
			#x = r.to_dict()
			if stockname ==(r.to_dict())['stock_name']:
				#real.append((r.to_dict())['company_share_value'])
				company_share_value =  (r.to_dict())['company_share_value']
				date_share = (r.to_dict())['date']
			
			
		db.collection(u'simulation_2').add({
				'user_mail':usermail,
			    'amount': amount,
			    'date':date_share,
			    'stock_name':stockname,
			    'price':company_share_value
			})	
		balance = float(balance) - float(amount)
		query = users_ref.where(u'user_mail', u'==', usermail).get()
		for p in query:
			docum= db.collection(u'simulation_1').document(p.id)
			docum.set({
    				u'total_money': balance
					}, merge=True)
		
		return redirect(url_for('sim'))



	return render_template('form_sim.html',stockname=stockname)



if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'the random string'
    app.run(host='0.0.0.0', port=5000)