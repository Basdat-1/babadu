from django.shortcuts import render
from utils.query import query
import string

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
    result = query(f"SELECT * FROM EVENT WHERE nama_stadium = '{namaStadium}'")
    context = {'list_event': result,
               'namaStadium': namaStadium}
    return render(request, 'stadium_event.html', context)

def daftarPartaiKompetisi(request, namaStadium, namaEvent, tahunEvent):
    result = query(f"""SELECT * FROM EVENT WHERE nama_event = '{namaEvent}' AND tahun = '{tahunEvent}'""")[0]
    jumlah_peserta = query(f"""SELECT COUNT(nomor_peserta) FROM PESERTA_MENDAFTAR_EVENT
                      WHERE nama_event = '{namaEvent}' AND tahun = '{tahunEvent}'""")[0]
    kapasitas_stadium = query(f"""SELECT kapasitas FROM STADIUM WHERE nama = '{namaStadium}'""")[0]['kapasitas']
    
    print(result)

    list_kategori = query(f"""SELECT jenis_partai FROM PARTAI_KOMPETISI
                        WHERE nama_event = '{namaEvent}' AND tahun_event = '{tahunEvent}'""")
    print(list_kategori)
    list_partai = []

    list_atlet_putra = query(f"""SELECT id_atlet FROM ATLET_KUALIFIKASI AK
                            JOIN ATLET A ON AK.id_atlet = A.id
                            WHERE A.jenis_kelamin = 'True' AND id_atlet NOT IN
                            (SELECT id_atlet_kualifikasi
                            FROM ATLET_GANDA
                            UNION
                            SELECT id_atlet_kualifikasi_2
                            FROM ATLET_GANDA)""")
    list_atlet_putri = query(f"""SELECT id_atlet FROM ATLET_KUALIFIKASI AK
                            JOIN ATLET A ON AK.id_atlet = A.id
                            WHERE A.jenis_kelamin = 'False' AND id_atlet NOT IN
                            (SELECT id_atlet_kualifikasi
                            FROM ATLET_GANDA
                            UNION
                            SELECT id_atlet_kualifikasi_2
                            FROM ATLET_GANDA)""")
    list_atlet_putra_putri = list_atlet_putri = query(f"""SELECT id_atlet FROM ATLET_KUALIFIKASI AK
                            JOIN ATLET A ON AK.id_atlet = A.id
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
            
        elif kategori['jenis_partai'] == 'WS':
            dict_kategori['jenis_partai'] = 'Tunggal Putri'
            dict_kategori["list_atlet"] = "-"
            kapasitas_partai = query(f"""SELECT COUNT(*) FROM PARTAI_PESERTA_KOMPETISI
                                WHERE jenis_partai = 'WS' AND nama_event = '{namaEvent}'
                                AND tahun_event = '{tahunEvent}'""")[0]
            dict_kategori['kapasitas'] = kapasitas_partai['count']
            
        elif kategori['jenis_partai'] == 'MD':
            dict_kategori['jenis_partai'] = 'Ganda Putra'
            dict_kategori["list_atlet"] = list_atlet_putra
            kapasitas_partai = query(f"""SELECT COUNT(*) FROM PARTAI_PESERTA_KOMPETISI
                                WHERE jenis_partai = 'MD' AND nama_event = '{namaEvent}'
                                AND tahun_event = '{tahunEvent}'""")[0]
            dict_kategori['kapasitas'] = kapasitas_partai['count']
            
        elif kategori['jenis_partai'] == 'WD':
            dict_kategori['jenis_partai'] = 'Ganda Putri'
            dict_kategori["list_atlet"] = list_atlet_putri
            kapasitas_partai = query(f"""SELECT COUNT(*) FROM PARTAI_PESERTA_KOMPETISI
                                WHERE jenis_partai = 'WD' AND nama_event = '{namaEvent}'
                                AND tahun_event = '{tahunEvent}'""")[0]
            dict_kategori['kapasitas'] = kapasitas_partai['count']
            
        else:
            dict_kategori['jenis_partai'] = 'Ganda Campuran'
            dict_kategori["list_atlet"] = list_atlet_putra_putri
            kapasitas_partai = query(f"""SELECT COUNT(*) FROM PARTAI_PESERTA_KOMPETISI
                                WHERE jenis_partai = 'XD' AND nama_event = '{namaEvent}'
                                AND tahun_event = '{tahunEvent}'""")[0]
            dict_kategori['kapasitas'] = kapasitas_partai['count']
            
        list_partai.append(dict_kategori)
        
    context = {'result':result,
               'jumlah_peserta':jumlah_peserta,
               'kapasitas_stadium': kapasitas_stadium,
               'list_partai':list_partai,}
    return render(request, 'form_partai_kompetisi.html', context)