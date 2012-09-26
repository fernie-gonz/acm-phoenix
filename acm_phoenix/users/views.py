B1;2802;0cfrom flask import Blueprint, request, render_template, flash, g, session, redirect, url_for

# WePay transaction
from wepay import WePay
import hashlib, random, os, base64
from datetime import datetime

# Signature storage
from signpad2image.signpad2image import s2i
import StringIO

# Google OAuth2
from oauth2client.client import OAuth2WebServerFlow
from apiclient.discovery import build
import httplib2

from acm_phoenix import db, app
from acm_phoenix.users import constants as USER
from acm_phoenix.users.forms import RegisterForm
from acm_phoenix.users.models import User
from acm_phoenix.users.decorators import requires_login

mod = Blueprint('users', __name__, url_prefix='')

flow = OAuth2WebServerFlow(client_id=app.config['GOOGLE_CLIENT_ID'],
                           client_secret=app.config['GOOGLE_CLIENT_SECRET'],
                           scope='https://www.googleapis.com/auth/userinfo.email',
                           redirect_uri='http://acm.frvl.us:5000/oauth2callback')

@mod.route('/profile/')
@requires_login
def home():
  """
  Display User profile
  """
  return render_template("users/profile.html", user=g.user)

@mod.route('/login/', methods=['GET', 'POST'])
def login():
  """
  Login with rmail account using Google OAuth2
  """
  auth_uri = flow.step1_get_authorize_url()
  return redirect(auth_uri)

  
def wepay_membership_response(user):
  """
  Make a WePay API call for membership payment and return the response.
  """
  # Generate verification_key for wepay payment.
  random_string = base64.urlsafe_b64encode(os.urandom(30))
  verification_key = hashlib.sha224(random_string + user.email +
                                    user.name).hexdigest()

  user.wepay_verification = verification_key
  db.session.commit()

  # WePay Application settings
  account_id = 319493
  access_token = '6dd6802f8ebef4992308a0e4f7698c275781ac36854f9451127115d995d8cda7'
  production = False

  wepay = WePay(production, access_token)
  redirect_url = 'http://acm.frvl.us:5000/verify/' + verification_key

  response = wepay.call('/checkout/create', {
      'account_id': account_id,
      'amount': '20.00',
      'short_description': '1 year ACM Club Membership',
      'mode': 'regular',
      'type': 'SERVICE',
      'redirect_uri': redirect_url
  })

  return response

@mod.route('/register/', methods=['GET', 'POST'])
def register():
  """
  Registration Form
  """
  form = RegisterForm(request.form)
  if form.validate_on_submit():
    # If netid and email are unique, create an user instance not yet stored in the database
    user = User.query.filter_by(netid=form.netid.data, email=form.email.data).first()
    if user:
      flash(u'NetID/Email already registred', 'error')
      return render_template("users/register.html", form=form)

    raw_signature = request.form['output']
    
    # Convert drawn signature to base64 encoded image.
    if raw_signature.find("data:image") == -1:
      PIL_image = s2i(raw_signature,
                      input_image=os.path.abspath("acm_phoenix/static/packages/signpad2image/signpad2image/blanksig.png"),
                      nosig_image=os.path.abspath("acm_phoenix/static/packages/signpad2image/signpad2image/nosig.png"))
      output =  StringIO.StringIO()
      PIL_image.save(output, format="PNG")
      sig_img = "data:image/png;base64," + base64.b64encode(output.getvalue())
      output.close()
    else:
      sig_img = raw_signature

    user = User(form.name.data, form.netid.data, form.email.data, \
                  form.standing.data, form.major.data, \
                  form.shirt_size.data, form.description.data, sig_img)
    user.member = True

    # Insert the record in our database and commit it
    db.session.add(user)
    db.session.commit()

    # Log the user in, as he now has an id
    session['user_id'] = user.id

    # flash will display a message to the user
    flash('Thanks for registering')

    
    if form.reg_and_pay.data == True:
      response = wepay_membership_response(user)
      user.wepay_checkout_id = response['checkout_id']
      db.session.add(user)
      db.session.commit()
      return redirect(response['checkout_uri'])
    else:
      # redirect user to the 'home' method of the user module.
      return redirect(url_for('users.home'))
  return render_template("users/register.html", form=form)

@mod.route('/verify/<string:verification_key>')
@requires_login
def verify_membership_payment(verification_key):
  # Notice that accepting verification_key as a string automatically cuts off
  # the trailing ?checkout_uri=##### from the WePay redirect.
  user = User.query.filter_by(wepay_verification=verification_key).first()
  if user:
    flash('Your membership payment has been received. Thank you!;')
    user.membership_status = USER.PAID
    user.member_since = datetime.now()
    user.membership_paid_on = user.member_since
    db.session.add(user)
    db.session.commit()
    session['user_id'] = user.id

  return redirect('/')
  
@mod.route('/paymembership/')
@requires_login
def payment_redirect():
  user = User.query.get(session['user_id'])
  response = wepay_membership_response(user)
  user.wepay_checkout_id = response['checkout_id']
  db.session.add(user)
  db.session.commit()
  return redirect(response['checkout_uri'])

@mod.route('/oauth2callback/')
def authenticate_user():
  error = request.args.get('error')
  if error:
    return redirect(url_for('users.home'))

  # Get OAuth2 authentication code
  code = request.args.get('code')

  # Exchange code for fresh credentials
  credentials = flow.step2_exchange(code)

  # Extract email and email verification
  id_token = credentials.id_token
  email = id_token['email']
  verified_email = id_token['verified_email']

  if verified_email == 'true':
    # Find user with this email
    user = User.query.filter_by(email=email).first()
    if user is None:
      flash(u'We couldn\'t find any users with that email. You must register to be a member before logging in with rmail', 'error')
      return redirect('/register')
    else:
      # Log them in and send them to their profile page
      session['user_id'] = user.id
      return redirect(url_for('users.home'))
  else:
    flash(u'Sorry, we couldn\'t verify your email', 'error')
    return redirect('/')
