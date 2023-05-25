from django.shortcuts import render, redirect
from utils.query import query
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
def dashboard_pelatih(request):
    nama = request.session["nama"]
    email = request.session["email"]
    id_pelatih = request.session["member_id"]
    spesialisasi = query("""SELECT S.SPESIALISASI
                    FROM SPESIALISASI S, PELATIH_SPESIALISASI PS
                    WHERE S.ID=PS.ID_SPESIALISASI
                    AND ID_PELATIH='{}';
                    """.format(id_pelatih))
    spesialisasi = ', '.join([s["spesialisasi"] for s in spesialisasi])

    tgl_mulai = query(f"SELECT tanggal_mulai FROM PELATIH WHERE ID='{id_pelatih}'")[0]["tanggal_mulai"]
    
    context = {
        "nama": nama,
        "email": email,
        "spesialisasi": spesialisasi,
        "tgl_mulai": tgl_mulai
    }
    
    return render(request, 'dashboard-pelatih.html', context)


# @login_required
@csrf_exempt
def c_latih_atlet(request):
    if request.method != 'POST':
        return latih_atlet_view(request, False)
    
    nama_atlet = request.POST.get("nama_atlet")
    if not nama_atlet:
        return latih_atlet_view(request, True)        
    
    id_pelatih = request.session["member_id"]
    id_atlet = str(query(f"SELECT ID FROM MEMBER WHERE Nama='{nama_atlet}';")[0]["id"])

    query(f"INSERT INTO ATLET_PELATIH VALUES ('{id_pelatih}', '{id_atlet}');")
    return redirect('/pelatih/list-atlet')

def latih_atlet_view(request, fail):
    list_atlet = query("SELECT M.Nama FROM MEMBER M, ATLET A WHERE M.ID=A.ID;")
    context = {
        "list_atlet": list_atlet,
        "fail": False
    }

    if fail:
        context["fail"] = True
    return render(request, "c_latih_atlet.html", context)

def list_atlet(request):
    nama_pelatih = request.session["nama"]
    atlet_dilatih = query("""SELECT MA.Nama, MA.Email, A.World_rank
                        FROM MEMBER MA, MEMBER MP, ATLET A, ATLET_PELATIH AP, PELATIH P 
                        WHERE MA.ID=A.ID
                        AND MP.ID=P.ID
                        AND AP.ID_Pelatih=P.ID
                        AND AP.ID_Atlet=A.ID
                        AND MP.Nama='{}';
                        """.format(nama_pelatih))
    context = {
        "atlet_dilatih": atlet_dilatih
    }
    return render(request, "list_atlet.html", context)