from django.shortcuts import render
from utils.query import query
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def dashboard_umpire(request):
    return


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
    context = {
        "partai_kompetisi": partai_kompetisi
    }
    return render(request, "r_partai_kompetisi.html", context)