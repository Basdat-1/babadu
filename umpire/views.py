import string
from django.http import JsonResponse
from django.shortcuts import render, redirect
from utils.query import query
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from utils.query import *
from django.db import transaction

from django.views.decorators.csrf import csrf_exempt, csrf_protect


# Create your views here.
def dashboard_umpire(request):
    nama = request.session["nama"]
    email = request.session["email"]
    negara = query("""SELECT negara FROM MEMBER M, UMPIRE U WHERE M.ID=U.ID AND 
                    M.nama='{}' AND M.email='{}';
                    """.format(nama, email))[0]["negara"]
    
    context = {
        "nama": nama,
        "email": email,
        "negara": negara
    }
    return render(request, 'dashboard-umpire.html', context)


# @login_required
def daftar_atlet(request):
    atlet_kuali = query("""SELECT DISTINCT M.nama, A.tgl_lahir, A.negara_asal, A.play_right, A.height, AK.world_rank, AK.world_tour_rank, A.jenis_kelamin, P.total_point
                        FROM MEMBER M, ATLET A, ATLET_KUALIFIKASI AK, POINT_HISTORY P
                        WHERE M.ID=A.ID AND A.ID=AK.ID_atlet
                        AND A.ID=P.ID_atlet
                        AND total_point IN (
                            SELECT total_point FROM POINT_HISTORY
                            WHERE ID_atlet=P.ID_atlet
                            ORDER BY (Tahun, Bulan, Minggu_ke) LIMIT 1
                        );""")
    
    atlet_nonkuali = query("""SELECT DISTINCT M.nama, A.tgl_lahir, A.negara_asal, A.play_right, A.height, A.jenis_kelamin
                            FROM MEMBER M, ATLET A, ATLET_NON_KUALIFIKASI AN
                            WHERE M.ID=A.ID AND A.ID=AN.ID_atlet;
                            """)
    
    atlet_ganda = query("""SELECT ID_Atlet_Ganda, MA.Nama AS nama_atlet_1, MB.Nama AS nama_atlet_2, SUM(PHA.total_point + PHB.total_point) AS total_point
                        FROM MEMBER MA, MEMBER MB, ATLET_GANDA AG, POINT_HISTORY PHA, POINT_HISTORY PHB
                        WHERE AG.ID_Atlet_kualifikasi=MA.ID
                        AND AG.ID_Atlet_kualifikasi_2=MB.ID
                        AND AG.ID_Atlet_kualifikasi=PHA.ID_Atlet
                        AND AG.ID_Atlet_kualifikasi_2=PHB.ID_Atlet
                        AND PHA.total_point IN (
                            SELECT total_point FROM POINT_HISTORY
                            WHERE ID_atlet=AG.ID_Atlet_kualifikasi
                            ORDER BY (Tahun, Bulan, Minggu_ke) LIMIT 1
                        )
                        AND PHB.total_point IN (
                            SELECT total_point FROM POINT_HISTORY
                            WHERE ID_atlet=AG.ID_Atlet_kualifikasi_2
                            ORDER BY (Tahun, Bulan, Minggu_ke) LIMIT 1
                        )
                        GROUP BY (ID_Atlet_Ganda, MA.Nama , MB.Nama);
                    """)

    context = {
        "atlet_kuali": atlet_kuali,
        "atlet_nonkuali": atlet_nonkuali,
        "atlet_ganda": atlet_ganda
    }

    return render(request, "daftar_atlet.html", context)

