from django.shortcuts import render, redirect
from django.shortcuts import redirect
from utils.query import query
import string
from django.views.decorators.csrf import csrf_exempt
from django.db import DatabaseError

import uuid

# Create your views here.


def atletHome(request):
    nama = string.capwords(request.session['nama'])
    email = request.session['email']
    id = request.session["member_id"]

    result = query(f"""SELECT * FROM ATLET A
                    WHERE A.id = '{id}'""")[0]

    pelatih = query("""SELECT * FROM ATLET_PELATIH AP 
                    JOIN MEMBER M ON M.id = AP.id_pelatih
                    WHERE AP.id_atlet = '{}'
                    """.format(id))
    
    if len(pelatih) == 0:
        pelatih = '-'
    else:
        pelatih = ', '.join([p["nama"] for p in pelatih])
                    
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
    result = query(f"SELECT * FROM EVENT WHERE nama_stadium = '{namaStadium}'")
    context = {'list_event': result,
               'kapasitas': kapasitas,}
    return render(request, 'stadium_event.html', context)

@csrf_exempt
def c_sponsor(request):
    print("test")
    if request.method != 'POST':
        return r_sponsor(request, False)
    print(request.POST)
    nama_sponsor = request.POST.get("nama_sponsor")
    tanggal_mulai = request.POST.get("tanggal_mulai")
    tanggal_selesai = request.POST.get("tanggal_selesai")
    print(nama_sponsor)
    if not nama_sponsor:
        return r_sponsor(request, True)        
    id_atlet = request.session["member_id"]
    id_sponsor = str(query(f"SELECT S.ID FROM SPONSOR S WHERE S.nama_brand ='{nama_sponsor}';")[0]["id"])
    print(id_sponsor)
    query(f"INSERT INTO ATLET_SPONSOR VALUES ('{id_atlet}', '{id_sponsor}', '{tanggal_mulai}', '{tanggal_selesai}');")

    return redirect('/atlet/list-sponsor')
def list_sponsor(request):
    id_atlet = request.session["member_id"]
    isi_table_sponsor = query("""SELECT S.nama_brand, ASP.tgl_mulai, ASP.tgl_selesai FROM ATLET A, SPONSOR S, ATLET_SPONSOR ASP WHERE S.id = ASP.id_sponsor AND A.ID = ASP.ID_ATLET AND A.ID='{}';
                        """.format(id_atlet))
    context = {
        "isi_table_sponsor": isi_table_sponsor
    }
    return render(request, "list_sponsor.html", context)

def r_sponsor(request, fail):
    id_atlet = request.session["member_id"]
    list_sponsor = query(f"SELECT S.nama_brand FROM SPONSOR S WHERE NOT EXISTS(SELECT S.nama_brand FROM ATLET_SPONSOR ASP WHERE S.id = ASP.id_sponsor AND ASP.id_atlet= '{id_atlet}');")
    context = {
        "list_sponsor": list_sponsor,
        "fail": False
    }

    if fail:
        context["fail"] = True
    return render(request, "c_sponsor.html", context)

def enrolled_event(request):
    id_atlet = request.session["member_id"]
    list_event = query(f""" SELECT E.nama_event, E.tahun, E.nama_stadium, E.kategori_superseries, E.tgl_mulai, E.tgl_selesai  FROM EVENT E 
                    JOIN PARTAI_KOMPETISI PKM ON E.nama_event = PKM.nama_event
                    JOIN partai_peserta_kompetisi PPK  ON (PPK.nama_event=E.nama_event AND PPK.tahun_event = E.tahun AND PPK.jenis_partai = PKM.jenis_partai)
                    WHERE PPK.nomor_peserta IN (SELECT nomor_peserta
                    FROM peserta_kompetisi PK JOIN atlet_ganda AG ON PK.id_atlet_ganda = AG.id_atlet_ganda
                    WHERE '{id_atlet}' IN (AG.id_atlet_kualifikasi, AG.id_atlet_kualifikasi_2, PK.id_atlet_kualifikasi)); """)
    context = {
        "list_event": list_event
    }
    if request.method == 'POST':
        id_atlet = request.POST.get('id_atlet')
        nama_event = request.POST.get('nama_event')
        tahun = request.POST.get('tahun')

        delete_enrolled = query(f"""
            DELETE FROM PESERTA_MENDAFTAR_EVENT 
            WHERE nomor_peserta IN (
                SELECT nomor_peserta
                FROM PESERTA_KOMPETISI
                WHERE id_atlet_kualifikasi = '{id_atlet}'
            )
            AND nama_event = '{nama_event}' 
            AND tahun = '{tahun}'
            """)

        if delete_enrolled == 0:
            context['message'] = 'You cannot unenroll from uncompleted event.'
        return redirect('/atlet/enrolled-event')

    return render(request, "enrolled_event.html", context)



