import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

url_day = "https://raw.githubusercontent.com/markavin/Proyek_analisis_data_bike/refs/heads/main/day.csv"
url_hour = "https://raw.githubusercontent.com/markavin/Proyek_analisis_data_bike/refs/heads/main/hour.csv"
day_df_new = pd.read_csv(url_day)
hour_df_new = pd.read_csv(url_hour)

hour_df_new["dteday"] = pd.to_datetime(hour_df_new["dteday"])

hour_df_new["datetime"] = pd.to_datetime(hour_df_new["dteday"]) + pd.to_timedelta(hour_df_new["hr"], unit="h")

cat = ['season', 'yr', 'mnth', 'holiday', 'weekday', 'workingday', 'weathersit']
for cl in cat:
    hour_df_new[cl] = hour_df_new[cl].astype('category')

hour_df_new['hr'] = hour_df_new['hr'].astype('category')

hour_df_new['hr_weekend'] = hour_df_new['weekday'].isin([0, 6]).astype(int)

hour_df_new['jm_prime'] = hour_df_new["hr"].isin([8,9,10]) | hour_df_new["hr"].isin([16, 17, 18, 19]).astype(int)

st.markdown("<h1 style='text-align: center;'>Bike Sharing Dashboard</h1>", unsafe_allow_html=True)

st.sidebar.header('Filter Rentang Waktu')
start_date = st.sidebar.date_input('Tanggal Mulai', hour_df_new['datetime'].min().date())
end_date = st.sidebar.date_input('Tanggal Akhir', hour_df_new['datetime'].max().date())