def get_partai_kompetisi(request):
    partai_kompetisi = query("""SELECT E.Nama_event, E.Tahun, E.Nama_stadium, PK.Jenis_partai,
                            E.Kategori_Superseries, E.Tgl_mulai, E.Tgl_selesai, COUNT(PPK.nomor_peserta) AS jumlah_peserta, S.Kapasitas
                            FROM EVENT E, PARTAI_KOMPETISI PK, PARTAI_PESERTA_KOMPETISI PPK, STADIUM S
                            WHERE E.Nama_event=PK.Nama_event
                            AND E.Tahun=PK.Tahun_event
                            AND PK.Nama_event=PPK.Nama_event
                            AND PK.Tahun_event=PPK.Tahun_event
                            AND PK.Jenis_partai=PPK.Jenis_partai
                            AND E.Nama_stadium=S.Nama
                            GROUP BY E.Nama_event, E.Tahun, E.Nama_stadium, PK.Jenis_partai,
                            E.Kategori_Superseries, E.Tgl_mulai, E.Tgl_selesai, S.Kapasitas;
                        """)
    request.session['nama_event'] = partai_kompetisi[0]['nama_event']
    context = {
        "partai_kompetisi": partai_kompetisi
    }
    return render(request, "r_partai_kompetisi.html", context)

def filter_peserta(lst, tahap):
	return [d for d in lst if d["jenis_babak"]==tahap]

def juara_1_3(lst, tahap, status):
    return [d for d in lst if d["jenis_babak"]==tahap and d["status_menang"]==status]

def get_hasil_pertandingan(request):
    nama_event = request.GET.get("nama_event")
    tahun = request.GET.get("tahun")
    jenis_partai = request.GET.get("jenis_partai")
    
    info_partai = query("""SELECT PK.Jenis_partai, E.Nama_event, E.Nama_stadium, E.total_hadiah,
                        E.Kategori_Superseries, E.Tgl_mulai, E.Tgl_selesai, S.Kapasitas
                        FROM EVENT E, PARTAI_KOMPETISI PK, STADIUM S
                        WHERE E.Nama_event=PK.Nama_event
                        AND E.Tahun=PK.Tahun_event
                        AND E.Nama_stadium=S.Nama
                        AND PK.Jenis_partai='{}'
                        AND PK.Nama_event='{}'
                        AND PK.Tahun_event='{}';
                        """.format(jenis_partai, nama_event, tahun))[0]
    
    partai_ganda = ['MD', 'XD', 'WD']
    if jenis_partai in partai_ganda:
        peserta = query("""SELECT M1.nama AS nama1, M2. nama AS nama2, PM.jenis_babak, PM.status_menang
                        FROM MEMBER M1, MEMBER M2, ATLET_GANDA AG, PESERTA_KOMPETISI PK,
                        MATCH M, PESERTA_MENGIKUTI_MATCH PM
                        WHERE AG.ID_Atlet_Kualifikasi=M1.ID
                        AND AG.ID_Atlet_Kualifikasi_2=M2.ID
                        AND AG.ID_atlet_ganda=PK.ID_atlet_ganda
				        AND PM.nomor_peserta=PK.nomor_peserta
                        AND M.jenis_babak=PM.jenis_babak
                        AND M.tanggal=PM.tanggal
                        AND M.waktu_mulai=PM.waktu_mulai
                        AND (status_menang='false' OR PM.jenis_babak='FINAL')
                        AND M.nama_event='{}'
                        AND M.tahun_event='{}';
                    """.format(nama_event, tahun))
        
    else:
        peserta = query("""SELECT ME.nama AS nama1, PM.jenis_babak, PM.status_menang
                        FROM MEMBER ME, PESERTA_KOMPETISI PK,
                        MATCH M, PESERTA_MENGIKUTI_MATCH PM
                        WHERE PM.nomor_peserta=PK.nomor_peserta
                        AND M.jenis_babak=PM.jenis_babak
                        AND M.tanggal=PM.tanggal
                        AND M.waktu_mulai=PM.waktu_mulai
                        AND PK.ID_ATLET_KUALIFIKASI=ME.ID
                        AND (status_menang='false' OR PM.jenis_babak='FINAL')
                        AND M.nama_event='{}'
                        AND M.tahun_event='{}';
                    """.format(nama_event, tahun))
                    
    
    r32 = filter_peserta(peserta, "R32")
    r16 = filter_peserta(peserta, "R16")
    perempat_final = filter_peserta(peserta, "PEREMPAT FINAL")
    semifinal = filter_peserta(peserta, "SEMIFINAL")
    juara_3 = juara_1_3(peserta, "JUARA 3", True)
    juara_2 = juara_1_3(peserta, "FINAL", False)
    juara_1 = juara_1_3(peserta, "FINAL", True)
    
    context = {
        "jenis_partai": info_partai["jenis_partai"],
        "nama_event": info_partai["nama_event"],
        "nama_stadium": info_partai["nama_stadium"],
        "total_hadiah": info_partai["total_hadiah"],
        "kategori_superseries": info_partai["kategori_superseries"],
        "tgl_mulai": info_partai["tgl_mulai"],
        "tgl_selesai": info_partai["tgl_selesai"],
        "kapasitas": info_partai["kapasitas"],
        "juara_1": juara_1,
        "juara_2": juara_2,
        "juara_3": juara_3,
        "semifinal": semifinal,
        "perempat_final": perempat_final,
        "r16": r16,
        "r32": r32,
        "jumlah_peserta": len(peserta),
        "partai_ganda": partai_ganda 
    }
    return render(request, "hasil_pertandingan.html", context)

