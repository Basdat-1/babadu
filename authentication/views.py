import uuid
from django.shortcuts import render, redirect
from utils.query import query
from django.views.decorators.csrf import csrf_exempt

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
    return 'umpire', is_umpire[0]['id']

  is_pelatih = query(f"SELECT M.ID FROM MEMBER M, PELATIH P WHERE M.ID=P.ID AND M.Email='{email}'")
  if len(is_pelatih) > 0:
    return 'pelatih', is_pelatih[0]['id']

  is_atlet = query(f"SELECT M.ID FROM MEMBER M, ATLET A WHERE M.ID=A.ID AND M.Email='{email}'")
  if len(is_atlet) > 0:
    return 'atlet', is_atlet[0]['id']
  else:
    return '', ''

  
def register(request):
  if request.method != 'POST':
    return render(request, 'register.html')
  
def register_atlet(request):
  if request.method != 'POST':
    return render(request, 'register-atlet.html')
  
@csrf_exempt
def register_atlet(request):
    if request.method == 'POST':
        id = uuid.uuid4()
        nama = str(request.POST['nama'])
        email = str(request.POST['email'])
        negara = str(request.POST['negara'])
        tgl_lahir = str(request.POST['tgl_lahir'])
        play = str(request.POST['play'])
        height = int(request.POST['height'])
        sex = str(request.POST['sex'])

        # if play 

        isValid = id and nama and email and negara and tgl_lahir and play and height and sex

        if isValid:
            member = query(f"INSERT INTO MEMBER VALUES('{id}, {nama}', '{email}')")
            print(member)
            atlet = query(f"INSERT INTO ATLET VALUES('{id}', '{tgl_lahir}', '{negara}', '{play}', '{height}', NULL, '{sex}')")
            print(atlet)
            atlet_non_kualifikasi = query(f"INSERT INTO ATLET_NON_KUALIFIKASI VALUES('{id}')")
            print(atlet_non_kualifikasi)

            return redirect("/login")
        else:
            return render(request, 'register-atlet.html')
    else:
        return render(request, 'register-atlet.html')
  
@csrf_exempt
def login(request):
  next = request.GET.get("next")
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

  role, member_id = get_role(email)
  if not role:
    context = {'fail': True}
    return render(request, "login.html", context)
  else:
    request.session["nama"] = nama
    request.session["email"] = email
    request.session["role"] = role
    request.session["member_id"] = str(member_id)
    request.session.set_expiry(0)
    request.session.modified = True

    if next != None and next != "None":
      return redirect(next)
    else:
      # redirect to dashboard
      if role == 'umpire':
        return redirect('/umpire')
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