st.sidebar.header('Filter Hari')
selected_days = st.sidebar.multiselect('Pilih Hari', ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'], default=['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'])
day_mapping = {'Senin': 0, 'Selasa': 1, 'Rabu': 2, 'Kamis': 3, 'Jumat': 4, 'Sabtu': 5, 'Minggu': 6}
selected_days_num = [day_mapping[day] for day in selected_days]

st.sidebar.header('Filter Pertanyaan')
question = st.sidebar.radio('Pilih Pertanyaan', 
                            ['Perbedaan penyewaan di hari kerja vs akhir pekan',
                             'Perbedaan penyewaan di jam prime time vs bukan prime time'])


filtered_df = hour_df_new[(hour_df_new['datetime'].dt.date >= start_date) & 
                          (hour_df_new['datetime'].dt.date <= end_date) &
                          (hour_df_new['weekday'].isin(selected_days_num))]


total_rentals = filtered_df['cnt'].sum()
total_casual = filtered_df['casual'].sum()  
total_registered = filtered_df['registered'].sum()

col1, col2, col3 = st.columns(3)
col1.metric("Total Penyewaan", f"{total_rentals:,}")  
col2.metric("Total Pengguna Casual", f"{total_casual:,}")
col3.metric("Total Pengguna Registered", f"{total_registered:,}") 

if question == 'Perbedaan penyewaan di hari kerja vs akhir pekan':
    st.caption("<h6 style='text-align: center;'>POLA PENYEWAAN SEPEDA SAAT HARI KERJA DAN AKHIR PEKAN</h6>", unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=filtered_df, x="hr", y="cnt", hue="hr_weekend",
                 estimator="mean", errorbar=None, palette=["#1f77b4", "#00FF00"],
                 linewidth=3, markers=True, ax=ax)
    ax.set_title("Pola Penyewaan Sepeda Saat Hari Kerja dan Akhir Pekan", fontsize=16)
    ax.set_xlabel("Jam (0-23)", fontsize=12)
    ax.set_ylabel("Rata-rata Jumlah Sewa", fontsize=12)
    ax.legend(["Hari Kerja", "Akhir Pekan"], fontsize=12, title="Tipe Hari")
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    ax.set_xticks(range(0, 24))
    st.pyplot(fig)

    st.caption("<h6 style='text-align: center;'>HIGHLIGHT PRIME TIME</h6>", unsafe_allow_html=True)
    plt.axvspan(8, 10, alpha= 0.3, color= "yellow", label="Prime Time Pagi")
    plt.axvspan(16, 19, alpha=0.3, color="yellow", label="Prime Time Sore")

    plt.annotate("PRIME TIME PAGI", xy=(9, 0.9), 
                xytext=(8.5, 0.95),
                fontsize=10, ha="center", color="green")
    plt.annotate("PRIME TIME SORE", xy=(17, 0.9), 
                xytext=(17, 0.95),
                fontsize=10, ha="center", color="green")
    plt.title("HIGHLIGHT PRIME TIME", fontsize=16)
    plt.xticks(range(0, 20))
    plt.xlim(0, 20)
    plt.ylabel("RATA-RATA JUMLAH PENYEWA", fontsize= 10)
    plt.xlabel("JAM", fontsize= 10)
    plt.tight_layout() 
    plt.savefig("haribiasa_akhirpekan.png")
    st.pyplot(fig)

    st.caption("<h6 style='text-align: center;'>HEATMAP POLA PENYEWAAN SEPEDA /JAM DALAM 1 MINGGU</h6>", unsafe_allow_html=True)
    hour_df_new["hr"] = hour_df_new["hr"].astype(int)
    hrkerja_jam_patt = hour_df_new.groupby(["weekday", "hr"], observed=False)["cnt"].mean().unstack()

    fig, ax = plt.subplots(figsize=(15, 8))
    sns.heatmap(hrkerja_jam_patt, cmap=["#FFEE99", "#99CCFF", "#A2D9A2"], annot=False, fmt=".0f", linewidths=.5, ax=ax)
    ax.set_title("HEATMAP POLA PENYEWAAN SEPEDA /JAM DALAM 1 MINGGU", fontsize=20)
    ax.set_xlabel("JAM", fontsize=14)
    ax.set_ylabel("HARI (0 = MINGGU, 6 = SABTU)", fontsize=14)
    st.pyplot(fig)

elif question == 'Perbedaan penyewaan di jam prime time vs bukan prime time':  
    st.caption("<h6 style='text-align: center;'>Perbandingan Penyewaan Sepeda: Prime Time & Bukan Prime Time</h6>", unsafe_allow_html=True)
    filtered_prime_time_df = filtered_df.groupby("jm_prime")[["casual", "registered", "cnt"]].mean().reset_index()
    filtered_prime_time_ml = pd.melt(filtered_prime_time_df, id_vars="jm_prime",
                                     value_vars=["casual", "registered", "cnt"],
                                     var_name="tipe_pengguna", value_name="count")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=filtered_prime_time_ml, x="tipe_pengguna", y="count", hue="jm_prime", 
                palette=["#FFD700", "#99CCFF"], ax=ax)
    
    for i, tipe_pengguna in enumerate(["casual", "registered", "cnt"]):
        bkn_prime_val = filtered_prime_time_df[filtered_prime_time_df["jm_prime"]==0][tipe_pengguna].values[0]
        prime_val = filtered_prime_time_df[filtered_prime_time_df["jm_prime"]==1][tipe_pengguna].values[0]
        pct_bkn = ((prime_val - bkn_prime_val) / bkn_prime_val) * 100
        ax.annotate(f"+{pct_bkn:.1f}%", xy=(i, prime_val), xytext=(0, 10), textcoords="offset points",
                    ha="center", va="bottom", color="black", fontweight="bold")
    
    ax.set_title("Perbandingan Penyewaan Sepeda: Prime Time & Bukan Prime Time", fontsize=16)
    ax.set_xlabel("Tipe Pengguna", fontsize=14)  
    ax.set_ylabel("Rata-rata Jumlah Sewa", fontsize=14)
    ax.legend(["Bukan Jam Sibuk", "Jam Sibuk"], fontsize=12)
    ax.set_xticklabels(["Casual", "Registered", "Total"])
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    st.pyplot(fig)

    st.caption("<h6 style='text-align: center;'>POLA PENYEWAAN /JAM : CASUAL VS REGISTERED</h6>", unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(14, 7))
    tipe_pengguna_jam = hour_df_new.groupby("hr")[["casual", "registered"]].mean()
    colors = sns.color_palette("husl", 2)
    tipe_pengguna_jam.plot(kind="line", linewidth=3, marker="o", color=colors, ax=ax)
    ax.set_title("POLA PENYEWAAN /JAM : CASUAL VS REGISTERED", fontsize=14)
    ax.set_xlabel("JAM", fontsize=14)
    ax.set_ylabel("RATA-RATA JUMLAH SEWA", fontsize=14)
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    ax.legend(["Casual", "Registered"], fontsize=12)
    st.pyplot(fig)

    st.caption("<h6 style='text-align: center;'>PERBANDINGAN PENYEWAAN SEPEDA : CASUAL VS REGISTERED</h6>", unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(14, 7))
    casual_data = hour_df_new.groupby("hr")["casual"].mean()
    registered_data = hour_df_new.groupby("hr")["registered"].mean()

    plt.axvspan(8, 10, alpha=0.2, color='red')  
    plt.axvspan(16, 19, alpha=0.2, color='red') 
    plt.annotate('Jam Sibuk Pagi', xy=(9, plt.ylim()[1]*0.9), xytext=(9, plt.ylim()[1]*0.95),
                fontsize=10, ha='center', color='red')
    plt.annotate('Jam Sibuk Sore', xy=(17, plt.ylim()[1]*0.9), xytext=(17, plt.ylim()[1]*0.95),
                fontsize=10, ha='center', color='red')

    plt.title("PERBANDINGAN PENYEWAAN SEPEDA : CASUAL VS REGISTERED", fontsize=18)
    plt.xlabel("JAM", fontsize=14)
    plt.ylabel("RATA-RATA SEWA SEPEDA", fontsize=14)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.legend(fontsize=12)
    st.pyplot(fig)

    
st.caption("<h6 style='text-align: center;'>Statistik Deskriptif</h6>", unsafe_allow_html=True)
st.write(filtered_df[['casual', 'registered', 'cnt']].describe())

st.caption("<h6 style='text-align: center;'>DataFrame Terfilter</h6>", unsafe_allow_html=True)
st.write(filtered_df)