def get_member_ganda(id_atlet_ganda):
    atlet_ganda_row = query(f"""
        SELECT ag.* FROM atlet_ganda as ag WHERE ag.id_atlet_ganda = '{id_atlet_ganda}' LIMIT 1
    """)[0]

    data_member = query(f"""
        SELECT * FROM member as m WHERE m.id IN 
        ('{atlet_ganda_row['id_atlet_kualifikasi']}', '{atlet_ganda_row['id_atlet_kualifikasi_2']}')
        LIMIT 2
    """)

    return data_member

def get_member_tunggal(id_kualifikasi):
    data_member = query(f"""
        SELECT * FROM member as member WHERE member.id = '{id_kualifikasi}'
        LIMIT 1
    """)[0]

    return data_member

mapPreviousMatchBabak = {
    'R2': 'R4',
    'R4': 'R8',
    'R8': 'R16',
    'R16': 'R32',
    'R32': '',
}

mapNextMatchBabak = {
    'R2': 'R1',
    'R4': 'R2',
    'R8': 'R4',
    'R16': 'R8',
    'R32': 'R16',
}


def c_pertandingan(request, namaEvent, jenisPartai, tahun, kategori):
    jenisBabak = request.GET.get("jenisBabak")

    if jenisBabak is None:
        pesertas = query(f"""
            SELECT pk.* 
            FROM peserta_kompetisi AS pk
            INNER JOIN partai_peserta_kompetisi AS ppk
            ON pk.nomor_peserta = ppk.nomor_peserta
            WHERE ppk.jenis_partai = '{jenisPartai}' AND ppk.nama_event = '{namaEvent}' AND ppk.tahun_event = '{tahun}'
        """)
    else:
        prevJenisBabak = mapPreviousMatchBabak[jenisBabak]
        pesertas = query(f"""
            SELECT pk.*
            FROM partai_peserta_kompetisi ppk 
            INNER JOIN peserta_kompetisi pk ON pk.nomor_peserta = ppk.nomor_peserta
            INNER JOIN peserta_mengikuti_match pmm ON pmm.nomor_peserta = ppk.nomor_peserta
            WHERE ppk.nama_event = '{namaEvent}' AND ppk.jenis_partai = '{jenisPartai}' AND ppk.tahun_event = '{tahun}'
            AND pmm.jenis_babak = '{prevJenisBabak}' AND status_menang IS TRUE
        """)
        print('prev : ')
        print(prevJenisBabak)
        print(pesertas)

    pertandingans = []
    jumlah_pertandingan = len(pesertas) // 2
    for i in range(jumlah_pertandingan):
        # 0 : 0 - 1
        # 1 : 2 - 3
        # 2 : 4 - 5
        # 3 : 6 - 7
        tim_1 = pesertas[i * 2]
        tim_2 = pesertas[i * 2 + 1]
        pertandingan = {
            'tim_1': tim_1,
            'tim_2': tim_2
        }


        if tim_1['id_atlet_ganda'] != None:
            member_ganda_1 = get_member_ganda(tim_1['id_atlet_ganda'])
            tim_1['nama'] = " & ".join(map(lambda member: member['nama'], member_ganda_1))
        else:
            member_tunggal_1 = get_member_tunggal(tim_1['id_atlet_kualifikasi'])
            tim_1['nama'] = member_tunggal_1['nama']

        if tim_2['id_atlet_ganda'] != None:
            member_ganda_2 = get_member_ganda(tim_2['id_atlet_ganda'])
            tim_2['nama'] = " & ".join(map(lambda member: member['nama'], member_ganda_2))
        else:
            member_tunggal_2 = get_member_tunggal(tim_2['id_atlet_kualifikasi'])
            tim_2['nama'] = member_tunggal_2['nama']

        pertandingans.append(pertandingan)

    total_peserta=query(f"""
        SELECT COUNT(*) AS total_peserta
        FROM partai_peserta_kompetisi AS ppk
        WHERE ppk.jenis_partai = '{jenisPartai}' AND ppk.nama_event = '{namaEvent}'
        GROUP BY ppk.nama_event, ppk.jenis_partai
        LIMIT 1;
    """)

    total_peserta_real = total_peserta[0]['total_peserta']

    if total_peserta_real == 32:
        jenisPertandingan = "R32"
        jenisBabak = "R32"
    elif total_peserta_real == 16:
        jenisPertandingan = "R16"
        jenisBabak = "R16"
    elif total_peserta_real == 8:
        jenisPertandingan = "PEREMPAT FINAL"
        jenisBabak = "R8"
    elif total_peserta_real == 4:
        jenisPertandingan = "SEMIFINAL"
        jenisBabak = "R4"
    elif total_peserta_real == 2:
        # perlu dibikin case untuk perebutan juara 3 = JUARA3
        jenisPertandingan = "FINAL"
        jenisBabak = "R2"
    else:
        jenisPertandingan = ""
        jenisBabak = ""

    context = {
        'pertandingans': pertandingans,
        'namaEvent' : namaEvent,
        'tahun': tahun,
        'jenis_pertandingan': jenisPertandingan,
        'jenisPartai' : jenisPartai,
        'jenisBabak': jenisBabak,
        'total_peserta_real' : total_peserta_real,
        'kategori':kategori,
    }
    return render(request, 'c_pertandingan.html', context)

