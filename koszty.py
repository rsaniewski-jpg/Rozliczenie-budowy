import os
import pathlib
from PIL import Image
import pandas as pd
import streamlit as st

# Ustalamy folder, w którym znajduje się ten plik skryptu
KATALOG_SKRYPTU = pathlib.Path(__file__).parent

sciezka_favicony = os.path.join(KATALOG_SKRYPTU, "loga", "logo.png")
sciezka_pelne_logo = os.path.join(KATALOG_SKRYPTU, "loga", "logo_pelne.png")

if os.path.exists(sciezka_favicony):
    ikonka = Image.open(sciezka_favicony)
else:
    ikonka = "🏗️"

st.set_page_config(
    page_title="Rozliczanie Kosztów Budowy", 
    page_icon=ikonka, 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- WŁASNY STYL CSS ---
st.markdown(
    """
    <style>
    div.stButton > button[kind="primary"] {
        background-color: #0066cc !important;
        color: white !important;
        border-color: #0052a3 !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #0052a3 !important;
        color: white !important;
    }
    [data-testid="stContainer"] {
        background-color: #e9ecef;
        border-radius: 8px;
        padding: 4px;
    }
    [data-testid="InputInstructions"] {
        display: none;
    }
    .block-container {
        max-width: 920px !important;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Odstępy dla nagłówków */
    h2, h3 {
        margin-top: 0.1rem !important;
        margin-bottom: -0.5rem !important;
    }
    
    /* Domyślna linia (hr) na całą szerokość (100%) */
    hr {
        width: 100% !important;
        margin-left: 0 !important;
        margin-right: auto !important;
        margin-top: 1rem !important;
        margin-bottom: 1rem !important;
    }

    /* Linie znajdujące się bezpośrednio po nagłówkach h2/h3 mają 75% szerokości od lewej */
    h2 + hr, h3 + hr {
        width: 75% !important;
        margin-left: 0 !important;
        margin-right: auto !important;
        margin-top: 0.2rem !important;
        margin-bottom: 0.2rem !important;
    }

    div.row-widget.stButton > button {
        width: 100% !important;
        padding: 0.2rem 0.4rem !important;
        font-size: 0.85rem !important;
    }

    @media (max-width: 768px) {
        .block-container {
            max-width: 100% !important;
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
        }
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.3rem !important; }
        h3 { font-size: 1.1rem !important; }
    }
    </style>
""",
    unsafe_allow_html=True,
)

PLIK_BAZY = os.path.join(KATALOG_SKRYPTU, "baza_danych.csv")
PLIK_PRACOWNICY = os.path.join(KATALOG_SKRYPTU, "baza_pracownikow.csv")
PLIK_STAWKI = os.path.join(KATALOG_SKRYPTU, "baza_stawek.csv")
PLIK_BUDOWY = os.path.join(KATALOG_SKRYPTU, "baza_budow.csv")
PLIK_AUTA = os.path.join(KATALOG_SKRYPTU, "baza_aut.csv")


def wczytaj_pracownikow():
    if os.path.exists(PLIK_PRACOWNICY):
        df = pd.read_csv(PLIK_PRACOWNICY, dtype=str)
        if "Pin" in df.columns and "Email" not in df.columns:
            df["Email"] = df["Pracownik"].str.lower().str.replace(" ", "") + "@firma.pl"
            df = df.rename(columns={"Pin": "Haslo"})
        if "Email" not in df.columns:
            df["Email"] = ""
        if "Haslo" not in df.columns:
            df["Haslo"] = "1234"
        if "Rola" not in df.columns:
            df["Rola"] = "Pracownik"
        
        df.loc[(df["Email"] == "admin@firma.pl") | (df["Pracownik"] == "Admin"), "Rola"] = "Admin"
        df.to_csv(PLIK_PRACOWNICY, index=False)
        return df
    else:
        df_domyslne = pd.DataFrame(
            {
                "Email": ["jan.kowalski@firma.pl", "adam.nowak@firma.pl", "admin@firma.pl"],
                "Haslo": ["1234", "5678", "0000"],
                "Pracownik": ["Jan Kowalski", "Adam Nowak", "Admin"],
                "Rola": ["Pracownik", "Pracownik", "Admin"],
            }
        )
        df_domyslne.to_csv(PLIK_PRACOWNICY, index=False)
        return df_domyslne


def zapisz_pracownikow(df):
    df.to_csv(PLIK_PRACOWNICY, index=False)


def wczytaj_auta():
    if os.path.exists(PLIK_AUTA):
        df = pd.read_csv(PLIK_AUTA, dtype=str)
        if "Nr Rejestracyjny" in df.columns:
            auta = df["Nr Rejestracyjny"].dropna().unique().tolist()
            if auta:
                return auta
    domyslne_auta = ["DW 12345", "WA 67890", "PO 11223"]
    pd.DataFrame({"Nr Rejestracyjny": domyslne_auta, "Opis": ["Autobus firmowy", "Skrzyniowy", "Osobowy"]}).to_csv(PLIK_AUTA, index=False)
    return domyslne_auta


def wczytaj_pelne_dane_aut():
    if os.path.exists(PLIK_AUTA):
        return pd.read_csv(PLIK_AUTA, dtype=str)
    return pd.DataFrame(columns=["Nr Rejestracyjny", "Opis"])


def zapisz_auto(nr_rej, opis):
    df = wczytaj_pelne_dane_aut()
    if nr_rej not in df["Nr Rejestracyjny"].values:
        nowy = pd.DataFrame({"Nr Rejestracyjny": [nr_rej], "Opis": [opis]})
        df = pd.concat([df, nowy], ignore_index=True)
        df.to_csv(PLIK_AUTA, index=False)
        return True
    return False


def usun_auto(nr_rej):
    df = wczytaj_pelne_dane_aut()
    if nr_rej in df["Nr Rejestracyjny"].values:
        df = df[df["Nr Rejestracyjny"] != nr_rej]
        df.to_csv(PLIK_AUTA, index=False)
        return True
    return False


def wczytaj_stawki():
    if os.path.exists(PLIK_STAWKI):
        try:
            df = pd.read_csv(PLIK_STAWKI)
            if (
                "Pracownik" not in df.columns
                or "Stawka" not in df.columns
                or "DataOd" not in df.columns
            ):
                raise ValueError("Niepoprawna struktura")
            return df
        except Exception:
            pass

    df_stawki_start = pd.DataFrame(
        {
            "Pracownik": ["Jan Kowalski", "Adam Nowak", "Admin"],
            "Stawka": [30.0, 35.0, 50.0],
            "DataOd": ["2024-01-01", "2024-01-01", "2024-01-01"],
        }
    )
    df_stawki_start.to_csv(PLIK_STAWKI, index=False)
    return df_stawki_start


def zapisz_stawki(df):
    df.to_csv(PLIK_STAWKI, index=False)


def dodaj_stawke_dla_pracownika(pracownik, stawka, data_od):
    df_s = wczytaj_stawki()
    nowy_wiersz = pd.DataFrame(
        {
            "Pracownik": [pracownik],
            "Stawka": [float(stawka)],
            "DataOd": [str(data_od)],
        }
    )
    df_s = pd.concat([df_s, nowy_wiersz], ignore_index=True)
    df_s = df_s.sort_values(by="DataOd", ascending=True)
    zapisz_stawki(df_s)


def pobierz_stawke_pracownika(nazwa_pracownika, data_wpisu):
    df_s = wczytaj_stawki()
    if df_s.empty:
        return 30.0

    p_stawki = df_s[df_s["Pracownik"] == nazwa_pracownika]
    if p_stawki.empty:
        return 30.0

    if data_wpisu is None:
        return float(p_stawki.iloc[-1]["Stawka"])

    data_wpisu_dt = pd.to_datetime(data_wpisu)
    p_stawki["DataOd_dt"] = pd.to_datetime(p_stawki["DataOd"])
    aktywne = p_stawki[p_stawki["DataOd_dt"] <= data_wpisu_dt]

    if aktywne.empty:
        return float(p_stawki.iloc[0]["Stawka"])

    return float(aktywne.iloc[-1]["Stawka"])


def wczytaj_budowy():
    if os.path.exists(PLIK_BUDOWY):
        df = pd.read_csv(PLIK_BUDOWY, dtype=str)
        if "Budowa" in df.columns:
            budowy = df["Budowa"].dropna().unique().tolist()
            if budowy:
                return budowy
    domyslne = [
        "Budowa ul. Słoneczna 5",
        "Osiedle Parkowe - Blok A",
        "Remont Biurowca Centrum",
    ]
    pd.DataFrame({"Budowa": domyslne}).to_csv(PLIK_BUDOWY, index=False)
    return domyslne


def zapisz_budowe(nowa_nazwa):
    budowy = wczytaj_budowy()
    if nowa_nazwa not in budowy:
        budowy.append(nowa_nazwa)
        pd.DataFrame({"Budowa": budowy}).to_csv(PLIK_BUDOWY, index=False)
        return True
    return False


def usun_budowe(nazwa_do_usuniecia):
    budowy = wczytaj_budowy()
    if nazwa_do_usuniecia in budowy:
        budowy.remove(nazwa_do_usuniecia)
        pd.DataFrame({"Budowa": budowy}).to_csv(PLIK_BUDOWY, index=False)
        return True
    return False


def wczytaj_dane():
    if os.path.exists(PLIK_BAZY):
        df = pd.read_csv(PLIK_BAZY)
        kolumny_wymagane = {
            "Powrót Od": "00:00",
            "Powrót Do": "00:00",
            "Czas powrotu (godz)": 0.0,
            "Koszt powrotu (zł)": 0.0,
            "Nr Rejestracyjny": "Brak",
            "Nr Rejestracyjny Powrót": "Brak"
        }
        for kol, domyslna_wartosc in kolumny_wymagane.items():
            if kol not in df.columns:
                df[kol] = domyslna_wartosc
        return df
    else:
        return pd.DataFrame(
            columns=[
                "Pracownik",
                "Data",
                "Budowa",
                "Nr Rejestracyjny",
                "Dojazd Od",
                "Dojazd Do",
                "Czas dojazdu (godz)",
                "Od",
                "Do",
                "Stawka (zł/h)",
                "Godziny",
                "Koszt pracy (zł)",
                "Koszt dojazdu (zł)",
                "Powrót Od",
                "Powrót Do",
                "Czas powrotu (godz)",
                "Nr Rejestracyjny Powrót",
                "Koszt powrotu (zł)",
                "Razem (zł)",
            ]
        )


def zapisz_dane(df):
    df.to_csv(PLIK_BAZY, index=False)


def sprawdz_konflikt_czasowy(df_dane, pracownik, data_str, d_od_dt, d_do_dt, p_od_dt, p_do_dt, pow_od_dt, pow_do_dt, czy_dojazd, czy_powrot):
    if df_dane.empty:
        return False

    istniejace = df_dane[
        (df_dane["Pracownik"] == pracownik) & (df_dane["Data"] == data_str)
    ]

    if istniejace.empty:
        return False

    def przedzialy_sie_nakladaja(s1, e1, s2, e2):
        if s1 == e1 or s2 == e2:
            return False
        return max(s1, s2) < min(e1, e2)

    for _, row in istniejace.iterrows():
        i_d_od = pd.to_datetime(f"{data_str} {row['Dojazd Od']}")
        i_d_do = pd.to_datetime(f"{data_str} {row['Dojazd Do']}")
        i_p_od = pd.to_datetime(f"{data_str} {row['Od']}")
        i_p_do = pd.to_datetime(f"{data_str} {row['Do']}")
        
        pow_od_val = row.get("Powrót Od", "00:00")
        pow_do_val = row.get("Powrót Do", "00:00")
        if pd.isna(pow_od_val) or pow_od_val == "": pow_od_val = "00:00"
        if pd.isna(pow_do_val) or pow_do_val == "": pow_do_val = "00:00"

        i_pow_od = pd.to_datetime(f"{data_str} {pow_od_val}")
        i_pow_do = pd.to_datetime(f"{data_str} {pow_do_val}")

        istniejace_okresy = [
            (i_d_od, i_d_do),
            (i_p_od, i_p_do),
            (i_pow_od, i_pow_do)
        ]

        nowe_okresy = [(p_od_dt, p_do_dt)]
        if czy_dojazd:
            nowe_okresy.append((d_od_dt, d_do_dt))
        if czy_powrot:
            nowe_okresy.append((pow_od_dt, pow_do_dt))

        for n_s, n_e in nowe_okresy:
            for i_s, i_e in istniejace_okresy:
                if przedzialy_sie_nakladaja(n_s, n_e, i_s, i_e):
                    return True

    return False


def sprawdz_konflikt_pojazdu_dojazd(df_dane, auto, data_str, d_od_dt, d_do_dt, czy_dojazd):
    if df_dane.empty or not czy_dojazd or auto == "Brak" or pd.isna(auto):
        return False

    def przedzialy_sie_nakladaja(s1, e1, s2, e2):
        if s1 == e1 or s2 == e2:
            return False
        return max(s1, s2) < min(e1, e2)

    for _, row in df_dane[df_dane["Data"] == data_str].iterrows():
        auta_wiersza = [row.get("Nr Rejestracyjny", "Brak"), row.get("Nr Rejestracyjny Powrót", "Brak")]
        if auto in auta_wiersza:
            i_d_od = pd.to_datetime(f"{data_str} {row['Dojazd Od']}")
            i_d_do = pd.to_datetime(f"{data_str} {row['Dojazd Do']}")
            i_p_od = pd.to_datetime(f"{data_str} {row['Od']}")
            i_p_do = pd.to_datetime(f"{data_str} {row['Do']}")
            
            pow_od_val = row.get("Powrót Od", "00:00")
            pow_do_val = row.get("Powrót Do", "00:00")
            if pd.isna(pow_od_val) or pow_od_val == "": pow_od_val = "00:00"
            if pd.isna(pow_do_val) or pow_do_val == "": pow_do_val = "00:00"
            i_pow_od = pd.to_datetime(f"{data_str} {pow_od_val}")
            i_pow_do = pd.to_datetime(f"{data_str} {pow_do_val}")

            if przedzialy_sie_nakladaja(d_od_dt, d_do_dt, i_d_od, i_d_do) or \
               przedzialy_sie_nakladaja(d_od_dt, d_do_dt, i_p_od, i_p_do) or \
               przedzialy_sie_nakladaja(d_od_dt, d_do_dt, i_pow_od, i_pow_do):
                return True
    return False


def sprawdz_konflikt_pojazdu_powrot(df_dane, auto, data_str, pow_od_dt, pow_do_dt, czy_powrot):
    if df_dane.empty or not czy_powrot or auto == "Brak" or pd.isna(auto):
        return False

    def przedzialy_sie_nakladaja(s1, e1, s2, e2):
        if s1 == e1 or s2 == e2:
            return False
        return max(s1, s2) < min(e1, e2)

    for _, row in df_dane[df_dane["Data"] == data_str].iterrows():
        auta_wiersza = [row.get("Nr Rejestracyjny", "Brak"), row.get("Nr Rejestracyjny Powrót", "Brak")]
        if auto in auta_wiersza:
            i_d_od = pd.to_datetime(f"{data_str} {row['Dojazd Od']}")
            i_d_do = pd.to_datetime(f"{data_str} {row['Dojazd Do']}")
            i_p_od = pd.to_datetime(f"{data_str} {row['Od']}")
            i_p_do = pd.to_datetime(f"{data_str} {row['Do']}")
            
            pow_od_val = row.get("Powrót Od", "00:00")
            pow_do_val = row.get("Powrót Do", "00:00")
            if pd.isna(pow_od_val) or pow_od_val == "": pow_od_val = "00:00"
            if pd.isna(pow_do_val) or pow_do_val == "": pow_do_val = "00:00"
            i_pow_od = pd.to_datetime(f"{data_str} {pow_od_val}")
            i_pow_do = pd.to_datetime(f"{data_str} {pow_do_val}")

            if przedzialy_sie_nakladaja(pow_od_dt, pow_do_dt, i_d_od, i_d_do) or \
               przedzialy_sie_nakladaja(pow_od_dt, pow_do_dt, i_p_od, i_p_do) or \
               przedzialy_sie_nakladaja(pow_od_dt, pow_do_dt, i_pow_od, i_pow_do):
                return True
    return False


if "zalogowany" not in st.session_state:
    st.session_state.zalogowany = False
    st.session_state.aktualny_pracownik = None
    st.session_state.rola = None

st.title("🏗️ System Rozliczania Czasu Pracy na Budowach")

if os.path.exists(sciezka_pelne_logo):
    st.sidebar.image(sciezka_pelne_logo, use_container_width=True)
    st.sidebar.markdown("---")

if not st.session_state.zalogowany:
    st.sidebar.header("🔐 Logowanie")
    
    with st.sidebar.form("form_logowania"):
        email_input = st.text_input("Adres e-mail")
        haslo_input = st.text_input("Hasło", type="password")
        submit_logowanie = st.form_submit_button("Zaloguj się")

    if submit_logowanie:
        df_pracownicy = wczytaj_pracownikow()
        pasujacy = df_pracownicy[
            (df_pracownicy["Email"].str.lower() == email_input.strip().lower()) & 
            (df_pracownicy["Haslo"] == haslo_input)
        ]

        if not pasujacy.empty:
            st.session_state.zalogowany = True
            st.session_state.aktualny_pracownik = pasujacy.iloc[0]["Pracownik"]
            st.session_state.rola = str(pasujacy.iloc[0]["Rola"]).strip()
            st.rerun()
        else:
            st.sidebar.error("❌ Błędny e-mail lub hasło!")

    st.info(
        "👈 Rozwiń menu boczne (ikona strzałki/menu w lewym górnym rogu), aby wpisać swój adres e-mail oraz hasło."
    )
    st.stop()

zalogowany_pracownik = st.session_state.aktualny_pracownik
rola_uzytkownika = str(st.session_state.rola).strip()

st.sidebar.success(
    f"Zalogowano jako: **{zalogowany_pracownik}**\n\nRola: **{rola_uzytkownika}**"
)

if st.sidebar.button("Wyloguj się"):
    st.session_state.zalogowany = False
    st.session_state.aktualny_pracownik = None
    st.session_state.rola = None
    st.rerun()

dane_systemowe = wczytaj_dane()
lista_budow = wczytaj_budowy()
lista_aut = wczytaj_auta()


# --- PANEL ADMINISTRATORA ---
if rola_uzytkownika == "Admin":
    st.subheader("👑 Panel Administratora")

    if "menu_admin" not in st.session_state:
        st.session_state.menu_admin = "📊 Raport wszystkich wpisów"

    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)

    with col_btn1:
        if st.button("📊 Raport", use_container_width=True, type="primary" if st.session_state.menu_admin == "📊 Raport wszystkich wpisów" else "secondary"):
            st.session_state.menu_admin = "📊 Raport wszystkich wpisów"
            st.rerun()

    with col_btn2:
        if st.button("👥 Pracownicy", use_container_width=True, type="primary" if st.session_state.menu_admin == "👥 Zarządzanie Pracownikami" else "secondary"):
            st.session_state.menu_admin = "👥 Zarządzanie Pracownikami"
            st.rerun()

    with col_btn3:
        if st.button("🏗️ Budowy", use_container_width=True, type="primary" if st.session_state.menu_admin == "🏗️ Zarządzanie Budowami" else "secondary"):
            st.session_state.menu_admin = "🏗️ Zarządzanie Budowami"
            st.rerun()

    with col_btn4:
        if st.button("🚗 Auta", use_container_width=True, type="primary" if st.session_state.menu_admin == "🚗 Zarządzanie Autami" else "secondary"):
            st.session_state.menu_admin = "🚗 Zarządzanie Autami"
            st.rerun()

    st.markdown("---")

    menu_admin = st.session_state.menu_admin

    if menu_admin == "📊 Raport wszystkich wpisów":
        st.markdown("### Raport godzin i kosztów całej firmy")

        with st.expander("➕ Dopisz godziny dla pracownika (kliknij, aby rozwinąć)"):
            df_pracownicy_adm = wczytaj_pracownikow()
            lista_pracownikow_nazwy = df_pracownicy_adm["Pracownik"].tolist()

            if not lista_pracownikow_nazwy:
                st.error("Brak pracowników w systemie.")
            elif not lista_budow:
                st.error("Brak dostępnych budów w systemie.")
            else:
                wybrany_pracownik_adm = st.selectbox("Wybierz pracownika", lista_pracownikow_nazwy, key="adm_p_sel")
                data_adm = st.date_input("Data wpisu", value=pd.Timestamp.today().date(), key="adm_d_date")
                budowa_adm = st.selectbox("Wybierz budowę", lista_budow, key="adm_b_sel")

                st.markdown("⏱️ **Czas pracy na budowie** (obowiązkowy)")
                col_pa1, col_pa2 = st.columns(2)
                with col_pa1:
                    godzina_od_adm = st.time_input("Godzina od", value=pd.to_datetime("08:00").time(), key="adm_t_od")
                with col_pa2:
                    godzina_do_adm = st.time_input("Godzina do", value=pd.to_datetime("16:00").time(), key="adm_t_do")

                czy_dojazd_adm = st.checkbox("🚗 Zgłoś dojazd firmowym autem", key="adm_chk_dojazd_dyn")
                dojazd_od_adm, dojazd_do_adm = pd.to_datetime("07:00").time(), pd.to_datetime("08:00").time()
                auto_dojazd_adm = "Brak"
                if czy_dojazd_adm:
                    col_da1, col_da2 = st.columns(2)
                    with col_da1:
                        dojazd_od_adm = st.time_input("Dojazd od", value=pd.to_datetime("07:00").time(), key="adm_doj_od")
                    with col_da2:
                        dojazd_do_adm = st.time_input("Dojazd do", value=pd.to_datetime("08:00").time(), key="adm_doj_do")
                    auto_dojazd_adm = st.selectbox("Auto na dojazd", lista_aut if lista_aut else ["Brak"], key="adm_auta_d")

                czy_powrot_adm = st.checkbox("🏠 Zgłoś powrót firmowym autem", key="adm_chk_powrot_dyn")
                powrot_od_adm, powrot_do_adm = pd.to_datetime("16:00").time(), pd.to_datetime("17:00").time()
                auto_powrot_adm = "Brak"
                if czy_powrot_adm:
                    col_powa1, col_powa2 = st.columns(2)
                    with col_powa1:
                        powrot_od_adm = st.time_input("Powrót od", value=pd.to_datetime("16:00").time(), key="adm_pow_od")
                    with col_powa2:
                        powrot_do_adm = st.time_input("Powrót do", value=pd.to_datetime("17:00").time(), key="adm_pow_do")
                    auto_powrot_adm = st.selectbox("Auto na powrót", lista_aut if lista_aut else ["Brak"], key="adm_auta_p")

                if st.button("💾 Dodaj ten wpis dla pracownika", use_container_width=True, type="primary", key="btn_save_adm"):
                    start_dt = pd.to_datetime(f"{data_adm} {godzina_od_adm}")
                    koniec_dt = pd.to_datetime(f"{data_adm} {godzina_do_adm}")
                    
                    dojazd_start_dt = pd.to_datetime(f"{data_adm} {dojazd_od_adm}") if czy_dojazd_adm else start_dt
                    dojazd_koniec_dt = pd.to_datetime(f"{data_adm} {dojazd_do_adm}") if czy_dojazd_adm else start_dt
                    
                    powrot_start_dt = pd.to_datetime(f"{data_adm} {powrot_od_adm}") if czy_powrot_adm else koniec_dt
                    powrot_koniec_dt = pd.to_datetime(f"{data_adm} {powrot_do_adm}") if czy_powrot_adm else koniec_dt

                    if koniec_dt <= start_dt:
                        st.error("Błąd: Godzina zakończenia pracy musi być późniejsza niż rozpoczęcia!")
                    elif czy_dojazd_adm and dojazd_koniec_dt < dojazd_start_dt:
                        st.error("Błąd: Godzina zakończenia dojazdu musi być późniejsza lub równa rozpoczęciu!")
                    elif czy_dojazd_adm and auto_dojazd_adm == "Brak":
                        st.error("Błąd: Wybierz auto na dojazd!")
                    elif czy_powrot_adm and powrot_koniec_dt < powrot_start_dt:
                        st.error("Błąd: Godzina zakończenia powrotu musi być późniejsza lub równa rozpoczęciu!")
                    elif czy_powrot_adm and auto_powrot_adm == "Brak":
                        st.error("Błąd: Wybierz auto na powrót!")
                    else:
                        AktualneDane = wczytaj_dane()
                        konflikt_pracownika = sprawdz_konflikt_czasowy(
                            AktualneDane, wybrany_pracownik_adm, str(data_adm), 
                            dojazd_start_dt, dojazd_koniec_dt, start_dt, koniec_dt,
                            powrot_start_dt, powrot_koniec_dt, czy_dojazd_adm, czy_powrot_adm
                        )
                        konflikt_auta_d = sprawdz_konflikt_pojazdu_dojazd(
                            AktualneDane, auto_dojazd_adm, str(data_adm), dojazd_start_dt, dojazd_koniec_dt, czy_dojazd_adm
                        )
                        konflikt_auta_p = sprawdz_konflikt_pojazdu_powrot(
                            AktualneDane, auto_powrot_adm, str(data_adm), powrot_start_dt, powrot_koniec_dt, czy_powrot_adm
                        )

                        if konflikt_pracownika:
                            st.error(f"❌ Wybrane godziny kolidują z innym wpisem pracownika w tym dniu!")
                        elif konflikt_auta_d:
                            st.error(f"❌ Pojazd dojazdu ({auto_dojazd_adm}) jest zajęty w tym przedziale czasowym!")
                        elif konflikt_auta_p:
                            st.error(f"❌ Pojazd powrotu ({auto_powrot_adm}) jest zajęty w tym przedziale czasowym!")
                        else:
                            roznica_czasu = (koniec_dt - start_dt).total_seconds() / 3600
                            roznica_dojazdu = (dojazd_koniec_dt - dojazd_start_dt).total_seconds() / 3600 if czy_dojazd_adm else 0.0
                            roznica_powrotu = (powrot_koniec_dt - powrot_start_dt).total_seconds() / 3600 if czy_powrot_adm else 0.0

                            stawka_wybranego = pobierz_stawke_pracownika(wybrany_pracownik_adm, str(data_adm))

                            koszt_pracy = roznica_czasu * stawka_wybranego
                            stawka_dojazdu = stawka_wybranego / 2.0
                            koszt_dojazdu_zl = roznica_dojazdu * stawka_dojazdu if czy_dojazd_adm else 0.0
                            koszt_powrotu_zl = roznica_powrotu * stawka_dojazdu if czy_powrot_adm else 0.0
                            razem = koszt_pracy + koszt_dojazdu_zl + koszt_powrotu_zl

                            nowy_wpis_adm = {
                                "Pracownik": wybrany_pracownik_adm,
                                "Data": str(data_adm),
                                "Budowa": budowa_adm,
                                "Nr Rejestracyjny": auto_dojazd_adm if czy_dojazd_adm else "Brak",
                                "Dojazd Od": str(dojazd_od_adm) if czy_dojazd_adm else "00:00",
                                "Dojazd Do": str(dojazd_do_adm) if czy_dojazd_adm else "00:00",
                                "Czas dojazdu (godz)": round(roznica_dojazdu, 2),
                                "Od": str(godzina_od_adm),
                                "Do": str(godzina_do_adm),
                                "Stawka (zł/h)": stawka_wybranego,
                                "Godziny": round(roznica_czasu, 2),
                                "Koszt pracy (zł)": round(koszt_pracy, 2),
                                "Koszt dojazdu (zł)": round(koszt_dojazdu_zl, 2),
                                "Powrót Od": str(powrot_od_adm) if czy_powrot_adm else "00:00",
                                "Powrót Do": str(powrot_do_adm) if czy_powrot_adm else "00:00",
                                "Czas powrotu (godz)": round(roznica_powrotu, 2),
                                "Nr Rejestracyjny Powrót": auto_powrot_adm if czy_powrot_adm else "Brak",
                                "Koszt powrotu (zł)": round(koszt_powrotu_zl, 2),
                                "Razem (zł)": round(razem, 2),
                            }

                            AktualneDane = pd.concat([AktualneDane, pd.DataFrame([nowy_wpis_adm])], ignore_index=True)
                            zapisz_dane(AktualneDane)
                            st.success(f"✅ Pomyślnie dopisano godziny dla pracownika: **{wybrany_pracownik_adm}**")
                            st.rerun()

        st.markdown("---")

        dane_systemowe = wczytaj_dane()
        if not dane_systemowe.empty:
            mc_a1, mc_a2, mc_a3 = st.columns(3)
            mc_a1.metric("Łączne godziny", f"{dane_systemowe['Godziny'].sum():.2f} h")
            mc_a2.metric("Koszt pracy", f"{dane_systemowe['Koszt pracy (zł)'].sum():.2f} zł")
            mc_a3.metric("Koszt dojazdu", f"{dane_systemowe['Koszt dojazdu (zł)'].sum():.2f} zł")
            
            mc_a4, mc_a5 = st.columns(2)
            mc_a4.metric("Koszt powrotu", f"{dane_systemowe['Koszt powrotu (zł)'].sum():.2f} zł")
            mc_a5.metric("Łączny koszt", f"{dane_systemowe['Razem (zł)'].sum():.2f} zł")
            
            st.markdown("---")
            st.dataframe(dane_systemowe, use_container_width=True)

            from io import BytesIO

            def convert_df_to_excel_z_tabela(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False, sheet_name="Wszystkie_Wpisy")
                    if not df.empty and "Budowa" in df.columns and "Pracownik" in df.columns:
                        tabela_kosztow = df.pivot_table(
                            values="Koszt pracy (zł)", 
                            index="Budowa", 
                            columns="Pracownik", 
                            aggfunc="sum", 
                            fill_value=0.0
                        )
                        tabela_kosztow.to_excel(writer, sheet_name="Podsumowanie_Kosztow")
                return output.getvalue()

            excel_data = convert_df_to_excel_z_tabela(dane_systemowe)
            st.download_button(
                label="📥 Pobierz zaawansowany raport Excel (.xlsx)",
                data=excel_data,
                file_name="raport_podsumowanie_budow.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        else:
            st.warning("Brak jakichkolwiek wpisów w systemie.")

    elif menu_admin == "👥 Zarządzanie Pracownikami":
        st.markdown("### Dodaj nowego pracownika")
        df_pracownicy = wczytaj_pracownikow()

        with st.form("form_dodaj_pracownika", clear_on_submit=True):
            c_n1, c_n2 = st.columns(2)
            with c_n1:
                nowe_imie = st.text_input("Imię i nazwisko pracownika")
                nowy_email = st.text_input("Adres e-mail (login)")
                nowe_haslo = st.text_input("Hasło do logowania", type="password")
            with c_n2:
                wybrana_rola = st.selectbox("Uprawnienia", ["Pracownik", "Admin"])
                poczatkowa_stawka = st.number_input("Stawka początkowa (zł/h)", min_value=0.0, value=30.0, step=5.0)
                data_od_stawki = st.date_input("Obowiązuje od daty", value=pd.Timestamp.today().date())

            submit_pracownik = st.form_submit_button("Dodaj pracownika")

            if submit_pracownik:
                if not nowe_imie or not nowy_email or not nowe_haslo:
                    st.warning("Uzupełnij imię, e-mail oraz hasło.")
                elif nowy_email.lower() in df_pracownicy["Email"].str.lower().values:
                    st.error("❌ Ten adres e-mail jest już zajęty przez innego pracownika!")
                else:
                    nowy_wiersz = pd.DataFrame(
                        {
                            "Email": [nowy_email.strip().lower()],
                            "Haslo": [nowe_haslo],
                            "Pracownik": [nowe_imie],
                            "Rola": [wybrana_rola],
                        }
                    )
                    df_pracownicy = pd.concat([df_pracownicy, nowy_wiersz], ignore_index=True)
                    zapisz_pracownikow(df_pracownicy)
                    dodaj_stawke_dla_pracownika(nowe_imie, poczatkowa_stawka, data_od_stawki)
                    st.success(f"✅ Pomyślnie dodano pracownika: {nowe_imie}")
                    st.rerun()

        st.markdown("---")
        st.markdown("### 📋 Lista pracowników")
        df_pracownicy = wczytaj_pracownikow()

        if "edytowany_pracownik" not in st.session_state:
            st.session_state.edytowany_pracownik = None

        if not df_pracownicy.empty:
            for idx, row in df_pracownicy.iterrows():
                p_imie = row["Pracownik"]
                p_email = row.get("Email", "Brak")
                p_rola = row.get("Rola", "Pracownik")
                aktualna_s = pobierz_stawke_pracownika(p_imie, None)

                with st.container(border=True):
                    col_info, col_przyciski = st.columns([7.0, 3.0])
                    with col_info:
                        st.write(f"👤 **{p_imie}** (`{p_email}`) \n Rola: `{p_rola}` | Stawka: `{aktualna_s} zł/h`")
                    with col_przyciski:
                        sub_c1, sub_c2 = st.columns(2)
                        with sub_c1:
                            if st.button("✏️", key=f"edit_p_{idx}", help="Edytuj", use_container_width=True):
                                st.session_state.edytowany_pracownik = p_imie
                                st.rerun()
                        with sub_c2:
                            if st.button("🗑️", key=f"del_p_{idx}", help="Usuń", use_container_width=True):
                                if p_imie == zalogowany_pracownik:
                                    st.error("Nie możesz usunąć samego siebie!")
                                else:
                                    df_pracownicy = df_pracownicy[df_pracownicy["Pracownik"] != p_imie]
                                    zapisz_pracownikow(df_pracownicy)
                                    st.success(f"Usunięto pracownika: {p_imie}")
                                    st.rerun()

            if st.session_state.edytowany_pracownik:
                cel = st.session_state.edytowany_pracownik
                dane_celu = df_pracownicy[df_pracownicy["Pracownik"] == cel]

                if not dane_celu.empty:
                    akt_wiersz = dane_celu.iloc[0]
                    st.markdown("---")
                    st.markdown(f"### ✏️ Edycja profilu pracownika: **{cel}**")

                    with st.form(f"form_edycja_{cel}"):
                        nowe_imie_ed = st.text_input("Imię i nazwisko", value=akt_wiersz["Pracownik"])
                        nowy_email_ed = st.text_input("Adres e-mail", value=akt_wiersz.get("Email", ""))
                        nowe_haslo_ed = st.text_input("Hasło", value=akt_wiersz.get("Haslo", ""), type="password")
                        idx_r = 0 if str(akt_wiersz["Rola"]) == "Pracownik" else 1
                        nowa_rola_ed = st.selectbox("Uprawnienia", ["Pracownik", "Admin"], index=idx_r)

                        st.markdown("---")
                        st.markdown("💰 **Nowa stawka godzinowa**")
                        ostatnia_s = pobierz_stawke_pracownika(cel, None)
                        nowa_stawka_ed = st.number_input("Stawka (zł/h)", min_value=0.0, value=ostatnia_s, step=5.0)
                        data_od_nowej = st.date_input("Obowiązuje od daty", value=pd.Timestamp.today().date())

                        col_zapisz, col_anuluj = st.columns(2)
                        with col_zapisz:
                            btn_zapisz_zmiany = st.form_submit_button("💾 Zapisz zmiany", use_container_width=True)
                        with col_anuluj:
                            btn_anuluj = st.form_submit_button("❌ Anuluj", use_container_width=True)

                        if btn_zapisz_zmiany:
                            df_pracownicy.loc[df_pracownicy["Pracownik"] == cel, "Pracownik"] = nowe_imie_ed
                            df_pracownicy.loc[df_pracownicy["Pracownik"] == nowe_imie_ed, "Email"] = nowy_email_ed.strip().lower()
                            df_pracownicy.loc[df_pracownicy["Pracownik"] == nowe_imie_ed, "Haslo"] = nowe_haslo_ed
                            df_pracownicy.loc[df_pracownicy["Pracownik"] == nowe_imie_ed, "Rola"] = nowa_rola_ed
                            zapisz_pracownikow(df_pracownicy)

                            if nowa_stawka_ed != ostatnia_s:
                                dodaj_stawke_dla_pracownika(nowe_imie_ed, nowa_stawka_ed, data_od_nowej)

                            st.session_state.edytowany_pracownik = None
                            st.success("Zaktualizowano pomyślnie!")
                            st.rerun()

                        if btn_anuluj:
                            st.session_state.edytowany_pracownik = None
                            st.rerun()
        else:
            st.info("Brak pracowników w systemie.")

    elif menu_admin == "🏗️ Zarządzanie Budowami":
        st.markdown("### Dodaj nową budowę / lokalizację")
        nowa_budowa_input = st.text_input("Nazwa budowy lub adres", key="input_nowa_budowa")

        if st.button("➕ Dodaj budowę do listy", use_container_width=True):
            czysta_nazwa = nowa_budowa_input.strip()
            if not czysta_nazwa:
                st.warning("⚠️ Podaj nazwę budowy.")
            else:
                sukces = zapisz_budowe(czysta_nazwa)
                if sukces:
                    st.success(f"✅ Dodano nową budowę: {czysta_nazwa}")
                    st.rerun()
                else:
                    st.error("❌ Taka budowa już istnieje na liście.")

        st.markdown("---")
        st.markdown("### Aktualnie aktywne budowy")
        aktualne_b = wczytaj_budowy()

        if "edytowana_budowa" not in st.session_state:
            st.session_state.edytowana_budowa = None

        if aktualne_b:
            for b in aktualne_b:
                with st.container(border=True):
                    col_info_b, col_przyciski_b = st.columns([7.0, 3.0])
                    with col_info_b:
                        st.markdown(f"<b>{b}</b>", unsafe_allow_html=True)
                    with col_przyciski_b:
                        sub_cb1, sub_cb2 = st.columns(2)
                        with sub_cb1:
                            if st.button("✏️", key=f"edit_b_{b}", help="Edytuj", use_container_width=True):
                                st.session_state.edytowana_budowa = b
                                st.rerun()
                        with sub_cb2:
                            if st.button("🗑️", key=f"del_{b}", help="Usuń", use_container_width=True):
                                usun_budowe(b)
                                st.success(f"Usunięto budowę: {b}")
                                st.rerun()

            if st.session_state.edytowana_budowa:
                st.markdown("---")
                st.markdown(f"### ✏️ Edycja budowy: **{st.session_state.edytowana_budowa}**")
                
                with st.form("form_edycja_budowy"):
                    nowa_nazwa_b = st.text_input("Nowa nazwa budowy / adresu", value=st.session_state.edytowana_budowa)
                    
                    c_zapisz, c_anuluj = st.columns(2)
                    with c_zapisz:
                        btn_zapisz_b = st.form_submit_button("💾 Zapisz", use_container_width=True)
                    with c_anuluj:
                        btn_anuluj_b = st.form_submit_button("❌ Anuluj", use_container_width=True)

                    if btn_zapisz_b:
                        stara_nazwa = st.session_state.edytowana_budowa
                        czysta_nowa = nowa_nazwa_b.strip()

                        if not czysta_nowa:
                            st.warning("Nazwa budowy nie może być pusta!")
                        elif czysta_nowa in aktualne_b:
                            st.error("Budowa o takiej nazwie już istnieje!")
                        else:
                            idx = aktualne_b.index(stara_nazwa)
                            aktualne_b[idx] = czysta_nowa
                            pd.DataFrame({"Budowa": aktualne_b}).to_csv(PLIK_BUDOWY, index=False)

                            df_dane = wczytaj_dane()
                            if not df_dane.empty and "Budowa" in df_dane.columns:
                                df_dane.loc[df_dane["Budowa"] == stara_nazwa, "Budowa"] = czysta_nowa
                                zapisz_dane(df_dane)

                            st.session_state.edytowana_budowa = None
                            st.success("✅ Zaktualizowano nazwę budowy pomyślnie!")
                            st.rerun()

                    if btn_anuluj_b:
                        st.session_state.edytowana_budowa = None
                        st.rerun()
        else:
            st.info("Brak aktywnych budów.")

    elif menu_admin == "🚗 Zarządzanie Autami":
        st.markdown("### 🚗 Dodaj nowy pojazd do floty")

        with st.form("form_dodaj_auto", clear_on_submit=True):
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                nr_rej_input = st.text_input("Numer rejestracyjny (np. DW 12345)")
            with col_a2:
                opis_auta_input = st.text_input("Opis / Model pojazdu")

            submit_auto = st.form_submit_button("Dodaj pojazd")

            if submit_auto:
                czysty_nr = nr_rej_input.strip().upper()
                if not czysty_nr:
                    st.warning("⚠️ Podaj numer rejestracyjny.")
                else:
                    sukces_auto = zapisz_auto(czysty_nr, opis_auta_input.strip())
                    if sukces_auto:
                        st.success(f"✅ Dodano pojazd: {czysty_nr}")
                        st.rerun()
                    else:
                        st.error("❌ Pojazd o takim numerze rejestracyjnym już istnieje.")

        st.markdown("---")
        st.markdown("### 📋 Lista zarejestrowanych pojazdów i raporty")

        df_pelne_auta = wczytaj_pelne_dane_aut()
        df_dane_wielkie = wczytaj_dane()

        if not df_pelne_auta.empty:
            from io import BytesIO
            
            def generuj_raport_aut_excel(df_auta, df_wpisy):
                output = BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    summary_rows = []
                    for _, r_auto in df_auta.iterrows():
                        nr = r_auto["Nr Rejestracyjny"]
                        opis = r_auto.get("Opis", "")
                        
                        if not df_wpisy.empty:
                            w_auta = df_wpisy[
                                (df_wpisy["Nr Rejestracyjny"] == nr) | 
                                (df_wpisy["Nr Rejestracyjny Powrót"] == nr)
                            ]
                            liczba_uzyc = len(w_auta)
                            c_dojazd = w_auta["Czas dojazdu (godz)"].sum() if "Czas dojazdu (godz)" in w_auta.columns else 0.0
                            c_powrot = w_auta["Czas powrotu (godz)"].sum() if "Czas powrotu (godz)" in w_auta.columns else 0.0
                            suma_godzin = c_dojazd + c_powrot
                        else:
                            w_auta = pd.DataFrame()
                            liczba_uzyc = 0
                            suma_godzin = 0.0

                        summary_rows.append({
                            "Nr Rejestracyjny": nr,
                            "Opis / Model": opis,
                            "Liczba przejazdów": liczba_uzyc,
                            "Łączny czas tras (h)": round(suma_godzin, 2)
                        })
                        
                        safe_sheet_name = str(nr)[:31]
                        if not w_auta.empty:
                            w_auta.to_excel(writer, index=False, sheet_name=safe_sheet_name)
                        else:
                            pd.DataFrame({"Informacja": ["Brak przejazdów"]}).to_excel(writer, index=False, sheet_name=safe_sheet_name)

                    df_summary = pd.DataFrame(summary_rows)
                    df_summary.to_excel(writer, index=False, sheet_name="Podsumowanie_Floty")
                return output.getvalue()

            excel_auta_data = generuj_raport_aut_excel(df_pelne_auta, df_dane_wielkie)
            st.download_button(
                label="📥 Pobierz pełny raport floty (każde auto w osobnym arkuszu)",
                data=excel_auta_data,
                file_name="raport_uzycia_aut.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            st.markdown("---")

        if "edytowane_auto" not in st.session_state:
            st.session_state.edytowane_auto = None

        if not df_pelne_auta.empty:
            for idx, row in df_pelne_auta.iterrows():
                nr = row["Nr Rejestracyjny"]
                opis = row.get("Opis", "")

                with st.container(border=True):
                    col_ia, col_ba = st.columns([7.0, 3.0])
                    with col_ia:
                        st.write(f"🚗 **{nr}** | Opis: `{opis}`")
                    with col_ba:
                        sub_au1, sub_au2 = st.columns(2)
                        with sub_au1:
                            if st.button("✏️", key=f"edit_auto_{idx}", help="Edytuj pojazd", use_container_width=True):
                                st.session_state.edytowane_auto = nr
                                st.rerun()
                        with sub_au2:
                            if st.button("🗑️", key=f"del_auto_{idx}", help="Usuń pojazd", use_container_width=True):
                                usun_auto(nr)
                                st.success(f"Usunięto pojazd: {nr}")
                                st.rerun()

            if st.session_state.edytowane_auto:
                st.markdown("---")
                stara_rejestracja = st.session_state.edytowane_auto
                st.markdown(f"### ✏️ Edycja pojazdu: **{stara_rejestracja}**")
                
                aktualny_opis_wiersz = df_pelne_auta[df_pelne_auta["Nr Rejestracyjny"] == stara_rejestracja]
                domyslny_opis = aktualny_opis_wiersz.iloc[0].get("Opis", "") if not aktualny_opis_wiersz.empty else ""

                with st.form("form_edycja_auta"):
                    nowy_nr_rej = st.text_input("Numer rejestracyjny", value=stara_rejestracja)
                    nowy_opis = st.text_input("Opis / Model pojazdu", value=domyslny_opis)
                    
                    c_zapisz_a, c_anuluj_a = st.columns(2)
                    with c_zapisz_a:
                        btn_zapisz_a = st.form_submit_button("💾 Zapisz zmiany", use_container_width=True)
                    with c_anuluj_a:
                        btn_anuluj_a = st.form_submit_button("❌ Anuluj", use_container_width=True)

                    if btn_zapisz_a:
                        czysty_nowy_nr = nowy_nr_rej.strip().upper()
                        if not czysty_nowy_nr:
                            st.warning("Numer rejestracyjny nie może być pusty!")
                        elif czysty_nowy_nr != stara_rejestracja and czysty_nowy_nr in df_pelne_auta["Nr Rejestracyjny"].values:
                            st.error("Pojazd o takim numerze rejestracyjnym już istnieje w bazie!")
                        else:
                            df_pelne_auta.loc[df_pelne_auta["Nr Rejestracyjny"] == stara_rejestracja, "Nr Rejestracyjny"] = czysty_nowy_nr
                            df_pelne_auta.loc[df_pelne_auta["Nr Rejestracyjny"] == czysty_nowy_nr, "Opis"] = nowy_opis.strip()
                            df_pelne_auta.to_csv(PLIK_AUTA, index=False)

                            st.session_state.edytowane_auto = None
                            st.success("✅ Zaktualizowano pojazd pomyślnie!")
                            st.rerun()

                    if btn_anuluj_a:
                        st.session_state.edytowane_auto = None
                        st.rerun()
        else:
            st.info("Brak aut w bazie.")

else:
    # --- PANEL DLA ZWYKŁEGO PRACOWNIKA ---
    st.subheader(f"Witaj, {zalogowany_pracownik}!")
    st.markdown("---")

    if not lista_budow:
        st.error("❌ Brak dostępnych budów w systemie. Poproś administratora o dodanie budowy.")
    else:
        st.subheader("Dodaj wpis czasu pracy")
        
        data = st.date_input("Data", value=pd.Timestamp.today().date())
        budowa = st.selectbox("Wybierz budowę", lista_budow)

        st.markdown("⏱️ **Czas pracy na budowie** (obowiązkowy)")
        col1, col2 = st.columns(2)
        with col1:
            godzina_od = st.time_input("Godzina od", value=pd.to_datetime("08:00").time())
        with col2:
            godzina_do = st.time_input("Godzina do", value=pd.to_datetime("16:00").time())

        # Dynamicznie rozwijana sekcja dojazdu
        czy_dojazd = st.checkbox("🚗 Zgłoś dojazd firmowym autem")
        dojazd_od, dojazd_do = pd.to_datetime("07:00").time(), pd.to_datetime("08:00").time()
        auto_dojazd = "Brak"
        if czy_dojazd:
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                dojazd_od = st.time_input("Dojazd od", value=pd.to_datetime("07:00").time())
            with col_d2:
                dojazd_do = st.time_input("Dojazd do", value=pd.to_datetime("08:00").time())
            auto_dojazd = st.selectbox("Numer rejestracyjny auta na dojazd", lista_aut if lista_aut else ["Brak"])

        # Dynamicznie rozwijana sekcja powrotu
        czy_powrot = st.checkbox("🏠 Zgłoś powrót firmowym autem")
        powrot_od, powrot_do = pd.to_datetime("16:00").time(), pd.to_datetime("17:00").time()
        auto_powrot = "Brak"
        if czy_powrot:
            col_pow1, col_pow2 = st.columns(2)
            with col_pow1:
                powrot_od = st.time_input("Powrót od", value=pd.to_datetime("16:00").time())
            with col_pow2:
                powrot_do = st.time_input("Powrót do", value=pd.to_datetime("17:00").time())
            auto_powrot = st.selectbox("Numer rejestracyjny auta na powrót", lista_aut if lista_aut else ["Brak"])

        if st.button("Dodaj wpis", use_container_width=True, type="primary"):
            start_dt = pd.to_datetime(f"{data} {godzina_od}")
            koniec_dt = pd.to_datetime(f"{data} {godzina_do}")

            dojazd_start_dt = pd.to_datetime(f"{data} {dojazd_od}") if czy_dojazd else start_dt
            dojazd_koniec_dt = pd.to_datetime(f"{data} {dojazd_do}") if czy_dojazd else start_dt
            
            powrot_start_dt = pd.to_datetime(f"{data} {powrot_od}") if czy_powrot else koniec_dt
            powrot_koniec_dt = pd.to_datetime(f"{data} {powrot_do}") if czy_powrot else koniec_dt

            if koniec_dt <= start_dt:
                st.error("Błąd: Godzina zakończenia pracy musi być późniejsza niż rozpoczęcia!")
            elif czy_dojazd and dojazd_koniec_dt < dojazd_start_dt:
                st.error("Błąd: Godzina zakończenia dojazdu musi być późniejsza lub równa rozpoczęciu!")
            elif czy_dojazd and auto_dojazd == "Brak":
                st.error("Błąd: Jeśli zgłaszasz dojazd, musisz wybrać numer rejestracyjny auta!")
            elif czy_powrot and powrot_koniec_dt < powrot_start_dt:
                st.error("Błąd: Godzina zakończenia powrotu musi być późniejsza lub równa rozpoczęciu!")
            elif czy_powrot and auto_powrot == "Brak":
                st.error("Błąd: Jeśli zgłaszasz powrót, musisz wybrać numer rejestracyjny auta!")
            else:
                AktualneDane = wczytaj_dane()
                konflikt_pracownika = sprawdz_konflikt_czasowy(
                    AktualneDane, zalogowany_pracownik, str(data),
                    dojazd_start_dt, dojazd_koniec_dt, start_dt, koniec_dt,
                    powrot_start_dt, powrot_koniec_dt, czy_dojazd, czy_powrot
                )
                konflikt_auta_d = sprawdz_konflikt_pojazdu_dojazd(
                    AktualneDane, auto_dojazd, str(data), dojazd_start_dt, dojazd_koniec_dt, czy_dojazd
                )
                konflikt_auta_p = sprawdz_konflikt_pojazdu_powrot(
                    AktualneDane, auto_powrot, str(data), powrot_start_dt, powrot_koniec_dt, czy_powrot
                )

                if konflikt_pracownika:
                    st.error("❌ Błąd: Wybrane godziny kolidują z innym Twoim wpisem w tym dniu!")
                elif konflikt_auta_d:
                    st.error(f"❌ Błąd: Pojazd dojazdu (**{auto_dojazd}**) jest już zajęty w tym przedziale czasowym!")
                elif konflikt_auta_p:
                    st.error(f"❌ Błąd: Pojazd powrotu (**{auto_powrot}**) jest już zajęty w tym przedziale czasowym!")
                else:
                    roznica_czasu = (koniec_dt - start_dt).total_seconds() / 3600
                    roznica_dojazdu = (dojazd_koniec_dt - dojazd_start_dt).total_seconds() / 3600 if czy_dojazd else 0.0
                    roznica_powrotu = (powrot_koniec_dt - powrot_start_dt).total_seconds() / 3600 if czy_powrot else 0.0

                    aktualna_stawka = pobierz_stawke_pracownika(zalogowany_pracownik, str(data))

                    koszt_pracy = roznica_czasu * aktualna_stawka
                    stawka_dojazdu = aktualna_stawka / 2.0
                    koszt_dojazdu_zl = roznica_dojazdu * stawka_dojazdu if czy_dojazd else 0.0
                    koszt_powrotu_zl = roznica_powrotu * stawka_dojazdu if czy_powrot else 0.0
                    razem = koszt_pracy + koszt_dojazdu_zl + koszt_powrotu_zl

                    nowy_wpis = {
                        "Pracownik": zalogowany_pracownik,
                        "Data": str(data),
                        "Budowa": budowa,
                        "Nr Rejestracyjny": auto_dojazd if czy_dojazd else "Brak",
                        "Dojazd Od": str(dojazd_od) if czy_dojazd else "00:00",
                        "Dojazd Do": str(dojazd_do) if czy_dojazd else "00:00",
                        "Czas dojazdu (godz)": round(roznica_dojazdu, 2),
                        "Od": str(godzina_od),
                        "Do": str(godzina_do),
                        "Stawka (zł/h)": aktualna_stawka,
                        "Godziny": round(roznica_czasu, 2),
                        "Koszt pracy (zł)": round(koszt_pracy, 2),
                        "Koszt dojazdu (zł)": round(koszt_dojazdu_zl, 2),
                        "Powrót Od": str(powrot_od) if czy_powrot else "00:00",
                        "Powrót Do": str(powrot_do) if czy_powrot else "00:00",
                        "Czas powrotu (godz)": round(roznica_powrotu, 2),
                        "Nr Rejestracyjny Powrót": auto_powrot if czy_powrot else "Brak",
                        "Koszt powrotu (zł)": round(koszt_powrotu_zl, 2),
                        "Razem (zł)": round(razem, 2),
                    }

                    AktualneDane = pd.concat([AktualneDane, pd.DataFrame([nowy_wpis])], ignore_index=True)
                    zapisz_dane(AktualneDane)
                    st.success(f"✅ Zapisano pomyślnie!")
                    st.rerun()

    # --- WIDOK WŁASNYCH WPISÓW PRACOWNIKA ---
    st.markdown("---")
    st.subheader("📋 Twoje dotychczasowe wpisy")

    AktualneDane = wczytaj_dane()
    if not AktualneDane.empty:
        moje_dane = AktualneDane[AktualneDane["Pracownik"] == zalogowany_pracownik]

        if not moje_dane.empty:
            mc1, mc2 = st.columns(2)
            mc1.metric("Twoje godziny", f"{moje_dane['Godziny'].sum():.2f} h")
            mc2.metric("Dojazd + Powrót (czas/koszt)", f"{(moje_dane['Czas dojazdu (godz)'].sum() + moje_dane['Czas powrotu (godz)'].sum()):.2f} h")
            
            st.markdown("---")
            st.dataframe(moje_dane, use_container_width=True)

            def convert_df_to_excel(df):
                from io import BytesIO
                output = BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False, sheet_name="Moje_Rozliczenie")
                return output.getvalue()

            excel_data = convert_df_to_excel(moje_dane)
            st.download_button(
                label="📥 Pobierz moje rozliczenie do Excela (.xlsx)",
                data=excel_data,
                file_name=f"rozliczenie_{zalogowany_pracownik.lower().replace(' ', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        else:
            st.info("Nie masz jeszcze żadnych wpisów.")
    else:
        st.info("Brak wpisów w systemie.")