def enrolled_partai_kompetisi(request) :
    id_atlet = request.session["member_id"]
    list_partai_kompetisi_event = query(f""" SELECT E.nama_event, E.tahun, E.nama_stadium,PPK.jenis_partai ,E.kategori_superseries, E.tgl_mulai, E.tgl_selesai FROM EVENT E 
                                    JOIN PARTAI_KOMPETISI ParKom ON E.nama_event = ParKom.nama_event
                                    JOIN partai_peserta_kompetisi PPK  ON (PPK.nama_event=E.nama_event AND PPK.tahun_event = E.tahun AND PPK.jenis_partai = ParKom.jenis_partai)
                                    WHERE PPK.nomor_peserta IN (SELECT nomor_peserta
                                    FROM peserta_kompetisi PK
                                    JOIN atlet_ganda AG ON PK.id_atlet_ganda = AG.id_atlet_ganda
                                    WHERE '{id_atlet}' IN (AG.id_atlet_kualifikasi, AG.id_atlet_kualifikasi_2, PK.id_atlet_kualifikasi))
                                    ; """)
    print(list_partai_kompetisi_event)
    context = {
        "list_partai_kompetisi_event": list_partai_kompetisi_event
    }
    return render(request, "enrolled_partai_kompetisi_event.html", context)