def get_datetime(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        time = request.POST.get('time')

        # Mengembalikan tanggapan JSON sebagai contoh
        response = {
            'status': 'success',
            'message': 'Tanggal dan waktu berhasil diterima',
            'date': date,
            'time': time
        }
        print(response)
        return JsonResponse(response)

@csrf_exempt
def save_match(request):
    if request.method == 'POST':
        request_body = json.loads(request.body)

        tanggal_mulai = request_body['tanggal_mulai']
        waktu_mulai = request_body['waktu_mulai']
        jenis_babak = request_body['jenis_babak']
        jenis_partai = request_body['jenis_partai']
        nama_event = request_body['nama_event']
        tahun_event = request_body['tahun_event']
        durasi = request_body['durasi']
        data_pertandingan = request_body['data_pertandingan']

        umpire_id = request.session['member_id']

        with transaction.atomic():
            row_count = query(f"""
                INSERT INTO match (jenis_babak, tanggal, waktu_mulai, nama_event, tahun_event, id_umpire, total_durasi) 
                VALUES 
                ('{jenis_babak}', '{tanggal_mulai}', '{waktu_mulai}', 
                '{nama_event}', {tahun_event}, '{umpire_id}', {durasi}) 
            """)

            if (isinstance(row_count, int) and row_count <= 0) or not isinstance(row_count, int):
                print("error")
                print(row_count)
                raise Exception("failed insert to match")
                return JsonResponse({
                    "message": "Gagal insert match",
                }, status=400)


            for i in data_pertandingan:
                tim_1_no = i['tim_1']['nomor_peserta']
                tim_2_no = i['tim_2']['nomor_peserta']
                tim_1_win = i['tim_1']['is_win']
                tim_2_win = i['tim_2']['is_win']
                
                print("test here")
                row_count = query(f"""
                    INSERT INTO peserta_mengikuti_match (jenis_babak, tanggal, waktu_mulai, nomor_peserta, status_menang)
                    VALUES ('{jenis_babak}', '{tanggal_mulai}', '{waktu_mulai}', {tim_1_no}, {tim_1_win})
                """)
                
                if (isinstance(row_count, int) and row_count <= 0) or not isinstance(row_count, int):
                    print("error")
                    print(row_count)
                    raise Exception("error insert tim 1 data")

            
                row_count = query(f"""
                    INSERT INTO peserta_mengikuti_match (jenis_babak, tanggal, waktu_mulai, nomor_peserta, status_menang)
                    VALUES ('{jenis_babak}', '{tanggal_mulai}', '{waktu_mulai}', {tim_2_no}, {tim_2_win})
                """)

                
                if (isinstance(row_count, int) and row_count <= 0) or not isinstance(row_count, int):
                    print("error")
                    print(row_count)
                    raise Exception("error insert tim 2 data")

    
        nextBabak = mapNextMatchBabak[jenis_babak]
        return JsonResponse({
            "next_babak": nextBabak,
        })

def set_point_juara_1(kategori):
    if kategori == 'S100':
        point = 1000
    elif kategori == 'S750':
        point = 750
    elif kategori == 'S500':
        point = 500
    elif kategori == 'S300':
        point = 300
    elif kategori == 'S100':
        point = 100

    return point

def set_point_juara_2(kategori):
    if kategori == 'S100':
        point = 800
    elif kategori == 'S750':
        point = 600
    elif kategori == 'S500':
        point = 400
    elif kategori == 'S300':
        point = 240
    elif kategori == 'S100':
        point = 80

    return point

    
@csrf_exempt
def save_final(request):
    if request.method == 'POST':
        request_body = json.loads(request.body)

        tanggal_mulai = request_body['tanggal_mulai']
        waktu_mulai = request_body['waktu_mulai']
        jenis_babak = request_body['jenis_babak']
        jenis_partai = request_body['jenis_partai']
        nama_event = request_body['nama_event']
        tahun_event = request_body['tahun_event']
        durasi = request_body['durasi']
        data_pertandingan = request_body['data_pertandingan']

        umpire_id = request.session['member_id']

        with transaction.atomic():
            row_count = query(f"""
                INSERT INTO match (jenis_babak, tanggal, waktu_mulai, nama_event, tahun_event, id_umpire, total_durasi) 
                VALUES 
                ('{jenis_babak}', '{tanggal_mulai}', '{waktu_mulai}', 
                '{nama_event}', {tahun_event}, '{umpire_id}', {durasi}) 
            """)

            if (isinstance(row_count, int) and row_count <= 0) or not isinstance(row_count, int):
                print("error")
                print(row_count)
                raise Exception("failed insert to match")

            for i in data_pertandingan:
                tim_1_no = i['tim_1']['nomor_peserta']
                tim_2_no = i['tim_2']['nomor_peserta']
                tim_1_win = i['tim_1']['is_win']
                tim_2_win = i['tim_2']['is_win']
                
                print("test here")
                row_count = query(f"""
                    INSERT INTO peserta_mengikuti_match (jenis_babak, tanggal, waktu_mulai, nomor_peserta, status_menang)
                    VALUES ('{jenis_babak}', '{tanggal_mulai}', '{waktu_mulai}', {tim_1_no}, {tim_1_win})
                """)
                
                if (isinstance(row_count, int) and row_count <= 0) or not isinstance(row_count, int):
                    print("error")
                    print(row_count)
                    raise Exception("error insert tim 1 data")
            
                row_count = query(f"""
                    INSERT INTO peserta_mengikuti_match (jenis_babak, tanggal, waktu_mulai, nomor_peserta, status_menang)
                    VALUES ('{jenis_babak}', '{tanggal_mulai}', '{waktu_mulai}', {tim_2_no}, {tim_2_win})
                """)

                if (isinstance(row_count, int) and row_count <= 0) or not isinstance(row_count, int):
                    print("error")
                    print(row_count)
                    raise Exception("error insert tim 2 data")
                
                # add points here
                
        #     get_kategori = query(f""" 
        #             SELECT KATEGORI_SUPERSERIES FROM EVENT WHERE NAMA_EVENT = '{nama_event}'
        #     """)
        #     get_kategori = get_kategori[0]['kategori_superseries']
                
        #     point_juara_1 = set_point_juara_1(get_kategori)
        #     point_juara_2 = set_point_juara_2(get_kategori)

        #     print(tim_1_no)
        #     print(tim_2_no)
        #     print(tim_1_win)
        #     print(tim_2_win)
        #     print(point_juara_1)
        #     print(point_juara_2)

        #     id_tim_1 = query(f"""
        #             SELECT ID_ATLET_KUALIFIKASI
        #             FROM peserta_kompetisi as pk WHERE
        #             pk.nomor_peserta = {tim_1_no}
        #     """)

        #     id_tim_2 = query(f"""
        #             SELECT ID_ATLET_KUALIFIKASI
        #             FROM peserta_kompetisi as pk WHERE
        #             pk.nomor_peserta = {tim_2_no}
        #     """)

        #     if tim_1_win == True:
        #             query_update_point_tim_1 = query(f"""
        #                 UPDATE point_history
        #                 SET total_point = total_point + {point_juara_1}
        #                 WHERE id_atlet = {id_tim_1}"""
        #             )
        #     else:
        #             query_update_point_tim_1 = query(f"""
        #                 UPDATE point_history
        #                 SET total_point = total_point + {point_juara_2}
        #                 WHERE id_atlet = {id_tim_1}"""
        #             )

        #     if tim_2_win == True:
        #             query_update_point_tim_2 = query(f"""
        #                 UPDATE point_history
        #                 SET total_point = total_point + {point_juara_1}
        #                 WHERE id_atlet = {id_tim_2}"""
        #             )
        #     else:
        #             query_update_point_tim_2 = query(f"""
        #                 UPDATE point_history
        #                 SET total_point = total_ point + {point_juara_2}
        #                 WHERE id_atlet = {id_tim_2}"""
        #             )

        # cursor.execute(query_update_point_tim_1)
        # cursor.execute(query_update_point_tim_2)

        nextBabak = mapNextMatchBabak[jenis_babak]
        return JsonResponse({
            "next_babak": nextBabak,
        })
        
    
    
def save_stopwatch(request):
    if request.method == 'POST':
        elapsed_time = request.POST.get('elapsed_time')
        # Save the elapsed_time value to the desired location (e.g., database)
        response = {
            'elapsed_time': elapsed_time
        }
        return JsonResponse(response)
    
def update_score(request):
    if request.method == 'POST':
        team = request.POST.get('team')
        row = request.POST.get('row')
        action = request.POST.get('action')

        # Lakukan operasi sesuai aksi (tambah atau kurang) pada skor yang sesuai
        # Misalnya, dapat menyimpan nilai skor dalam database atau variabel sesuai kebutuhan Anda

        # Contoh: Simpan skor dalam session
        session_key = f'score-team{team}-row{row}'
        current_score = request.session.get(session_key, 0)
        if action == 'plus':
            current_score += 1
        elif action == 'minus':
            current_score -= 1
        request.session[session_key] = current_score

        response = {
            'current_score': current_score
        }
        return JsonResponse(response)
    
def list_ujian_kualifikasi(request):
    ujian_kualifikasi = query("""SELECT * FROM UJIAN_KUALIFIKASI;""")
    # print(ujian_kualifikasi)
    context = {
        "ujian_kualifikasi": ujian_kualifikasi
    }
    return render(request, "list_ujian_kualifikasi.html", context)