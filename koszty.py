import os
import pathlib
from PIL import Image
import pandas as pd
import streamlit as st
import bcrypt
from io import BytesIO

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


def hashuj_haslo(haslo: str) -> str:
    """Generuje hash bcrypt dla podanego hasła."""
    sol = bcrypt.gensalt()
    return bcrypt.hashpw(haslo.encode("utf-8"), sol).decode("utf-8")


def zweryfikuj_haslo(haslo: str, hash_bazy: str) -> bool:
    """Weryfikuje hasło względem hasha z bazy (obsługuje też wsteczną kompatybilność z plain text)."""
    if not hash_bazy.startswith("$2b$") and not hash_bazy.startswith("$2a$"):
        return haslo == hash_bazy
    try:
        return bcrypt.checkpw(haslo.encode("utf-8"), hash_bazy.encode("utf-8"))
    except Exception:
        return False


def wczytaj_pracownikow():
    if os.path.exists(PLIK_PRACOWNICY):
        df = pd.read_csv(PLIK_PRACOWNICY, dtype=str)
        if "Pin" in df.columns and "Email" not in df.columns:
            df["Email"] = df["Pracownik"].str.lower().str.replace(" ", "") + "@firma.pl"
            df = df.rename(columns={"Pin": "Haslo"})
        if "Email" not in df.columns:
            df["Email"] = ""
        if "Haslo" not in df.columns:
            df["Haslo"] = hashuj_haslo("123456")
        if "Rola" not in df.columns:
            df["Rola"] = "Pracownik"
        
        df.loc[(df["Email"] == "admin@firma.pl") | (df["Pracownik"] == "Admin"), "Rola"] = "Admin"
        
        zmieniono = False
        for idx, row in df.iterrows():
            h = str(row["Haslo"])
            if not h.startswith("$2b$") and not h.startswith("$2a$"):
                df.at[idx, "Haslo"] = hashuj_haslo(h)
                zmieniono = True
        if zmieniono:
            df.to_csv(PLIK_PRACOWNICY, index=False)

        return df
    else:
        df_domyslne = pd.DataFrame(
            {
                "Email": ["jan.kowalski@firma.pl", "adam.nowak@firma.pl", "admin@firma.pl"],
                "Haslo": [hashuj_haslo("123456"), hashuj_haslo("123456"), hashuj_haslo("123456")],
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


def wczytaj_pelne_dane_budow():
    if os.path.exists(PLIK_BUDOWY):
        df = pd.read_csv(PLIK_BUDOWY, dtype=str)
        if "Budowa" in df.columns:
            if "DataRozpoczecia" not in df.columns:
                df["DataRozpoczecia"] = "2024-01-01"
                df.to_csv(PLIK_BUDOWY, index=False)
            return df
    
    domyslne_df = pd.DataFrame({
        "Budowa": [
            "Budowa ul. Słoneczna 5",
            "Osiedle Parkowe - Blok A",
            "Remont Biurowca Centrum",
        ],
        "DataRozpoczecia": ["2024-01-01", "2024-02-01", "2024-03-01"]
    })
    domyslne_df.to_csv(PLIK_BUDOWY, index=False)
    return domyslne_df


def wczytaj_budowy():
    df = wczytaj_pelne_dane_budow()
    if not df.empty and "Budowa" in df.columns:
        return df["Budowa"].dropna().unique().tolist()
    return []


def pobierz_date_rozpoczecia_budowy(nazwa_budowy):
    df = wczytaj_pelne_dane_budow()
    if not df.empty and "Budowa" in df.columns and "DataRozpoczecia" in df.columns:
        wynik = df[df["Budowa"] == nazwa_budowy]
        if not wynik.empty:
            val = wynik.iloc[0]["DataRozpoczecia"]
            if pd.notna(val) and val != "":
                return str(val)
    return "2024-01-01"


def zapisz_budowe(nowa_nazwa, data_rozpoczecia):
    df = wczytaj_pelne_dane_budow()
    if nowa_nazwa not in df["Budowa"].values:
        nowy_wiersz = pd.DataFrame({"Budowa": [nowa_nazwa], "DataRozpoczecia": [str(data_rozpoczecia)]})
        df = pd.concat([df, nowy_wiersz], ignore_index=True)
        df.to_csv(PLIK_BUDOWY, index=False)
        return True
    return False


def edytuj_budowe(stara_nazwa, nowa_nazwa, nowa_data):
    df = wczytaj_pelne_dane_budow()
    if stara_nazwa != nowa_nazwa and nowa_nazwa in df["Budowa"].values:
        return False
    
    df.loc[df["Budowa"] == stara_nazwa, "Budowa"] = nowa_nazwa
    df.loc[df["Budowa"] == nowa_nazwa, "DataRozpoczecia"] = str(nowa_data)
    df.to_csv(PLIK_BUDOWY, index=False)

    if stara_nazwa != nowa_nazwa:
        df_dane = wczytaj_dane()
        if not df_dane.empty and "Budowa" in df_dane.columns:
            df_dane.loc[df_dane["Budowa"] == stara_nazwa, "Budowa"] = nowa_nazwa
            zapisz_dane(df_dane)
    return True


def usun_budowe(nazwa_do_usuniecia):
    df = wczytaj_pelne_dane_budow()
    if nazwa_do_usuniecia in df["Budowa"].values:
        df = df[df["Budowa"] != nazwa_do_usuniecia]
        df.to_csv(PLIK_BUDOWY, index=False)
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
            "Nr Rejestracyjny Powrót": "Brak",
            "Zatwierdzone": "Nie"
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
                "Zatwierdzone",
            ]
        )


def zapisz_dane(df):
    df.to_csv(PLIK_BAZY, index=False)


def sprawdz_konflikt_czasowy(df_dane, pracownik, data_str, d_od_dt, d_do_dt, p_od_dt, p_do_dt, pow_od_dt, pow_do_dt, czy_dojazd, czy_powrot, pomijany_index=None):
    if df_dane.empty:
        return False

    istniejace = df_dane[
        (df_dane["Pracownik"] == pracownik) & (df_dane["Data"] == data_str)
    ]

    if pomijany_index is not None and pomijany_index in istniejace.index:
        istniejace = istniejace.drop(pomijany_index)

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


def sprawdz_konflikt_pojazdu_dojazd(df_dane, auto, data_str, d_od_dt, d_do_dt, czy_dojazd, pomijany_index=None):
    if df_dane.empty or not czy_dojazd or auto == "Brak" or pd.isna(auto):
        return False

    def przedzialy_sie_nakladaja(s1, e1, s2, e2):
        if s1 == e1 or s2 == e2:
            return False
        return max(s1, s2) < min(e1, e2)

    df_sprawdzenie = df_dane[df_dane["Data"] == data_str]
    if pomijany_index is not None and pomijany_index in df_sprawdzenie.index:
        df_sprawdzenie = df_sprawdzenie.drop(pomijany_index)

    for _, row in df_sprawdzenie.iterrows():
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


def sprawdz_konflikt_pojazdu_powrot(df_dane, auto, data_str, pow_od_dt, pow_do_dt, czy_powrot, pomijany_index=None):
    if df_dane.empty or not czy_powrot or auto == "Brak" or pd.isna(auto):
        return False

    def przedzialy_sie_nakladaja(s1, e1, s2, e2):
        if s1 == e1 or s2 == e2:
            return False
        return max(s1, s2) < min(e1, e2)

    df_sprawdzenie = df_dane[df_dane["Data"] == data_str]
    if pomijany_index is not None and pomijany_index in df_sprawdzenie.index:
        df_sprawdzenie = df_sprawdzenie.drop(pomijany_index)

    for _, row in df_sprawdzenie.iterrows():
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