def daftarPartaiKompetisi(request, namaStadium, namaEvent, tahunEvent):
    user_sex = checkUserSex(request)

    result = query(f"""SELECT * FROM EVENT WHERE nama_event = '{namaEvent}' AND tahun = '{tahunEvent}'""")[0]
    jumlah_peserta = query(f"""SELECT COUNT(nomor_peserta) FROM PESERTA_MENDAFTAR_EVENT
                      WHERE nama_event = '{namaEvent}' AND tahun = '{tahunEvent}'""")[0]['count']
    kapasitas_stadium = query(f"""SELECT kapasitas FROM STADIUM WHERE nama = '{namaStadium}'""")[0]['kapasitas']

    list_kategori = query(f"""SELECT jenis_partai FROM PARTAI_KOMPETISI
                        WHERE nama_event = '{namaEvent}' AND tahun_event = '{tahunEvent}'""")
    print(list_kategori)
    list_partai = []

    list_atlet_putra = query(f"""SELECT nama FROM ATLET_KUALIFIKASI AK
                            JOIN ATLET A ON AK.id_atlet = A.id
                            JOIN MEMBER M ON A.id = M.id
                            WHERE A.jenis_kelamin = 'True' AND id_atlet NOT IN
                            (SELECT id_atlet_kualifikasi
                            FROM ATLET_GANDA
                            UNION
                            SELECT id_atlet_kualifikasi_2
                            FROM ATLET_GANDA)""")
    list_atlet_putri = query(f"""SELECT nama FROM ATLET_KUALIFIKASI AK
                            JOIN ATLET A ON AK.id_atlet = A.id
                            JOIN MEMBER M ON A.id = M.id
                            WHERE A.jenis_kelamin = 'False' AND id_atlet NOT IN
                            (SELECT id_atlet_kualifikasi
                            FROM ATLET_GANDA
                            UNION
                            SELECT id_atlet_kualifikasi_2
                            FROM ATLET_GANDA)""")
    list_atlet_putra_putri = query(f"""SELECT nama FROM ATLET_KUALIFIKASI AK
                            JOIN ATLET A ON AK.id_atlet = A.id
                            JOIN MEMBER M ON A.id = M.id
                            WHERE id_atlet NOT IN
                            (SELECT id_atlet_kualifikasi
                            FROM ATLET_GANDA
                            UNION
                            SELECT id_atlet_kualifikasi_2
                            FROM ATLET_GANDA)""")
    
    for kategori in list_kategori:
        print(kategori)
        dict_kategori = {}

        if kategori['jenis_partai'] == 'MS':
            dict_kategori['jenis_partai'] = 'Tunggal Putra'
            dict_kategori["list_atlet"] = "-"
            kapasitas_partai = query(f"""SELECT COUNT(*) FROM PARTAI_PESERTA_KOMPETISI
                                WHERE jenis_partai = 'MS' AND nama_event = '{namaEvent}'
                                AND tahun_event = '{tahunEvent}'""")[0]
            dict_kategori['kapasitas'] = kapasitas_partai['count']
            if user_sex == True:
                dict_kategori['joinable'] = (dict_kategori['kapasitas'] < kapasitas_stadium)
            else:
                dict_kategori['joinable'] = False
            
        elif kategori['jenis_partai'] == 'WS':
            dict_kategori['jenis_partai'] = 'Tunggal Putri'
            dict_kategori["list_atlet"] = "-"
            kapasitas_partai = query(f"""SELECT COUNT(*) FROM PARTAI_PESERTA_KOMPETISI
                                WHERE jenis_partai = 'WS' AND nama_event = '{namaEvent}'
                                AND tahun_event = '{tahunEvent}'""")[0]
            dict_kategori['kapasitas'] = kapasitas_partai['count']
            if user_sex == False:
                dict_kategori['joinable'] = (dict_kategori['kapasitas'] < kapasitas_stadium)
            else:
                dict_kategori['joinable'] = False
            
        elif kategori['jenis_partai'] == 'MD':
            dict_kategori['jenis_partai'] = 'Ganda Putra'
            dict_kategori["list_atlet"] = list_atlet_putra
            kapasitas_partai = query(f"""SELECT COUNT(*) FROM PARTAI_PESERTA_KOMPETISI
                                WHERE jenis_partai = 'MD' AND nama_event = '{namaEvent}'
                                AND tahun_event = '{tahunEvent}'""")[0]
            dict_kategori['kapasitas'] = kapasitas_partai['count']
            if user_sex == True:
                dict_kategori['joinable'] = (dict_kategori['kapasitas'] < kapasitas_stadium)
            else:
                dict_kategori['joinable'] = False
            
        elif kategori['jenis_partai'] == 'WD':
            dict_kategori['jenis_partai'] = 'Ganda Putri'
            dict_kategori["list_atlet"] = list_atlet_putri
            kapasitas_partai = query(f"""SELECT COUNT(*) FROM PARTAI_PESERTA_KOMPETISI
                                WHERE jenis_partai = 'WD' AND nama_event = '{namaEvent}'
                                AND tahun_event = '{tahunEvent}'""")[0]
            dict_kategori['kapasitas'] = kapasitas_partai['count']
            if user_sex == False:
                dict_kategori['joinable'] = (dict_kategori['kapasitas'] < kapasitas_stadium)
            else:
                dict_kategori['joinable'] = False
            
        else:
            dict_kategori['jenis_partai'] = 'Ganda Campuran'
            dict_kategori["list_atlet"] = list_atlet_putra_putri
            kapasitas_partai = query(f"""SELECT COUNT(*) FROM PARTAI_PESERTA_KOMPETISI
                                WHERE jenis_partai = 'XD' AND nama_event = '{namaEvent}'
                                AND tahun_event = '{tahunEvent}'""")[0]
            dict_kategori['kapasitas'] = kapasitas_partai['count']
            dict_kategori['joinable'] = (dict_kategori['kapasitas'] < kapasitas_stadium)
            
        list_partai.append(dict_kategori)
        
    context = {'result':result,
               'jumlah_peserta':jumlah_peserta,
               'kapasitas_stadium': kapasitas_stadium,
               'list_partai':list_partai,}
    return render(request, 'form_partai_kompetisi.html', context)