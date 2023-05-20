from django.shortcuts import render, redirect
from utils.query import query
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import uuid;

def index(request):
    return render(request, 'index.html')

def check_session(request):
  '''Check apakah info user masih ada di session atau belum'''
  try:
    request.session["nama"]
    return True
  except:
    return False

def get_role(email):
  is_umpire = query(f"SELECT M.ID FROM MEMBER M, UMPIRE U WHERE M.ID=U.ID AND M.Email='{email}'")
  if len(is_umpire) > 0:
    return 'umpire'

  is_pelatih = query(f"SELECT M.ID FROM MEMBER M, PELATIH P WHERE M.ID=P.ID AND M.Email='{email}'")
  if len(is_pelatih) > 0:
    return 'pelatih'

  is_atlet = query(f"SELECT M.ID FROM MEMBER M, ATLET A WHERE M.ID=A.ID AND M.Email='{email}'")
  if len(is_atlet) > 0:
    return 'atlet'
  else:
    return ''
  
def register(request):
  if request.method != 'POST':
    return render(request, 'register.html')

@csrf_exempt
def login(request):
  if request.method != "POST":
    return login_view(request)

  nama=''
  email=''

  if check_session(request):
    nama = request.session['nama']
    email = request.session['email']
  else:
    nama = request.POST['nama']
    email = request.POST['email']

  role = get_role(email)
  if not role:
    context = {'fail': True}
    return render(request, "login.html", context)
  else:
    request.session["nama"] = nama
    request.session["email"] = email
    request.session["role"] = role
    request.session.set_expiry(0)
    request.session.modified = True

  # redirect to dashboard
  if role == 'umpire':
    return redirect('/umpire') # path to change
  elif role == 'pelatih':
    return redirect('/pelatih')
  else:
    return redirect('/atlet')

def login_view(request):
  return render(request, "login.html")

def logout(request):
  if not check_session(request):
    return redirect('login/')
  request.session.flush()
  request.session.clear_expired()
  return redirect('/')