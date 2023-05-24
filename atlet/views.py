from django.shortcuts import render, redirect
from utils.query import query
import string
from django.views.decorators.csrf import csrf_exempt


# Create your views here.

forms = {}

def atletHome(request):
    nama = string.capwords(request.session['nama'])
    email = request.session['email']
    print(nama, email)
    id = query(f"""SELECT id FROM MEMBER
               WHERE nama = '{nama}' AND email = '{email}'""")[0]
    id = id['id']
    print(id)

    result = query(f"""SELECT * FROM ATLET A
                    WHERE A.id = '{id}'""")[0]
    print(result)

    pelatih = query(f"""SELECT * FROM ATLET_PELATIH AP JOIN MEMBER M ON M.id = AP.id_pelatih
                    WHERE AP.id_atlet = '{id}'""")[0]
    print(pelatih)
    pelatih = pelatih['nama']
                    
    if result['jenis_kelamin'] == False:
        sex = 'Perempuan'
    else:
        sex = 'Laki-Laki'

    kualifikasi = query(f"""SELECT * FROM ATLET_KUALIFIKASI WHERE id_atlet = '{id}'""")
    print(kualifikasi)
    if not kualifikasi:
        kualifikasi = 'Non-Qualified'
    else:
        kualifikasi = 'Qualified'
    
    if result['play_right'] == True:
        play_right = 'Right-hand'
    else:
        play_right = 'Left-hand'

    point_history = query(f"""SELECT * FROM POINT_HISTORY WHERE id_atlet = '{id}'""")
    if not point_history:
        total_poin = 0
    else:
        point_history = point_history[0]
        bulan = convertMonthName(point_history['bulan'])
        total_poin = query(f"""SELECT total_point FROM
                        (SELECT total_point, CONCAT(tahun, '-', '{bulan}', '-', minggu_ke) as waktu
                        FROM POINT_HISTORY WHERE id_atlet = '{id}') as waktu_history
                        ORDER BY waktu DESC""")[0]
        total_poin = total_poin['total_point']
    
    print(total_poin)

    context = {'nama':nama,
                'email':email,
                'result':result,
                'pelatih':pelatih,
                'kualifikasi':kualifikasi,
                'sex':sex,
                'play_right':play_right,
                'total_poin':total_poin}
    return render(request, 'dashboard-atlet.html', context)

def convertMonthName(bulan):
    if bulan == "Januari":
        return '01'
    elif bulan == "Februari":
        return '02'
    elif bulan == "Maret":
        return '03'
    elif bulan == "April":
        return '04'
    elif bulan == "Mei":
        return '05'
    elif bulan == "Juni":
        return '06'
    elif bulan == "Juli":
        return '07'
    elif bulan == "Agustus":
        return '08'
    elif bulan == "September":
        return '09'
    elif bulan == "Oktober":
        return '10'
    elif bulan == "November":
        return '11'
    elif bulan == "Desember":
        return '12'
    
def daftarStadium(request):
    result = query(f"SELECT * FROM STADIUM")

    context = {'list_stadium': result}
    return render(request, 'daftar_stadium.html', context)
    
def daftarEventStadium(request, namaStadium):
    result = query(f"SELECT * FROM EVENT E WHERE E.nama_stadium = '{namaStadium}'")
    peserta_mendaftar = query(f"""SELECT COUNT(*) FROM EVENT E JOIN PESERTA_MENDAFTAR_EVENT PME
                              ON E.nama_event = PME.nama_event
                              WHERE nama_stadium = '{namaStadium}'""")[0]
    kapasitas_stadium = query(f"SELECT kapasitas FROM STADIUM WHERE nama = '{namaStadium}'")[0]
    kapasitas = (str)(peserta_mendaftar['count']) + " / " + (str)(kapasitas_stadium['kapasitas'])
    context = {'list_event': result,
               'kapasitas': kapasitas,}
    return render(request, 'stadium_event.html', context)

@csrf_exempt
def c_sponsor(request):
    if request.method != 'POST':
        return r_sponsor(request, False)
    nama_sponsor = request.POST.get("nama_sponsor")
    if not nama_sponsor:
        return r_sponsor(request, True)        
    nama_atlet = request.session["nama"]
    
    id_atlet = str(query(f"SELECT A.ID FROM MEMBER M, ATLET_SPONSOR ASP, ATLET A WHERE M.ID=A.ID AND A.ID = ASP.ID AND M.Nama='{nama_atlet}';")[0]["id"])
    id_sponsor = str(query(f"SELECT S.ID FROM SPONSOR S, ATLET A, ATLET_SPONSOR ASP WHERE S.ID=ASP.ID_SPONSOR AND A.ID = ASP.ID_ATLET AND S.nama_brand ='{nama_sponsor}';")[0]["id"])

    query(f"INSERT INTO SPONSOR VALUES ('{id_atlet}', '{id_sponsor}');")
    return redirect('/atlet/list-atlet')

def r_sponsor(request, fail):
    list_sponsor = query("SELECT S.nama_brand, ASP.tgl_mulai, ASP.tgl_selesai FROM SPONSOR S, ATLET_SPONSOR ASP WHERE S.id = ASP.id_sponsor;")
    context = {
        "list_sponsor": list_sponsor,
        "fail": False
    }

    if fail:
        context["fail"] = True
    return render(request, "c_sponsor.html", context)

def list_sponsor(request):
    nama_atlet = request.session["nama"]
    isi_table_sponsor = query("""SELECT S.nama_brand, ASP.tgl_mulai, ASP.tgl_selesai FROM ATLET A, SPONSOR S, ATLET_SPONSOR ASP WHERE S.id = ASP.id_sponsor, 
                        AND A.ID = ASP.ID AND AND A.Nama='{}';
                        """.format(nama_atlet))
    context = {
        "isi_table_sponsor": isi_table_sponsor
    }
    return render(request, "list_sponsor.html", context)