# --- AUTOMATYCZNE LOGOWANIE Z PARAMETRÓW URL ---
if not st.session_state.zalogowany and "user" in st.query_params:
    url_user = st.query_params["user"]
    df_pracownicy_init = wczytaj_pracownikow()
    pasujacy_url = df_pracownicy_init[df_pracownicy_init["Pracownik"] == url_user]
    if not pasujacy_url.empty:
        st.session_state.zalogowany = True
        st.session_state.aktualny_pracownik = pasujacy_url.iloc[0]["Pracownik"]
        st.session_state.rola = str(pasujacy_url.iloc[0]["Rola"]).strip()

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
        pasujacy_email = df_pracownicy[df_pracownicy["Email"].str.lower() == email_input.strip().lower()]

        zalogowano_pomyślnie = False
        if not pasujacy_email.empty:
            hash_z_bazy = pasujacy_email.iloc[0]["Haslo"]
            if zweryfikuj_haslo(haslo_input, hash_z_bazy):
                nazwa_zalogowanego = pasujacy_email.iloc[0]["Pracownik"]
                st.session_state.zalogowany = True
                st.session_state.aktualny_pracownik = nazwa_zalogowanego
                st.session_state.rola = str(pasujacy_email.iloc[0]["Rola"]).strip()
                st.query_params["user"] = nazwa_zalogowanego
                zalogowano_pomyślnie = True
                st.rerun()

        if not zalogowano_pomyślnie:
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
    if "user" in st.query_params:
        del st.query_params["user"]
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

                czy_dojazd_adm = st.checkbox("🚗 Dodaj dojazd firmowym autem", key="adm_chk_dojazd_dyn")
                dojazd_od_adm, dojazd_do_adm = pd.to_datetime("07:00").time(), pd.to_datetime("08:00").time()
                auto_dojazd_adm = "Brak"
                
                if czy_dojazd_adm:
                    if "adm_poprzedni_dojazd" not in st.session_state:
                        st.session_state["adm_poprzedni_dojazd"] = False

                    col_da1, col_da2 = st.columns(2)
                    with col_da1:
                        dojazd_od_adm = st.time_input("Dojazd od", value=pd.to_datetime("07:00").time(), key="adm_doj_od")
                    with col_da2:
                        def aktualizuj_start_pracy_adm():
                            st.session_state["adm_t_od"] = st.session_state["adm_doj_do"]
                        dojazd_do_adm = st.time_input("Dojazd do", value=pd.to_datetime("08:00").time(), key="adm_doj_do", on_change=aktualizuj_start_pracy_adm)
                    
                    auto_dojazd_adm = st.selectbox("Auto na dojazd", lista_aut if lista_aut else ["Brak"], key="adm_auta_d")
                    
                    if not st.session_state["adm_poprzedni_dojazd"]:
                        st.session_state["adm_t_od"] = dojazd_do_adm
                        st.session_state["adm_poprzedni_dojazd"] = True
                        
                    domyslna_praca_od_adm = st.session_state.get("adm_t_od", dojazd_do_adm)
                else:
                    st.session_state["adm_poprzedni_dojazd"] = False
                    domyslna_praca_od_adm = pd.to_datetime("08:00").time()

                st.markdown("⏱️ **Czas pracy na budowie** (obowiązkowy)")
                
                if "adm_poprzedni_powrot" not in st.session_state:
                    st.session_state["adm_poprzedni_powrot"] = False

                col_pa1, col_pa2 = st.columns(2)
                with col_pa1:
                    godzina_od_adm = st.time_input("Godzina od", value=domyslna_praca_od_adm, key="adm_t_od")
                with col_pa2:
                    domyslny_koniec_pracy_adm = (pd.Timestamp(f"2026-01-01 {godzina_od_adm}") + pd.Timedelta(hours=8)).time()
                    
                    def aktualizuj_start_powrotu_adm():
                        st.session_state["adm_pow_od"] = st.session_state["adm_t_do_koniec"]
                        st.session_state["adm_poprzedni_powrot"] = True

                    godzina_do_adm = st.time_input("Godzina do", value=domyslny_koniec_pracy_adm, key="adm_t_do_koniec", on_change=aktualizuj_start_powrotu_adm)

                czy_powrot_adm = st.checkbox("🏠 Dodaj powrót firmowym autem", key="adm_chk_powrot_dyn")
                powrot_od_adm, powrot_do_adm = pd.to_datetime("16:00").time(), pd.to_datetime("17:00").time()
                auto_powrot_adm = "Brak"
                
                if czy_powrot_adm:
                    if not st.session_state["adm_poprzedni_powrot"]:
                        st.session_state["adm_pow_od"] = godzina_do_adm
                        st.session_state["adm_poprzedni_powrot"] = True

                    domyslny_powrot_od_adm = st.session_state.get("adm_pow_od", godzina_do_adm)

                    col_powa1, col_powa2 = st.columns(2)
                    with col_powa1:
                        powrot_od_adm = st.time_input("Powrót od", value=domyslny_powrot_od_adm, key="adm_pow_od")
                    with col_powa2:
                        domyslny_powrot_do_adm = (pd.Timestamp(f"2026-01-01 {domyslny_powrot_od_adm}") + pd.Timedelta(hours=1)).time()
                        powrot_do_adm = st.time_input("Powrót do", value=domyslny_powrot_do_adm, key="adm_pow_do")
                    auto_powrot_adm = st.selectbox("Auto na powrót", lista_aut if lista_aut else ["Brak"], key="adm_auta_p")
                else:
                    st.session_state["adm_poprzedni_powrot"] = False

                if st.button("💾 Dodaj ten wpis dla pracownika", use_container_width=True, type="primary", key="btn_save_adm"):
                    data_rozpoczecia_budowy_str = pobierz_date_rozpoczecia_budowy(budowa_adm)
                    data_rozp_dt = pd.to_datetime(data_rozpoczecia_budowy_str).date()

                    start_dt = pd.to_datetime(f"{data_adm} {godzina_od_adm}")
                    koniec_dt = pd.to_datetime(f"{data_adm} {godzina_do_adm}")
                    
                    dojazd_start_dt = pd.to_datetime(f"{data_adm} {dojazd_od_adm}") if czy_dojazd_adm else start_dt
                    dojazd_koniec_dt = pd.to_datetime(f"{data_adm} {dojazd_do_adm}") if czy_dojazd_adm else start_dt
                    
                    powrot_start_dt = pd.to_datetime(f"{data_adm} {powrot_od_adm}") if czy_powrot_adm else koniec_dt
                    powrot_koniec_dt = pd.to_datetime(f"{data_adm} {powrot_do_adm}") if czy_powrot_adm else koniec_dt

                    if data_adm < data_rozp_dt:
                        st.error(f"❌ Błąd: Data wpisu ({data_adm}) jest wcześniejsza niż data rozpoczęcia budowy ({data_rozp_dt})!")
                    elif koniec_dt <= start_dt:
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
                                "Zatwierdzone": "Tak"
                            }

                            AktualneDane = pd.concat([AktualneDane, pd.DataFrame([nowy_wpis_adm])], ignore_index=True)
                            zapisz_dane(AktualneDane)
                            st.success(f"✅ Pomyślnie dopisano godziny dla pracownika: **{wybrany_pracownik_adm}**")
                            st.rerun()

        st.markdown("---")

        dane_systemowe = wczytaj_dane()
        if not dane_systemowe.empty:
            # --- PODSUMOWANIE ADMINISTRATORA ---
            # Ten sam styl kart/podsumowania co w panelu pracownika.
            suma_godzin_adm = pd.to_numeric(
                dane_systemowe.get("Godziny", pd.Series(dtype=float)), errors="coerce"
            ).fillna(0).sum()
            suma_koszt_pracy_adm = pd.to_numeric(
                dane_systemowe.get("Koszt pracy (zł)", pd.Series(dtype=float)), errors="coerce"
            ).fillna(0).sum()
            suma_koszt_dojazdu_adm = pd.to_numeric(
                dane_systemowe.get("Koszt dojazdu (zł)", pd.Series(dtype=float)), errors="coerce"
            ).fillna(0).sum()
            suma_koszt_powrotu_adm = pd.to_numeric(
                dane_systemowe.get("Koszt powrotu (zł)", pd.Series(dtype=float)), errors="coerce"
            ).fillna(0).sum()
            suma_lacznego_kosztu_adm = pd.to_numeric(
                dane_systemowe.get("Razem (zł)", pd.Series(dtype=float)), errors="coerce"
            ).fillna(0).sum()
            suma_czasu_dojazdu_adm = pd.to_numeric(
                dane_systemowe.get("Czas dojazdu (godz)", pd.Series(dtype=float)), errors="coerce"
            ).fillna(0).sum()
            suma_czasu_powrotu_adm = pd.to_numeric(
                dane_systemowe.get("Czas powrotu (godz)", pd.Series(dtype=float)), errors="coerce"
            ).fillna(0).sum()
            suma_lacznego_czasu_adm = (
                suma_godzin_adm + suma_czasu_dojazdu_adm + suma_czasu_powrotu_adm
            )

            st.markdown("### 📊 Podsumowanie czasu i kosztów")

            # Wybór budowy wpływa na wartości widoczne w podsumowaniu.
            if "Budowa" in dane_systemowe.columns:
                budowy_do_podsumowania = (
                    dane_systemowe["Budowa"]
                    .dropna()
                    .astype(str)
                    .loc[lambda s: s.str.strip() != ""]
                    .unique()
                    .tolist()
                )
            else:
                budowy_do_podsumowania = []

            budowy_do_podsumowania = sorted(budowy_do_podsumowania)
            opcje_budowy_podsumowania = ["🏗️ Wszystkie budowy"] + budowy_do_podsumowania

            wybrana_budowa_podsumowania = st.selectbox(
                "🏗️ Wybierz budowę do podsumowania:",
                opcje_budowy_podsumowania,
               key="admin_budowa_podsumowanie"
            )

            if wybrana_budowa_podsumowania == "🏗️ Wszystkie budowy":
                dane_podsumowania_admin = dane_systemowe
            else:
                dane_podsumowania_admin = dane_systemowe[
                    dane_systemowe["Budowa"] == wybrana_budowa_podsumowania
                ]

            suma_godzin_admin = pd.to_numeric(
                dane_podsumowania_admin.get("Godziny", pd.Series(dtype=float)),
                errors="coerce"
            ).fillna(0).sum()

            suma_dojazdow_admin = pd.to_numeric(
                dane_podsumowania_admin.get("Czas dojazdu (godz)", pd.Series(dtype=float)),
                errors="coerce"
            ).fillna(0).sum()

            suma_powrotow_admin = pd.to_numeric(
                dane_podsumowania_admin.get("Czas powrotu (godz)", pd.Series(dtype=float)),
                errors="coerce"
            ).fillna(0).sum()

            pod1, pod2, pod3 = st.columns(3)
            with pod1:
                st.metric("⏱️ Łączna ilość godzin", f"{suma_godzin_admin:.2f} h")
            with pod2:
                st.metric("🚗 Łączny czas dojazdów", f"{suma_dojazdow_admin:.2f} h")
            with pod3:
                st.metric("🏠 Łączny czas powrotów", f"{suma_powrotow_admin:.2f} h")

            st.markdown("---")

            st.markdown("### 🛠️ Zarządzanie wpisami (Zatwierdzanie / Edycja / Usuwanie)")

            df_pracownicy_adm = wczytaj_pracownikow()
            lista_pracownikow_filtru = ["Wszyscy pracownicy"] + df_pracownicy_adm["Pracownik"].tolist()
            wybrany_filtr_pracownika = st.selectbox("🔎 Filtruj wpisy według pracownika:", lista_pracownikow_filtru)

            if wybrany_filtr_pracownika != "Wszyscy pracownicy":
                dane_do_wyswietlenia = dane_systemowe[dane_systemowe["Pracownik"] == wybrany_filtr_pracownika]
            else:
                dane_do_wyswietlenia = dane_systemowe

            if "edytowany_wpis_id" not in st.session_state:
                st.session_state.edytowany_wpis_id = None

            if st.session_state.edytowany_wpis_id is not None:
                e_id = st.session_state.edytowany_wpis_id
                if e_id in dane_systemowe.index:
                    wiersz_ed = dane_systemowe.loc[e_id]
                    
                    if str(wiersz_ed.get("Zatwierdzone", "Nie")) == "Tak":
                        st.warning("⚠️ Ten wpis jest zatwierdzony. Musisz najpierw wcisnąć przycisk cofnięcia edycji/zatwierdzenia (🔓), aby go edytować.")
                        st.session_state.edytowany_wpis_id = None
                        st.rerun()

                    st.markdown(f"#### ✏️ Edycja wpisu ID `{e_id}` (Pracownik: **{wiersz_ed['Pracownik']}**, Data: `{wiersz_ed['Data']}`)")

                    with st.form(f"form_edycja_wpisu_{e_id}"):
                        e_pracownik = st.selectbox("Pracownik", df_pracownicy_adm["Pracownik"].tolist(), index=df_pracownicy_adm["Pracownik"].tolist().index(wiersz_ed['Pracownik']) if wiersz_ed['Pracownik'] in df_pracownicy_adm["Pracownik"].tolist() else 0)
                        e_data = st.date_input("Data wpisu", value=pd.to_datetime(wiersz_ed['Data']).date())
                        e_budowa = st.selectbox("Budowa", lista_budow, index=lista_budow.index(wiersz_ed['Budowa']) if wiersz_ed['Budowa'] in lista_budow else 0)

                        akt_auto_d = wiersz_ed.get("Nr Rejestracyjny", "Brak")
                        czy_byl_dojazd = akt_auto_d != "Brak" and pd.notna(akt_auto_d)
                        e_czy_doj = st.checkbox("🚗 Dojazd firmowym autem", value=czy_byl_dojazd)
                        
                        d_od_val = pd.to_datetime(wiersz_ed.get("Dojazd Od", "07:00")).time() if czy_byl_dojazd else pd.to_datetime("07:00").time()
                        d_do_val = pd.to_datetime(wiersz_ed.get("Dojazd Do", "08:00")).time() if czy_byl_dojazd else pd.to_datetime("08:00").time()
                        
                        col_ed1, col_ed2 = st.columns(2)
                        with col_ed1:
                            e_doj_od = st.time_input("Dojazd od", value=d_od_val)
                        with col_ed2:
                            e_doj_do = st.time_input("Dojazd do", value=d_do_val)
                        e_auto_d = st.selectbox("Auto na dojazd", ["Brak"] + lista_aut, index=(["Brak"] + lista_aut).index(akt_auto_d) if akt_auto_d in (["Brak"] + lista_aut) else 0)

                        st.markdown("⏱️ **Czas pracy na budowie**")
                        p_od_val = pd.to_datetime(wiersz_ed.get("Od", "08:00")).time()
                        p_do_val = pd.to_datetime(wiersz_ed.get("Do", "16:00")).time()
                        
                        col_ed3, col_ed4 = st.columns(2)
                        with col_ed3:
                            e_praca_od = st.time_input("Praca od", value=p_od_val)
                        with col_ed4:
                            e_praca_do = st.time_input("Praca do", value=p_do_val)

                        akt_auto_p = wiersz_ed.get("Nr Rejestracyjny Powrót", "Brak")
                        czy_byl_powrot = akt_auto_p != "Brak" and pd.notna(akt_auto_p)
                        e_czy_pow = st.checkbox("🏠 Powrót firmowym autem", value=czy_byl_powrot)

                        pow_od_val = pd.to_datetime(wiersz_ed.get("Powrót Od", "16:00")).time() if czy_byl_powrot else pd.to_datetime("16:00").time()
                        pow_do_val = pd.to_datetime(wiersz_ed.get("Powrót Do", "17:00")).time() if czy_byl_powrot else pd.to_datetime("17:00").time()

                        col_ed5, col_ed6 = st.columns(2)
                        with col_ed5:
                            e_pow_od = st.time_input("Powrót od", value=pow_od_val)
                        with col_ed6:
                            e_pow_do = st.time_input("Powrót do", value=pow_do_val)
                        e_auto_p = st.selectbox("Auto na powrót", ["Brak"] + lista_aut, index=(["Brak"] + lista_aut).index(akt_auto_p) if akt_auto_p in (["Brak"] + lista_aut) else 0)

                        col_ez1, col_ez2 = st.columns(2)
                        with col_ez1:
                            submit_edytuj_wpis = st.form_submit_button("💾 Zapisz zmiany we wpisie", use_container_width=True, type="primary")
                        with col_ez2:
                            submit_anuluj_edycje = st.form_submit_button("❌ Anuluj", use_container_width=True)

                        if submit_edytuj_wpis:
                            data_rozp_budowy_str = pobierz_date_rozpoczecia_budowy(e_budowa)
                            data_rozp_dt = pd.to_datetime(data_rozp_budowy_str).date()

                            start_dt = pd.to_datetime(f"{e_data} {e_praca_od}")
                            koniec_dt = pd.to_datetime(f"{e_data} {e_praca_do}")
                            
                            dojazd_start_dt = pd.to_datetime(f"{e_data} {e_doj_od}") if e_czy_doj else start_dt
                            dojazd_koniec_dt = pd.to_datetime(f"{e_data} {e_doj_do}") if e_czy_doj else start_dt
                            
                            powrot_start_dt = pd.to_datetime(f"{e_data} {e_pow_od}") if e_czy_pow else koniec_dt
                            powrot_koniec_dt = pd.to_datetime(f"{e_data} {e_pow_do}") if e_czy_pow else koniec_dt

                            auto_d_val = e_auto_d if e_czy_doj else "Brak"
                            auto_p_val = e_auto_p if e_czy_pow else "Brak"

                            if e_data < data_rozp_dt:
                                st.error(f"❌ Błąd: Data wpisu ({e_data}) jest wcześniejsza niż data rozpoczęcia budowy ({data_rozp_dt})!")
                            elif koniec_dt <= start_dt:
                                st.error("Błąd: Godzina zakończenia pracy musi być późniejsza niż rozpoczęcia!")
                            elif e_czy_doj and dojazd_koniec_dt < dojazd_start_dt:
                                st.error("Błąd: Godzina zakończenia dojazdu musi być późniejsza lub równa rozpoczęciu!")
                            elif e_czy_doj and auto_d_val == "Brak":
                                st.error("Błąd: Wybierz auto na dojazd!")
                            elif e_czy_pow and powrot_koniec_dt < powrot_start_dt:
                                st.error("Błąd: Godzina zakończenia powrotu musi być późniejsza lub równa rozpoczęciu!")
                            elif e_czy_pow and auto_p_val == "Brak":
                                st.error("Błąd: Wybierz auto na powrót!")
                            else:
                                AktDane = wczytaj_dane()
                                konflikt_pracownika = sprawdz_konflikt_czasowy(
                                    AktDane, e_pracownik, str(e_data), 
                                    dojazd_start_dt, dojazd_koniec_dt, start_dt, koniec_dt,
                                    powrot_start_dt, powrot_koniec_dt, e_czy_doj, e_czy_pow, pomijany_index=e_id
                                )
                                konflikt_auta_d = sprawdz_konflikt_pojazdu_dojazd(
                                    AktDane, auto_d_val, str(e_data), dojazd_start_dt, dojazd_koniec_dt, e_czy_doj, pomijany_index=e_id
                                )
                                konflikt_auta_p = sprawdz_konflikt_pojazdu_powrot(
                                    AktDane, auto_p_val, str(e_data), powrot_start_dt, powrot_koniec_dt, e_czy_pow, pomijany_index=e_id
                                )

                                if konflikt_pracownika:
                                    st.error("❌ Wybrane godziny kolidują z innym wpisem pracownika w tym dniu!")
                                elif konflikt_auta_d:
                                    st.error(f"❌ Pojazd dojazdu ({auto_d_val}) jest zajęty w tym przedziale czasowym!")
                                elif konflikt_auta_p:
                                    st.error(f"❌ Pojazd powrotu ({auto_p_val}) jest zajęty w tym przedziale czasowym!")
                                else:
                                    roznica_czasu = (koniec_dt - start_dt).total_seconds() / 3600
                                    roznica_dojazdu = (dojazd_koniec_dt - dojazd_start_dt).total_seconds() / 3600 if e_czy_doj else 0.0
                                    roznica_powrotu = (powrot_koniec_dt - powrot_start_dt).total_seconds() / 3600 if e_czy_pow else 0.0

                                    stawka_wybranego = pobierz_stawke_pracownika(e_pracownik, str(e_data))

                                    koszt_pracy = roznica_czasu * stawka_wybranego
                                    stawka_dojazdu = stawka_wybranego / 2.0
                                    koszt_dojazdu_zl = roznica_dojazdu * stawka_dojazdu if e_czy_doj else 0.0
                                    koszt_powrotu_zl = roznica_powrotu * stawka_dojazdu if e_czy_pow else 0.0
                                    razem = koszt_pracy + koszt_dojazdu_zl + koszt_powrotu_zl

                                    AktDane.loc[e_id, "Pracownik"] = e_pracownik
                                    AktDane.loc[e_id, "Data"] = str(e_data)
                                    AktDane.loc[e_id, "Budowa"] = e_budowa
                                    AktDane.loc[e_id, "Nr Rejestracyjny"] = auto_d_val
                                    AktDane.loc[e_id, "Dojazd Od"] = str(e_doj_od) if e_czy_doj else "00:00"
                                    AktDane.loc[e_id, "Dojazd Do"] = str(e_doj_do) if e_czy_doj else "00:00"
                                    AktDane.loc[e_id, "Czas dojazdu (godz)"] = round(roznica_dojazdu, 2)
                                    AktDane.loc[e_id, "Od"] = str(e_praca_od)
                                    AktDane.loc[e_id, "Do"] = str(e_praca_do)
                                    AktDane.loc[e_id, "Stawka (zł/h)"] = stawka_wybranego
                                    AktDane.loc[e_id, "Godziny"] = round(roznica_czasu, 2)
                                    AktDane.loc[e_id, "Koszt pracy (zł)"] = round(koszt_pracy, 2)
                                    AktDane.loc[e_id, "Koszt dojazdu (zł)"] = round(koszt_dojazdu_zl, 2)
                                    AktDane.loc[e_id, "Powrót Od"] = str(e_pow_od) if e_czy_pow else "00:00"
                                    AktDane.loc[e_id, "Powrót Do"] = str(e_pow_do) if e_czy_pow else "00:00"
                                    AktDane.loc[e_id, "Czas powrotu (godz)"] = round(roznica_powrotu, 2)
                                    AktDane.loc[e_id, "Nr Rejestracyjny Powrót"] = auto_p_val
                                    AktDane.loc[e_id, "Koszt powrotu (zł)"] = round(koszt_powrotu_zl, 2)
                                    AktDane.loc[e_id, "Razem (zł)"] = round(razem, 2)

                                    zapisz_dane(AktDane)
                                    st.session_state.edytowany_wpis_id = None
                                    st.success("✅ Pomyślnie zaktualizowano wpis!")
                                    st.rerun()

                        if submit_anuluj_edycje:
                            st.session_state.edytowany_wpis_id = None
                            st.rerun()
                else:
                    st.session_state.edytowany_wpis_id = None

            if not dane_do_wyswietlenia.empty:
                for idx, row in dane_do_wyswietlenia.iterrows():
                    status_zatw = row.get("Zatwierdzone", "Nie")
                    status_badge = "🟢 **Zatwierdzone**" if status_zatw == "Tak" else "🟠 **Oczekuje**"
                    
                    koszt_pracy_val = f"{row['Koszt pracy (zł)']:.2f}" if "Koszt pracy (zł)" in row and pd.notna(row["Koszt pracy (zł)"]) else "0.00"

                    with st.container(border=True):
                        col_tw1, col_tw2 = st.columns([7.5, 2.5])
                        with col_tw1:
                            st.markdown(
                                f"**ID: {idx}** | {status_badge} | 👤 **{row['Pracownik']}** | 📅 `{row['Data']}` | 🏗️ `{row['Budowa']}`\n"
                                f"⏱️ Praca: `{row['Od']} - {row['Do']}` (**{row['Godziny']}h**, {koszt_pracy_val} zł) | "
                                f"🚗 Dojazd: `{row['Nr Rejestracyjny']}` | 🏠 Powrót: `{row['Nr Rejestracyjny Powrót']}` | "
                                f"💰 **Razem: {row['Razem (zł)']} zł**"
                            )
                        with col_tw2:
                            sub_tw0, sub_tw1, sub_tw2 = st.columns(3)
                            with sub_tw0:
                                if status_zatw != "Tak":
                                    if st.button("✅", key=f"zatw_w_{idx}", help="Zatwierdź wpis", use_container_width=True):
                                        AktDane = wczytaj_dane()
                                        AktDane.loc[idx, "Zatwierdzone"] = "Tak"
                                        zapisz_dane(AktDane)
                                        st.success(f"Zatwierdzono wpis ID {idx}")
                                        st.rerun()
                                else:
                                    if st.button("🔓", key=f"odzatw_w_{idx}", help="Cofnij zatwierdzenie (odblokuj edycję)", use_container_width=True):
                                        AktDane = wczytaj_dane()
                                        AktDane.loc[idx, "Zatwierdzone"] = "Nie"
                                        zapisz_dane(AktDane)
                                        st.success(f"Cofnięto zatwierdzenie wpisu ID {idx} – edycja została odblokowana.")
                                        st.rerun()
                            with sub_tw1:
                                if status_zatw == "Tak":
                                    st.button("🔒", key=f"edit_lock_{idx}", help="Edycja zablokowana (najpierw cofnij zatwierdzenie)", use_container_width=True, disabled=True)
                                else:
                                    if st.button("✏️", key=f"edit_w_{idx}", help="Edytuj wpis", use_container_width=True):
                                        st.session_state.edytowany_wpis_id = idx
                                        st.rerun()
                            with sub_tw2:
                                if status_zatw == "Tak":
                                    st.button("🔒", key=f"del_lock_{idx}", help="Usuwanie zablokowane (wpis zatwierdzony)", use_container_width=True, disabled=True)
                                else:
                                    if st.button("🗑️", key=f"del_w_{idx}", help="Usuń wpis", use_container_width=True):
                                        nowe_dane = dane_systemowe.drop(idx)
                                        zapisz_dane(nowe_dane)
                                        st.success(f"Usunięto wpis ID {idx}")
                                        st.rerun()
            else:
                st.info("Brak wpisów dla wybranego pracownika.")

            st.markdown("---")
            st.dataframe(dane_do_wyswietlenia, use_container_width=True)

            def convert_df_to_excel_z_tabela(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    # 1. Główny arkusz ze wszystkimi wpisami
                    df.to_excel(writer, index=False, sheet_name="Wszystkie_Wpisy")
                    
                    # 2. Tworzenie osobnych arkuszy dla każdej budowy z wierszem SUM na końcu
                    if not df.empty and "Budowa" in df.columns:
                        unikalne_budowy = df["Budowa"].dropna().unique()
                        for budowa in unikalne_budowy:
                            # Filtrujemy wpisy dla danej budowy
                            df_budowa = df[df["Budowa"] == budowa].copy()
                            
                            # Obliczamy sumy dla wymaganych kolumn
                            suma_godz_dojazdu = df_budowa["Czas dojazdu (godz)"].sum() if "Czas dojazdu (godz)" in df_budowa.columns else 0.0
                            suma_godz_pracownikow = df_budowa["Godziny"].sum() if "Godziny" in df_budowa.columns else 0.0
                            suma_koszt_pracy = df_budowa["Koszt pracy (zł)"].sum() if "Koszt pracy (zł)" in df_budowa.columns else 0.0
                            suma_godz_powrotu = df_budowa["Czas powrotu (godz)"].sum() if "Czas powrotu (godz)" in df_budowa.columns else 0.0
                            suma_koszt_powrotu = df_budowa["Koszt powrotu (zł)"].sum() if "Koszt powrotu (zł)" in df_budowa.columns else 0.0
                            suma_razem = df_budowa["Razem (zł)"].sum() if "Razem (zł)" in df_budowa.columns else 0.0
                            
                            # Tworzymy słownik podsumowania dopasowany do struktury kolumn
                            wiersz_sumy = {col: "" for col in df_budowa.columns}
                            
                            # Wypełniamy etykietę oraz wyliczone sumy w odpowiednich kolumnach
                            if "Pracownik" in df_budowa.columns:
                                wiersz_sumy["Pracownik"] = "SUMA"
                            elif "Data" in df_budowa.columns:
                                wiersz_sumy["Data"] = "SUMA"
                            
                            if "Czas dojazdu (godz)" in df_budowa.columns:
                                wiersz_sumy["Czas dojazdu (godz)"] = round(suma_godz_dojazdu, 2)
                            if "Godziny" in df_budowa.columns:
                                wiersz_sumy["Godziny"] = round(suma_godz_pracownikow, 2)
                            if "Koszt pracy (zł)" in df_budowa.columns:
                                wiersz_sumy["Koszt pracy (zł)"] = round(suma_koszt_pracy, 2)
                            if "Czas powrotu (godz)" in df_budowa.columns:
                                wiersz_sumy["Czas powrotu (godz)"] = round(suma_godz_powrotu, 2)
                            if "Koszt powrotu (zł)" in df_budowa.columns:
                                wiersz_sumy["Koszt powrotu (zł)"] = round(suma_koszt_powrotu, 2)
                            if "Razem (zł)" in df_budowa.columns:
                                wiersz_sumy["Razem (zł)"] = round(suma_razem, 2)
                                
                            # Doklejamy wiersz sumy do DataFrame budowy
                            df_budowa_z_suma = pd.concat([df_budowa, pd.DataFrame([wiersz_sumy])], ignore_index=True)
                            
                            # Nazwa arkusza w Excelu może mieć maksymalnie 31 znaków i nie może zawierać niedozwolonych znaków
                            safe_sheet_name = "".join(c for c in str(budowa) if c not in '[]:*?/\\')[:31]
                            df_budowa_z_suma.to_excel(writer, index=False, sheet_name=safe_sheet_name)

                    # Dodatkowa tabela podsumowania kosztów między pracownikami a budowami
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
                nowe_haslo = st.text_input("Hasło do logowania (min. 6 znaków)", type="password")
            with c_n2:
                wybrana_rola = st.selectbox("Uprawnienia", ["Pracownik", "Admin"])
                poczatkowa_stawka = st.number_input("Stawka początkowa (zł/h)", min_value=0.0, value=30.0, step=5.0)
                data_od_stawki = st.date_input("Obowiązuje od daty", value=pd.Timestamp.today().date())

            submit_pracownik = st.form_submit_button("Dodaj pracownika")

            if submit_pracownik:
                if not nowe_imie or not nowy_email or not nowe_haslo:
                    st.warning("Uzupełnij imię, e-mail oraz hasło.")
                elif len(nowe_haslo) < 6:
                    st.error("❌ Hasło musi składać się z co najmniej 6 znaków!")
                elif nowy_email.lower() in df_pracownicy["Email"].str.lower().values:
                    st.error("❌ Ten adres e-mail jest już zajęty przez innego pracownika!")
                else:
                    nowy_wiersz = pd.DataFrame(
                        {
                            "Email": [nowy_email.strip().lower()],
                            "Haslo": [hashuj_haslo(nowe_haslo)],
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
                        nowe_haslo_ed = st.text_input("Nowe hasło (min. 6 znaków, pozostaw puste, jeśli bez zmian)", value="", type="password")
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
                            if nowe_haslo_ed.strip() != "" and len(nowe_haslo_ed) < 6:
                                st.error("❌ Nowe hasło musi składać się z co najmniej 6 znaków!")
                            else:
                                df_pracownicy.loc[df_pracownicy["Pracownik"] == cel, "Pracownik"] = nowe_imie_ed
                                df_pracownicy.loc[df_pracownicy["Pracownik"] == nowe_imie_ed, "Email"] = nowy_email_ed.strip().lower()
                                if nowe_haslo_ed.strip() != "":
                                    df_pracownicy.loc[df_pracownicy["Pracownik"] == nowe_imie_ed, "Haslo"] = hashuj_haslo(nowe_haslo_ed)
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
        
        with st.form("form_dodaj_budowe", clear_on_submit=True):
            nowa_budowa_input = st.text_input("Nazwa budowy lub adres")
            data_rozp_input = st.date_input("Data rozpoczęcia budowy", value=pd.Timestamp.today().date())
            submit_budowa = st.form_submit_button("➕ Dodaj budowę do listy", use_container_width=True)

            if submit_budowa:
                czysta_nazwa = nowa_budowa_input.strip()
                if not czysta_nazwa:
                    st.warning("⚠️ Podaj nazwę budowy.")
                else:
                    sukces = zapisz_budowe(czysta_nazwa, data_rozp_input)
                    if sukces:
                        st.success(f"✅ Dodano nową budowę: {czysta_nazwa} (od {data_rozp_input})")
                        st.rerun()
                    else:
                        st.error("❌ Taka budowa już istnieje na liście.")

        st.markdown("---")
        st.markdown("### Aktualnie aktywne budowy")
        df_budowy_pelne = wczytaj_pelne_dane_budow()

        if "edytowana_budowa" not in st.session_state:
            st.session_state.edytowana_budowa = None

        if not df_budowy_pelne.empty:
            for idx, row in df_budowy_pelne.iterrows():
                b_nazwa = row["Budowa"]
                b_data = row.get("DataRozpoczecia", "Brak")

                with st.container(border=True):
                    col_info_b, col_przyciski_b = st.columns([7.0, 3.0])
                    with col_info_b:
                        st.markdown(f"<b>{b_nazwa}</b><br><small style='color: gray;'>📅 Data rozpoczęcia: {b_data}</small>", unsafe_allow_html=True)
                    with col_przyciski_b:
                        sub_cb1, sub_cb2 = st.columns(2)
                        with sub_cb1:
                            if st.button("✏️", key=f"edit_b_{idx}", help="Edytuj", use_container_width=True):
                                st.session_state.edytowana_budowa = b_nazwa
                                st.rerun()
                        with sub_cb2:
                            if st.button("🗑️", key=f"del_b_{idx}", help="Usuń", use_container_width=True):
                                usun_budowe(b_nazwa)
                                st.success(f"Usunięto budowę: {b_nazwa}")
                                st.rerun()

            if st.session_state.edytowana_budowa:
                st.markdown("---")
                stara_nazwa = st.session_state.edytowana_budowa
                st.markdown(f"### ✏️ Edycja budowy: **{stara_nazwa}**")
                
                akt_wiersz_b = df_budowy_pelne[df_budowy_pelne["Budowa"] == stara_nazwa]
                domyslna_data_ed = pd.to_datetime(akt_wiersz_b.iloc[0]["DataRozpoczecia"]).date() if not akt_wiersz_b.empty else pd.Timestamp.today().date()

                with st.form("form_edycja_budowy"):
                    nowa_nazwa_b = st.text_input("Nowa nazwa budowy / adresu", value=stara_nazwa)
                    nowa_data_b = st.date_input("Data rozpoczęcia", value=domyslna_data_ed)
                    
                    c_zapisz, c_anuluj = st.columns(2)
                    with c_zapisz:
                        btn_zapisz_b = st.form_submit_button("💾 Zapisz", use_container_width=True)
                    with c_anuluj:
                        btn_anuluj_b = st.form_submit_button("❌ Anuluj", use_container_width=True)

                    if btn_zapisz_b:
                        czysta_nowa = nowa_nazwa_b.strip()

                        if not czysta_nowa:
                            st.warning("Nazwa budowy nie może być pusta!")
                        else:
                            sukces_edycji = edytuj_budowe(stara_nazwa, czysta_nowa, nowa_data_b)
                            if sukces_edycji:
                                st.session_state.edytowana_budowa = None
                                st.success("✅ Zaktualizowano budowę pomyślnie!")
                                st.rerun()
                            else:
                                st.error("❌ Budowa o takiej nazwie już istnieje!")

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

                            st.session_state.edytowany_auto = None
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

        data_rozp_budowy_str = pobierz_date_rozpoczecia_budowy(budowa)
        st.info(f"ℹ️ Wybrana budowa (**{budowa}**) rozpoczęła się: **{data_rozp_budowy_str}**")

        czy_dojazd = st.checkbox("🚗 Zgłoś dojazd firmowym autem", key="prac_chk_dojazd")
        dojazd_od, dojazd_do = pd.to_datetime("07:00").time(), pd.to_datetime("08:00").time()
        auto_dojazd = "Brak"
        
        if czy_dojazd:
            if "prac_poprzedni_dojazd" not in st.session_state:
                st.session_state["prac_poprzedni_dojazd"] = False

            col_d1, col_d2 = st.columns(2)
            with col_d1:
                dojazd_od = st.time_input("Dojazd od", value=pd.to_datetime("07:00").time(), key="doj_od")
            with col_d2:
                def aktualizuj_start_pracy():
                    st.session_state["t_od"] = st.session_state["doj_do"]
                dojazd_do = st.time_input("Dojazd do", value=pd.to_datetime("08:00").time(), key="doj_do", on_change=aktualizuj_start_pracy)
            
            auto_dojazd = st.selectbox("Auto na dojazd", lista_aut if lista_aut else ["Brak"], key="auta_d")
            
            if not st.session_state["prac_poprzedni_dojazd"]:
                st.session_state["t_od"] = dojazd_do
                st.session_state["prac_poprzedni_dojazd"] = True
                
            domyslna_praca_od = st.session_state.get("t_od", dojazd_do)
        else:
            st.session_state["prac_poprzedni_dojazd"] = False
            domyslna_praca_od = pd.to_datetime("08:00").time()

        st.markdown("⏱️ **Czas pracy na budowie**")
        
        if "prac_poprzedni_powrot" not in st.session_state:
            st.session_state["prac_poprzedni_powrot"] = False

        col_pr1, col_pr2 = st.columns(2)
        with col_pr1:
            godzina_od = st.time_input("Godzina od", value=domyslna_praca_od, key="t_od")
        with col_pr2:
            domyslny_koniec_pracy = (pd.Timestamp(f"2026-01-01 {godzina_od}") + pd.Timedelta(hours=8)).time()
            
            def aktualizuj_start_powrotu():
                st.session_state["pow_od"] = st.session_state["t_do"]
                st.session_state["prac_poprzedni_powrot"] = True

            godzina_do = st.time_input("Godzina do", value=domyslny_koniec_pracy, key="t_do", on_change=aktualizuj_start_powrotu)

        czy_powrot = st.checkbox("🏠 Zgłoś powrót firmowym autem", key="prac_chk_powrot")
        powrot_od, powrot_do = pd.to_datetime("16:00").time(), pd.to_datetime("17:00").time()
        auto_powrot = "Brak"
        
        if czy_powrot:
            if not st.session_state["prac_poprzedni_powrot"]:
                st.session_state["pow_od"] = godzina_do
                st.session_state["prac_poprzedni_powrot"] = True

            domyslny_powrot_od = st.session_state.get("pow_od", godzina_do)

            col_p1, col_p2 = st.columns(2)
            with col_p1:
                powrot_od = st.time_input("Powrót od", value=domyslny_powrot_od, key="pow_od")
            with col_p2:
                domyslny_powrot_do = (pd.Timestamp(f"2026-01-01 {domyslny_powrot_od}") + pd.Timedelta(hours=1)).time()
                powrot_do = st.time_input("Powrót do", value=domyslny_powrot_do, key="pow_do")
            auto_powrot = st.selectbox("Auto na powrót", lista_aut if lista_aut else ["Brak"], key="auta_p")
        else:
            st.session_state["prac_poprzedni_powrot"] = False

        if st.button("💾 Zapisz wpis", use_container_width=True, type="primary"):
            data_rozp_budowy_dt = pd.to_datetime(data_rozp_budowy_str).date()

            start_dt = pd.to_datetime(f"{data} {godzina_od}")
            koniec_dt = pd.to_datetime(f"{data} {godzina_do}")
            
            dojazd_start_dt = pd.to_datetime(f"{data} {dojazd_od}") if czy_dojazd else start_dt
            dojazd_koniec_dt = pd.to_datetime(f"{data} {dojazd_do}") if czy_dojazd else start_dt
            
            powrot_start_dt = pd.to_datetime(f"{data} {powrot_od}") if czy_powrot else koniec_dt
            powrot_koniec_dt = pd.to_datetime(f"{data} {powrot_do}") if czy_powrot else koniec_dt

            if data < data_rozp_budowy_dt:
                st.error(f"❌ Błąd: Data wpisu ({data}) jest wcześniejsza niż data rozpoczęcia budowy ({data_rozp_budowy_str})!")
            elif koniec_dt <= start_dt:
                st.error("❌ Błąd: Godzina zakończenia pracy musi być późniejsza niż rozpoczęcia!")
            elif czy_dojazd and dojazd_koniec_dt < dojazd_start_dt:
                st.error("❌ Błąd: Godzina zakończenia dojazdu musi być późniejsza lub równa rozpoczęciu!")
            elif czy_dojazd and auto_dojazd == "Brak":
                st.error("❌ Błąd: Wybierz auto na dojazd!")
            elif czy_powrot and powrot_koniec_dt < powrot_start_dt:
                st.error("❌ Błąd: Godzina zakończenia powrotu musi być późniejsza lub równa rozpoczęciu!")
            elif czy_powrot and auto_powrot == "Brak":
                st.error("❌ Błąd: Wybierz auto na powrót!")
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
                    st.error("❌ Masz już inny wpis pokrywający się z tymi godzinami w tym dniu!")
                elif konflikt_auta_d:
                    st.error(f"❌ Wybrany pojazd dojazdu ({auto_dojazd}) jest zajęty w tym przedziale czasowym!")
                elif konflikt_auta_p:
                    st.error(f"❌ Wybrany pojazd powrotu ({auto_powrot}) jest zajęty w tym przedziale czasowym!")
                else:
                    roznica_czasu = (koniec_dt - start_dt).total_seconds() / 3600
                    roznica_dojazdu = (dojazd_koniec_dt - dojazd_start_dt).total_seconds() / 3600 if czy_dojazd else 0.0
                    roznica_powrotu = (powrot_koniec_dt - powrot_start_dt).total_seconds() / 3600 if czy_powrot else 0.0

                    stawka_aktualna = pobierz_stawke_pracownika(zalogowany_pracownik, str(data))

                    koszt_pracy = roznica_czasu * stawka_aktualna
                    stawka_dojazdu = stawka_aktualna / 2.0
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
                        "Stawka (zł/h)": stawka_aktualna,
                        "Godziny": round(roznica_czasu, 2),
                        "Koszt pracy (zł)": round(koszt_pracy, 2),
                        "Koszt dojazdu (zł)": round(koszt_dojazdu_zl, 2),
                        "Powrót Od": str(powrot_od) if czy_powrot else "00:00",
                        "Powrót Do": str(powrot_do) if czy_powrot else "00:00",
                        "Czas powrotu (godz)": round(roznica_powrotu, 2),
                        "Nr Rejestracyjny Powrót": auto_powrot if czy_powrot else "Brak",
                        "Koszt powrotu (zł)": round(koszt_powrotu_zl, 2),
                        "Razem (zł)": round(razem, 2),
                        "Zatwierdzone": "Nie"
                    }

                    AktualneDane = pd.concat([AktualneDane, pd.DataFrame([nowy_wpis])], ignore_index=True)
                    zapisz_dane(AktualneDane)
                    st.success("✅ Pomyślnie dodano wpis czasu pracy!")
                    st.rerun()

    st.markdown("---")
    st.subheader("Moje wpisy")
    
    if "edytowany_moj_wpis_id" not in st.session_state:
        st.session_state.edytowany_moj_wpis_id = None

    # Obsługa formularza edycji własnego wpisu przez pracownika
    if st.session_state.edytowany_moj_wpis_id is not None:
        e_m_id = st.session_state.edytowany_moj_wpis_id
        if e_m_id in dane_systemowe.index:
            w_ed_moj = dane_systemowe.loc[e_m_id]
            
            if str(w_ed_moj.get("Zatwierdzone", "Nie")) == "Tak":
                st.warning("⚠️ Ten wpis został już zatwierdzony przez administratora i nie możesz go edytować.")
                st.session_state.edytowany_moj_wpis_id = None
                st.rerun()

            st.markdown(f"#### ✏️ Edycja Twojego wpisu z dnia `{w_ed_moj['Data']}`")

            with st.form(f"form_edycja_mojego_wpisu_{e_m_id}"):
                em_data = st.date_input("Data wpisu", value=pd.to_datetime(w_ed_moj['Data']).date())
                em_budowa = st.selectbox("Budowa", lista_budow, index=lista_budow.index(w_ed_moj['Budowa']) if w_ed_moj['Budowa'] in lista_budow else 0)

                em_akt_auto_d = w_ed_moj.get("Nr Rejestracyjny", "Brak")
                em_czy_byl_dojazd = em_akt_auto_d != "Brak" and pd.notna(em_akt_auto_d)
                em_czy_doj = st.checkbox("🚗 Dojazd firmowym autem", value=em_czy_byl_dojazd)
                
                em_d_od_val = pd.to_datetime(w_ed_moj.get("Dojazd Od", "07:00")).time() if em_czy_byl_dojazd else pd.to_datetime("07:00").time()
                em_d_do_val = pd.to_datetime(w_ed_moj.get("Dojazd Do", "08:00")).time() if em_czy_byl_dojazd else pd.to_datetime("08:00").time()
                
                col_em1, col_em2 = st.columns(2)
                with col_em1:
                    em_doj_od = st.time_input("Dojazd od", value=em_d_od_val)
                with col_em2:
                    em_doj_do = st.time_input("Dojazd do", value=em_d_do_val)
                em_auto_d = st.selectbox("Auto na dojazd", ["Brak"] + lista_aut, index=(["Brak"] + lista_aut).index(em_akt_auto_d) if em_akt_auto_d in (["Brak"] + lista_aut) else 0)

                st.markdown("⏱️ **Czas pracy na budowie**")
                em_p_od_val = pd.to_datetime(w_ed_moj.get("Od", "08:00")).time()
                em_p_do_val = pd.to_datetime(w_ed_moj.get("Do", "16:00")).time()
                
                col_em3, col_em4 = st.columns(2)
                with col_em3:
                    em_praca_od = st.time_input("Praca od", value=em_p_od_val)
                with col_em4:
                    em_praca_do = st.time_input("Praca do", value=em_p_do_val)

                em_akt_auto_p = w_ed_moj.get("Nr Rejestracyjny Powrót", "Brak")
                em_czy_byl_powrot = em_akt_auto_p != "Brak" and pd.notna(em_akt_auto_p)
                em_czy_pow = st.checkbox("🏠 Powrót firmowym autem", value=em_czy_byl_powrot)

                em_pow_od_val = pd.to_datetime(w_ed_moj.get("Powrót Od", "16:00")).time() if em_czy_byl_powrot else pd.to_datetime("16:00").time()
                em_pow_do_val = pd.to_datetime(w_ed_moj.get("Powrót Do", "17:00")).time() if em_czy_byl_powrot else pd.to_datetime("17:00").time()

                col_em5, col_em6 = st.columns(2)
                with col_em5:
                    em_pow_od = st.time_input("Powrót od", value=em_pow_od_val)
                with col_em6:
                    em_pow_do = st.time_input("Powrót do", value=em_pow_do_val)
                em_auto_p = st.selectbox("Auto na powrót", ["Brak"] + lista_aut, index=(["Brak"] + lista_aut).index(em_akt_auto_p) if em_akt_auto_p in (["Brak"] + lista_aut) else 0)

                col_emz1, col_emz2 = st.columns(2)
                with col_emz1:
                    submit_zapisz_moj = st.form_submit_button("💾 Zapisz zmiany", use_container_width=True, type="primary")
                with col_emz2:
                    submit_anuluj_moj = st.form_submit_button("❌ Anuluj", use_container_width=True)

                if submit_zapisz_moj:
                    data_rozp_budowy_str = pobierz_date_rozpoczecia_budowy(em_budowa)
                    data_rozp_dt = pd.to_datetime(data_rozp_budowy_str).date()

                    start_dt = pd.to_datetime(f"{em_data} {em_praca_od}")
                    koniec_dt = pd.to_datetime(f"{em_data} {em_praca_do}")
                    
                    dojazd_start_dt = pd.to_datetime(f"{em_data} {em_doj_od}") if em_czy_doj else start_dt
                    dojazd_koniec_dt = pd.to_datetime(f"{em_data} {em_doj_do}") if em_czy_doj else start_dt
                    
                    powrot_start_dt = pd.to_datetime(f"{em_data} {em_pow_od}") if em_czy_pow else koniec_dt
                    powrot_koniec_dt = pd.to_datetime(f"{em_data} {em_pow_do}") if em_czy_pow else koniec_dt

                    auto_d_val = em_auto_d if em_czy_doj else "Brak"
                    auto_p_val = em_auto_p if em_czy_pow else "Brak"

                    if em_data < data_rozp_dt:
                        st.error(f"❌ Błąd: Data wpisu ({em_data}) jest wcześniejsza niż data rozpoczęcia budowy ({data_rozp_dt})!")
                    elif koniec_dt <= start_dt:
                        st.error("Błąd: Godzina zakończenia pracy musi być późniejsza niż rozpoczęcia!")
                    elif em_czy_doj and dojazd_koniec_dt < dojazd_start_dt:
                        st.error("Błąd: Godzina zakończenia dojazdu musi być późniejsza lub równa rozpoczęciu!")
                    elif em_czy_doj and auto_d_val == "Brak":
                        st.error("Błąd: Wybierz auto na dojazd!")
                    elif em_czy_pow and powrot_koniec_dt < powrot_start_dt:
                        st.error("Błąd: Godzina zakończenia powrotu musi być późniejsza lub równa rozpoczęciu!")
                    elif em_czy_pow and auto_p_val == "Brak":
                        st.error("Błąd: Wybierz auto na powrót!")
                    else:
                        AktDane = wczytaj_dane()
                        konflikt_pracownika = sprawdz_konflikt_czasowy(
                            AktDane, zalogowany_pracownik, str(em_data), 
                            dojazd_start_dt, dojazd_koniec_dt, start_dt, koniec_dt,
                            powrot_start_dt, powrot_koniec_dt, em_czy_doj, em_czy_pow, pomijany_index=e_m_id
                        )
                        konflikt_auta_d = sprawdz_konflikt_pojazdu_dojazd(
                            AktDane, auto_d_val, str(em_data), dojazd_start_dt, dojazd_koniec_dt, em_czy_doj, pomijany_index=e_m_id
                        )
                        konflikt_auta_p = sprawdz_konflikt_pojazdu_powrot(
                            AktDane, auto_p_val, str(em_data), powrot_start_dt, powrot_koniec_dt, em_czy_pow, pomijany_index=e_m_id
                        )

                        if konflikt_pracownika:
                            st.error("❌ Wybrane godziny kolidują z innym Twoim wpisem w tym dniu!")
                        elif konflikt_auta_d:
                            st.error(f"❌ Pojazd dojazdu ({auto_d_val}) jest zajęty w tym przedziale czasowym!")
                        elif konflikt_auta_p:
                            st.error(f"❌ Pojazd powrotu ({auto_p_val}) jest zajęty w tym przedziale czasowym!")
                        else:
                            roznica_czasu = (koniec_dt - start_dt).total_seconds() / 3600
                            roznica_dojazdu = (dojazd_koniec_dt - dojazd_start_dt).total_seconds() / 3600 if em_czy_doj else 0.0
                            roznica_powrotu = (powrot_koniec_dt - powrot_start_dt).total_seconds() / 3600 if em_czy_pow else 0.0

                            stawka_wybranego = pobierz_stawke_pracownika(zalogowany_pracownik, str(em_data))

                            koszt_pracy = roznica_czasu * stawka_wybranego
                            stawka_dojazdu = stawka_wybranego / 2.0
                            koszt_dojazdu_zl = roznica_dojazdu * stawka_dojazdu if em_czy_doj else 0.0
                            koszt_powrotu_zl = roznica_powrotu * stawka_dojazdu if em_czy_pow else 0.0
                            razem = koszt_pracy + koszt_dojazdu_zl + koszt_powrotu_zl

                            AktDane.loc[e_m_id, "Data"] = str(em_data)
                            AktDane.loc[e_m_id, "Budowa"] = em_budowa
                            AktDane.loc[e_m_id, "Nr Rejestracyjny"] = auto_d_val
                            AktDane.loc[e_m_id, "Dojazd Od"] = str(em_doj_od) if em_czy_doj else "00:00"
                            AktDane.loc[e_m_id, "Dojazd Do"] = str(em_doj_do) if em_czy_doj else "00:00"
                            AktDane.loc[e_m_id, "Czas dojazdu (godz)"] = round(roznica_dojazdu, 2)
                            AktDane.loc[e_m_id, "Od"] = str(em_praca_od)
                            AktDane.loc[e_m_id, "Do"] = str(em_praca_do)
                            AktDane.loc[e_m_id, "Stawka (zł/h)"] = stawka_wybranego
                            AktDane.loc[e_m_id, "Godziny"] = round(roznica_czasu, 2)
                            AktDane.loc[e_m_id, "Koszt pracy (zł)"] = round(koszt_pracy, 2)
                            AktDane.loc[e_m_id, "Koszt dojazdu (zł)"] = round(koszt_dojazdu_zl, 2)
                            AktDane.loc[e_m_id, "Powrót Od"] = str(em_pow_od) if em_czy_pow else "00:00"
                            AktDane.loc[e_m_id, "Powrót Do"] = str(em_pow_do) if em_czy_pow else "00:00"
                            AktDane.loc[e_m_id, "Czas powrotu (godz)"] = round(roznica_powrotu, 2)
                            AktDane.loc[e_m_id, "Nr Rejestracyjny Powrót"] = auto_p_val
                            AktDane.loc[e_m_id, "Koszt powrotu (zł)"] = round(koszt_powrotu_zl, 2)
                            AktDane.loc[e_m_id, "Razem (zł)"] = round(razem, 2)

                            zapisz_dane(AktDane)
                            st.session_state.edytowany_moj_wpis_id = None
                            st.success("✅ Pomyślnie zaktualizowano wpis!")
                            st.rerun()

                if submit_anuluj_moj:
                    st.session_state.edytowany_moj_wpis_id = None
                    st.rerun()
        else:
            st.session_state.edytowany_moj_wpis_id = None

    moje_dane = dane_systemowe[dane_systemowe["Pracownik"] == zalogowany_pracownik]

    # --- PODSUMOWANIE CZASU PRACY PRACOWNIKA ---
    # Pokazujemy wyłącznie dane dotyczące czasu. Stawki i koszty pozostają niewidoczne dla pracownika.
    if not moje_dane.empty:
        suma_godzin_pracy = pd.to_numeric(
            moje_dane.get("Godziny", pd.Series(dtype=float)), errors="coerce"
        ).fillna(0).sum()
        suma_czasu_dojazdu = pd.to_numeric(
            moje_dane.get("Czas dojazdu (godz)", pd.Series(dtype=float)), errors="coerce"
        ).fillna(0).sum()
        suma_czasu_powrotu = pd.to_numeric(
            moje_dane.get("Czas powrotu (godz)", pd.Series(dtype=float)), errors="coerce"
        ).fillna(0).sum()
        suma_lacznego_czasu = suma_godzin_pracy + suma_czasu_dojazdu + suma_czasu_powrotu

        st.markdown("### 📊 Moje podsumowanie czasu")
        pod1, pod2, pod3, pod4 = st.columns(4)
        pod1.metric("⏱️ Przepracowane", f"{suma_godzin_pracy:.2f} h")
        pod2.metric("🚗 Dojazdy", f"{suma_czasu_dojazdu:.2f} h")
        pod3.metric("🏠 Powroty", f"{suma_czasu_powrotu:.2f} h")
        pod4.metric("🕐 Łącznie", f"{suma_lacznego_czasu:.2f} h")

        st.caption(
            "Podsumowanie obejmuje wszystkie Twoje zapisane wpisy i jest aktualizowane automatycznie po dodaniu lub edycji wpisu."
        )
        st.markdown("---")

    if not moje_dane.empty:
        # --- PRZYCISK EKSPORTU DLA PRACOWNIKA (BEZ STAWEK I KOSZTÓW) ---
        def generuj_excel_pracownika(df_prac):
            output = BytesIO()
            # Usuwamy kolumny ze stawkami oraz kosztami
            kolumny_do_odrzucenia = ["Stawka (zł/h)", "Koszt pracy (zł)", "Koszt dojazdu (zł)", "Koszt powrotu (zł)", "Razem (zł)"]
            df_czyste = df_prac.drop(columns=[k for k in kolumny_do_odrzucenia if k in df_prac.columns], errors="ignore")
            
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df_czyste.to_excel(writer, index=False, sheet_name="Moje_Wpisy")
            return output.getvalue()

        excel_pracownika_data = generuj_excel_pracownika(moje_dane)
        st.download_button(
            label="📥 Pobierz moje wpisy do Excela (.xlsx)",
            data=excel_pracownika_data,
            file_name=f"moje_wpisy_{zalogowany_pracownik.lower().replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        st.markdown("---")

        for idx, row in moje_dane.iterrows():
            status_zatw = row.get("Zatwierdzone", "Nie")
            status_badge = "🟢 **Zatwierdzone**" if status_zatw == "Tak" else "🟠 **Oczekuje na zatwierdzenie**"
            
            with st.container(border=True):
                col_m1, col_m2 = st.columns([7.5, 2.5])
                with col_m1:
                    st.markdown(
                        f"📅 `{row['Data']}` | 🏗️ `{row['Budowa']}` | {status_badge}\n"
                        f"⏱️ Praca: `{row['Od']} - {row['Do']}` (**{row['Godziny']}h**)\n"
                        f"🚗 Dojazd: `{row['Nr Rejestracyjny']}` | 🏠 Powrót: `{row['Nr Rejestracyjny Powrót']}`"
                    )
                with col_m2:
                    sub_m1, sub_m2 = st.columns(2)
                    with sub_m1:
                        if status_zatw == "Tak":
                            st.button("🔒", key=f"edit_lock_moj_{idx}", help="Edycja zablokowana (wpis zatwierdzony)", use_container_width=True, disabled=True)
                        else:
                            if st.button("✏️", key=f"edit_moj_{idx}", help="Edytuj wpis", use_container_width=True):
                                st.session_state.edytowany_moj_wpis_id = idx
                                st.rerun()
                    with sub_m2:
                        if status_zatw == "Tak":
                            st.button("🔒", key=f"del_lock_moj_{idx}", help="Usuwanie zablokowane (wpis zatwierdzony)", use_container_width=True, disabled=True)
                        else:
                            if st.button("🗑️", key=f"del_moj_{idx}", help="Usuń wpis", use_container_width=True):
                                nowe_dane = dane_systemowe.drop(idx)
                                zapisz_dane(nowe_dane)
                                st.success("Usunięto wpis!")
                                st.rerun()
    else:
        st.info("Brak Twoich wpisów w systemie.")
