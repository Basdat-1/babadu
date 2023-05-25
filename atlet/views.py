from django.shortcuts import render
from django.shortcuts import redirect
from utils.query import query
import string
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
               'namaStadium': namaStadium}
    return render(request, 'stadium_event.html', context)

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

def checkUserSex(request):
    nama = string.capwords(request.session['nama'])
    email = request.session['email']
    
    sex = query(f"""SELECT jenis_kelamin FROM ATLET NATURAL JOIN MEMBER
               WHERE nama = '{nama}' AND email = '{email}'""")[0]['jenis_kelamin']
    # true = men
    # false = women
    return sex

def joinEvent(request):
    nama_event = request.GET.get('nama_event')
    tahun = (int) (request.GET.get('tahun'))
    jenis_partai = request.GET.get('jenis_partai')
    partner = request.GET.get('partner')

    print(nama_event, tahun, jenis_partai, partner)

    id_user = getIdUser(request)

    if "Tunggal" in jenis_partai:
        check_peserta_kompetisi = query(f"""SELECT * FROM PESERTA_KOMPETISI
                                    WHERE id_atlet_kualifikasi = '{id_user}'""")
    else:
        id_partner = getIdByName(partner)
        check_ganda = query(f"""SELECT * FROM ATLET_GANDA
                        WHERE (id_atlet_kualifikasi = '{id_user}' AND id_atlet_kualifikasi_2 = '{id_partner}')
                        OR (id_atlet_kualifikasi_2 = '{id_user}' AND id_atlet_kualifikasi = '{id_partner}')""")
        if check_ganda:
            pass
            
        else:
            print("id_atlet_ganda")
            id_atlet_ganda = uuid.uuid4()
            while (isIdExist(id_atlet_ganda)):
                id_atlet_ganda = uuid.uuid4()
            
            daftar_ganda = query(f"""INSERT INTO ATLET_GANDA VALUES ('{id_atlet_ganda}', '{id_user}', '{id_partner}')""")
            print(daftar_ganda)
        check_peserta_kompetisi = query(f"""SELECT * FROM PESERTA_KOMPETISI
                                    WHERE id_atlet_ganda = '{id_atlet_ganda}'""")    
    if check_peserta_kompetisi:
        return redirect('atlet:home')
    else:
        nomor_peserta = getLatestNomorPeserta() + 1
        world_rank_peserta = getWorldRankById(id_user)
        world_tour_rank_peserta = getWorldTourRankById(id_user)
        if "Tunggal" in jenis_partai:
            daftar_peserta = query(f"""INSERT INTO PESERTA_KOMPETISI VALUES (
                                    {nomor_peserta}, NULL, '{id_user}', {world_rank_peserta}, {world_tour_rank_peserta})""")
            print(daftar_peserta)
        else:
            daftar_peserta = query(f"""INSERT INTO PESERTA_KOMPETISI VALUES (
                                    {nomor_peserta}, '{id_atlet_ganda}', NULL, {world_rank_peserta}, {world_tour_rank_peserta})""")
            print(daftar_peserta)

        jenis_partai = convertJenisPartaiName(jenis_partai)
        daftar_partai_peserta_kompetisi = query(f"""INSERT INTO PARTAI_PESERTA_KOMPETISI VALUES (
                                                '{jenis_partai}', '{nama_event}', {tahun}, {nomor_peserta})""")
        print(daftar_partai_peserta_kompetisi)

    return redirect('atlet:home')

def getIdUser(request):
    nama = string.capwords(request.session['nama'])
    email = request.session['email']
    
    id = query(f"""SELECT id FROM MEMBER
               WHERE nama = '{nama}' AND email = '{email}'""")[0]['id']
    # true = men
    # false = women
    return id

def getIdByName(nama):
    id = query(f"""SELECT id FROM MEMBER
               WHERE nama = '{nama}'""")[0]['id']
    return id

def isIdExist(id):
    check = query(f"""SELECT id FROM MEMBER WHERE id = '{id}'""")
    if not check:
        return False
    else:
        return True

# @login_required
def pilih_ujian_kualifikasi(request):
    ujian_kualifikasi = query("""SELECT * FROM UJIAN_KUALIFIKASI;""")
    # print(ujian_kualifikasi)
    context = {
        "ujian_kualifikasi": ujian_kualifikasi
    }
    return render(request, "pilih_ujian_kualifikasi.html", context)

# @login_required
def riwayat_ujian_kualifikasi(request):
    id = request.session['member_id']
    print(id)

    kualifikasi = query(f"""SELECT * FROM ATLET_KUALIFIKASI WHERE id_atlet = '{id}'""")
    print(kualifikasi)
    if not kualifikasi:
        kualifikasi = 'Non-Qualified'
    else:
        kualifikasi = 'Qualified'

    riwayat_ujian_atlet = query(f"""SELECT TAHUN, BATCH, TEMPAT, TANGGAL, HASIL_LULUS
                                        FROM ATLET_NONKUALIFIKASI_UJIAN_KUALIFIKASI
                                        WHERE id_atlet = '{id}';""")
    print(riwayat_ujian_atlet)

    context = {
        "riwayat_ujian_atlet": riwayat_ujian_atlet
    }

    return render(request, "riwayat_ujian_kualifikasi.html", context)

# @login_required
def soal_ujian_kualifikasi(request):
    return render(request, "soal_ujian_kualifikasi.html")
    
def getLatestNomorPeserta():
    nomor_peserta = query(f"""SELECT nomor_peserta FROM PESERTA_KOMPETISI
                    ORDER BY nomor_peserta DESC""")[0]['nomor_peserta']
    return nomor_peserta

def getWorldRankById(id):
    world_rank = query(f"""SELECT world_rank FROM ATLET_KUALIFIKASI
                        WHERE id_atlet = '{id}'""")[0]['world_rank']
    return world_rank

def getWorldTourRankById(id):
    world_tour_rank = query(f"""SELECT world_tour_rank FROM ATLET_KUALIFIKASI
                        WHERE id_atlet = '{id}'""")[0]['world_tour_rank']
    return world_tour_rank

def convertJenisPartaiName(name):
    if name == "Tunggal Putra":
        return "MS"
    elif name == "Tunggal Putri":
        return "WS"
    elif name == "Ganda Putra":
        return "MD"
    elif name == "Ganda Putri":
        return "WD"
    elif name == "Ganda Campuran":
        return "XD"
    else:
        return None
