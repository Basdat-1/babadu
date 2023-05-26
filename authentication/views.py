import uuid
from django.shortcuts import render, redirect
from utils.query import query
from django.views.decorators.csrf import csrf_exempt
from psycopg2.errors import RaiseException

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
  
def get_uuid_existed():
   uuid_member =  query("SELECT ID FROM MEMBER;")
   return [member['id'] for member in uuid_member]
  
@csrf_exempt
def register_atlet(request):
    if request.method == 'POST':
        id = uuid.uuid4()
        while (id in get_uuid_existed()):
           id = uuid.uuid4()
        nama = str(request.POST['nama'])
        email = str(request.POST['email'])
        negara = str(request.POST['negara'])
        tgl_lahir = request.POST['tgl_lahir']
        play = request.POST["play"]
        height = int(request.POST['height'])
        sex = str(request.POST['sex'])

        if play == "left":
           play_bool = False
        else:
           play_bool = True

        if sex == 'm':
           sex_bool = True
        else:
           sex_bool = False

        isValid = id and nama and email and negara and tgl_lahir and play and height and sex
        if isValid:
            message = query(f"INSERT INTO MEMBER VALUES('{id}', '{nama}', '{email}')")
            if type(message) == RaiseException:
               context = {
                  "message": "Email sudah pernah didaftarkan"
               }
               return render(request, 'register-atlet.html', context)
            query(f"INSERT INTO ATLET VALUES('{id}', '{tgl_lahir}', '{negara}', {play_bool}, '{height}', NULL, {sex_bool})")
            return redirect("/login")
        else:
            context = {"message": "Mohon masukan data Anda dengan benar"}
            return render(request, 'register-atlet.html', context)
    else:
        return render(request, 'register-atlet.html')
    
@csrf_exempt
def register_umpire(request):
    if request.method == 'POST':
        id = uuid.uuid4()
        while (id in get_uuid_existed()):
           id = uuid.uuid4()
        print(id)
        nama = str(request.POST['nama'])
        email = str(request.POST['email'])
        negara = str(request.POST['negara'])
        isValid = id and nama and email and negara

        if isValid:
            message = query(f"INSERT INTO MEMBER VALUES('{id}', '{nama}', '{email}')")
            if type(message) == RaiseException:
               context = {
                  "message": "Email sudah pernah didaftarkan"
               }
               return render(request, 'register-umpire.html', context)
            query(f"INSERT INTO UMPIRE VALUES('{id}', '{negara}')")
            return redirect("/login")
        
        else:
            context = {"message": "Mohon masukan data Anda dengan benar"}
            return render(request, 'register-umpire.html', context)
    else:
        return render(request, 'register-umpire.html')
    
@csrf_exempt
def register_pelatih(request):
    if request.method == 'POST':
        id = uuid.uuid4()
        while (id in get_uuid_existed()):
           id = uuid.uuid4()
        nama = str(request.POST['nama'])
        email = str(request.POST['email'])
        kategori = request.POST.getlist('kategori')
        tgl_mulai = str(request.POST['tgl_mulai'])
        isValid = id and nama and email and kategori and tgl_mulai

        if isValid:
            message = query(f"INSERT INTO MEMBER VALUES('{id}', '{nama}', '{email}')")
            if type(message) == RaiseException:
               context = {
                  "message": "Email sudah pernah didaftarkan"
               }
               return render(request, 'register-pelatih.html', context)
            query(f"INSERT INTO PELATIH VALUES('{id}', '{tgl_mulai}')")

            for k in kategori:
               id_kategori = query(f"SELECT ID FROM SPESIALISASI WHERE SPESIALISASI='{k}';")[0]['id']
               query(f"INSERT INTO PELATIH_SPESIALISASI VALUES('{id}', '{id_kategori}')")

            return redirect("/login")
        else:
            context = {"message": "Mohon masukan data Anda dengan benar"}
            return render(request, 'register-pelatih.html', context)
    else:
        return render(request, 'register-pelatih.html')
  
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
    return redirect('/login')
  request.session.flush()
  request.session.clear_expired()
  return redirect('/')