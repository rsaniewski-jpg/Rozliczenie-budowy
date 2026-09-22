import os
from PIL import Image
import pandas as pd
import streamlit as st

# Ścieżka do favicony (małe logo) oraz pełnego logo w folderze "loga"
sciezka_favicony = os.path.join("loga", "logo.png")
sciezka_pelne_logo = os.path.join("loga", "logo_pelne.png")

if os.path.exists(sciezka_favicony):
    ikonka = Image.open(sciezka_favicony)
else:
    ikonka = "🏗️"  # Awaryjna ikona tekstowa

st.set_page_config(
    page_title="Rozliczanie Kosztów Budowy", page_icon=ikonka, layout="centered"
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
    /* Wyraźniejsze wyszarzenie tła kontenerów z budowami */
    [data-testid="stContainer"] {
        background-color: #e9ecef;
        border-radius: 8px;
        padding: 4px;
    }
    /* Ukrycie napisu "Press enter to apply" pod polami */
    [data-testid="InputInstructions"] {
        display: none;
    }
    /* Zwiększenie szerokości głównego kontenera, aby długi tytuł mieścił się w jednej linii */
    .block-container {
        max-width: 920px !important;
    }
    /* Zablokowanie / ustalenie stałej szerokości lewego paska bocznego */
    [data-testid="stSidebar"] {
        min-width: 320px !important;
        max-width: 320px !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Pliki do trwałego przechowywania danych
PLIK_BAZY = "baza_danych.csv"
PLIK_PRACOWNICY = "baza_pracownikow.csv"
PLIK_STAWKI = "baza_stawek.csv"
PLIK_BUDOWY = "baza_budow.csv"


# --- FUNKCJE POMOCNICZE DLA BAZ ---
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
        return pd.read_csv(PLIK_BAZY)
    else:
        return pd.DataFrame(
            columns=[
                "Pracownik",
                "Data",
                "Budowa",
                "Dojazd Od",
                "Dojazd Do",
                "Czas dojazdu (godz)",
                "Od",
                "Do",
                "Stawka (zł/h)",
                "Godziny",
                "Koszt pracy (zł)",
                "Koszt dojazdu (zł)",
                "Razem (zł)",
            ]
        )


def zapisz_dane(df):
    df.to_csv(PLIK_BAZY, index=False)


# --- STAN SESJI ---
if "zalogowany" not in st.session_state:
    st.session_state.zalogowany = False
    st.session_state.aktualny_pracownik = None
    st.session_state.rola = None

st.title("🏗️ System Rozliczania Czasu Pracy na Budowach")

# --- WYŚWIETLANIE PEŁNEGO LOGO NA SAMEJ GÓRZE PANELU BOCZNEGO ---
if os.path.exists(sciezka_pelne_logo):
    st.sidebar.image(sciezka_pelne_logo, use_container_width=True)
    st.sidebar.markdown("---")

# --- PANEL LOGOWANIA / UŻYTKOWNIKA ---
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
        "👈 Wpisz swój adres e-mail oraz hasło w panelu po lewej stronie i wciśnij **Enter** (lub kliknij 'Zaloguj się')."
        
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


# --- PANEL ADMINISTRATORA ---
if rola_uzytkownika == "Admin":
    st.subheader("👑 Panel Administratora")

    if "menu_admin" not in st.session_state:
        st.session_state.menu_admin = "📊 Raport wszystkich wpisów"

    col_btn1, col_btn2, col_btn3 = st.columns(3)

    with col_btn1:
        if st.button(
            "📊 Raport wpisów i dopisywanie",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.menu_admin == "📊 Raport wszystkich wpisów"
                else "secondary"
            ),
        ):
            st.session_state.menu_admin = "📊 Raport wszystkich wpisów"
            st.rerun()

    with col_btn2:
        if st.button(
            "👥 Pracownicy",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.menu_admin == "👥 Zarządzanie Pracownikami"
                else "secondary"
            ),
        ):
            st.session_state.menu_admin = "👥 Zarządzanie Pracownikami"
            st.rerun()

    with col_btn3:
        if st.button(
            "🏗️ Budowy",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.menu_admin == "🏗️ Zarządzanie Budowami"
                else "secondary"
            ),
        ):
            st.session_state.menu_admin = "🏗️ Zarządzanie Budowami"
            st.rerun()

    st.markdown("---")

    menu_admin = st.session_state.menu_admin

    if menu_admin == "📊 Raport wszystkich wpisów":
        st.markdown("### Raport godzin i kosztów całej firmy")

        # --- SEKCJA DOPISYWANIA GODZIN W GÓRNEJ CZĘŚCI RAPORTU ---
        with st.expander("➕ Dopisz godziny dla pracownika (kliknij, aby rozwinąć)"):
            df_pracownicy_adm = wczytaj_pracownikow()
            lista_pracownikow_nazwy = df_pracownicy_adm["Pracownik"].tolist()

            if not lista_pracownikow_nazwy:
                st.error("Brak pracowników w systemie.")
            elif not lista_budow:
                st.error("Brak dostępnych budów w systemie.")
            else:
                with st.form("form_admin_dopisz_godziny", clear_on_submit=True):
                    wybrany_pracownik_adm = st.selectbox("Wybierz pracownika", lista_pracownikow_nazwy)
                    data_adm = st.date_input("Data wpisu", value=pd.Timestamp.today().date())
                    budowa_adm = st.selectbox("Wybierz budowę", lista_budow)

                    st.markdown("🚗 **Czas dojazdu** (50% stawki)")
                    col_da1, col_da2 = st.columns(2)
                    with col_da1:
                        dojazd_od_adm = st.time_input("Dojazd od", value=pd.to_datetime("07:00").time())
                    with col_da2:
                        dojazd_do_adm = st.time_input("Dojazd do", value=pd.to_datetime("08:00").time())

                    st.markdown("⏱️ **Czas pracy na budowie** (pełna stawka)")
                    col_pa1, col_pa2 = st.columns(2)
                    with col_pa1:
                        godzina_od_adm = st.time_input("Godzina od", value=pd.to_datetime("08:00").time())
                    with col_pa2:
                        godzina_do_adm = st.time_input("Godzina do", value=pd.to_datetime("16:00").time())

                    submit_adm_wpis = st.form_submit_button("💾 Dodaj ten wpis dla pracownika")

                    if submit_adm_wpis:
                        dojazd_start_dt = pd.to_datetime(f"{data_adm} {dojazd_od_adm}")
                        dojazd_koniec_dt = pd.to_datetime(f"{data_adm} {dojazd_do_adm}")
                        start_dt = pd.to_datetime(f"{data_adm} {godzina_od_adm}")
                        koniec_dt = pd.to_datetime(f"{data_adm} {godzina_do_adm}")

                        if dojazd_koniec_dt < dojazd_start_dt:
                            st.error("Błąd: Godzina zakończenia dojazdu musi być późniejsza lub równa rozpoczęciu!")
                        elif koniec_dt <= start_dt:
                            st.error("Błąd: Godzina zakończenia pracy musi być późniejsza niż rozpoczęcia!")
                        else:
                            # --- SPRAWDZENIE KONFLIKTU GODZIN DLA ADMINA ---
                            konflikt = False
                            AktualneDane = wczytaj_dane()

                            if not AktualneDane.empty:
                                istniejace = AktualneDane[
                                    (AktualneDane["Pracownik"] == wybrany_pracownik_adm)
                                    & (AktualneDane["Data"] == str(data_adm))
                                ]

                                for _, row in istniejace.iterrows():
                                    ist_dojazd_start = pd.to_datetime(
                                        f"{row['Data']} {row['Dojazd Od']}"
                                    )
                                    ist_praca_koniec = pd.to_datetime(f"{row['Data']} {row['Do']}")

                                    if max(dojazd_start_dt, ist_dojazd_start) < min(
                                        koniec_dt, ist_praca_koniec
                                    ):
                                        konflikt = True
                                        break

                            if konflikt:
                                st.error(
                                    f"❌ Błąd: Te godziny (dojazd lub praca) pokrywają się z innym wpisem "
                                    f"pracownika **{wybrany_pracownik_adm}** w tym dniu!"
                                )
                            else:
                                roznica_dojazdu = (dojazd_koniec_dt - dojazd_start_dt).total_seconds() / 3600
                                roznica_czasu = (koniec_dt - start_dt).total_seconds() / 3600

                                stawka_wybranego = pobierz_stawke_pracownika(wybrany_pracownik_adm, str(data_adm))

                                koszt_pracy = roznica_czasu * stawka_wybranego
                                stawka_dojazdu = stawka_wybranego / 2.0
                                koszt_dojazdu_zl = roznica_dojazdu * stawka_dojazdu
                                razem = koszt_pracy + koszt_dojazdu_zl

                                nowy_wpis_adm = {
                                    "Pracownik": wybrany_pracownik_adm,
                                    "Data": str(data_adm),
                                    "Budowa": budowa_adm,
                                    "Dojazd Od": str(dojazd_od_adm),
                                    "Dojazd Do": str(dojazd_do_adm),
                                    "Czas dojazdu (godz)": round(roznica_dojazdu, 2),
                                    "Od": str(godzina_od_adm),
                                    "Do": str(godzina_do_adm),
                                    "Stawka (zł/h)": stawka_wybranego,
                                    "Godziny": round(roznica_czasu, 2),
                                    "Koszt pracy (zł)": round(koszt_pracy, 2),
                                    "Koszt dojazdu (zł)": round(koszt_dojazdu_zl, 2),
                                    "Razem (zł)": round(razem, 2),
                                }

                                AktualneDane = pd.concat([AktualneDane, pd.DataFrame([nowy_wpis_adm])], ignore_index=True)
                                zapisz_dane(AktualneDane)
                                st.success(
                                    f"✅ Pomyślnie dopisano godziny dla pracownika: **{wybrany_pracownik_adm}** "
                                    f"(Stawka z dnia {data_adm}: {stawka_wybranego} zł/h)"
                                )
                                st.rerun()

        st.markdown("---")

        dane_systemowe = wczytaj_dane()
        if not dane_systemowe.empty:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Łączne godziny", f"{dane_systemowe['Godziny'].sum():.2f} h")
            c2.metric(
                "Koszt pracy", f"{dane_systemowe['Koszt pracy (zł)'].sum():.2f} zł"
            )
            c3.metric(
                "Koszt dojazdu", f"{dane_systemowe['Koszt dojazdu (zł)'].sum():.2f} zł"
            )
            c4.metric("Łączny koszt", f"{dane_systemowe['Razem (zł)'].sum():.2f} zł")
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

                        tabela_godzin = df.pivot_table(
                            values="Godziny", 
                            index="Budowa", 
                            columns="Pracownik", 
                            aggfunc="sum", 
                            fill_value=0.0
                        )
                        tabela_godzin.to_excel(writer, sheet_name="Podsumowanie_Godzin")

                return output.getvalue()

            excel_data = convert_df_to_excel_z_tabela(dane_systemowe)
            
            st.download_button(
                label="📥 Pobierz zaawansowany raport Excel (Budowy x Pracownicy) (.xlsx)",
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
                poczatkowa_stawka = st.number_input(
                    "Stawka początkowa (zł/h)", min_value=0.0, value=30.0, step=5.0
                )
                data_od_stawki = st.date_input(
                    "Obowiązuje od daty", value=pd.Timestamp.today().date()
                )

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
                    df_pracownicy = pd.concat(
                        [df_pracownicy, nowy_wiersz], ignore_index=True
                    )
                    zapisz_pracownikow(df_pracownicy)
                    dodaj_stawke_dla_pracownika(
                        nowe_imie, poczatkowa_stawka, data_od_stawki
                    )
                    st.success(f"✅ Pomyślnie dodano pracownika: {nowe_imie}")
                    st.rerun()

        st.markdown("---")
        st.markdown(
            "### 📋 Lista pracowników (Edycja profilu i dodawanie podwyżek)"
        )

        df_pracownicy = wczytaj_pracownikow()

        if "edytowany_pracownik" not in st.session_state:
            st.session_state.edytowany_pracownik = None

        if not df_pracownicy.empty:
            for idx, row in df_pracownicy.iterrows():
                p_imie = row["Pracownik"]
                p_email = row.get("Email", "Brak")
                p_rola = row.get("Rola", "Pracownik")
                aktualna_s = pobierz_stawke_pracownika(p_imie, None)

                col_info, col_edit, col_del = st.columns([3, 1, 1])

                with col_info:
                    st.write(
                        f"👤 **{p_imie}** (`{p_email}`) | Rola: `{p_rola}` | Akt. stawka:"
                        f" `{aktualna_s} zł/h`"
                    )

                with col_edit:
                    if st.button("✏️ Edytuj / Zmień stawkę", key=f"edit_p_{idx}"):
                        st.session_state.edytowany_pracownik = p_imie
                        st.rerun()

                with col_del:
                    if st.button("🗑️ Usuń", key=f"del_p_{idx}"):
                        if p_imie == zalogowany_pracownik:
                            st.error("Nie możesz usunąć samego siebie!")
                        else:
                            df_pracownicy = df_pracownicy[
                                df_pracownicy["Pracownik"] != p_imie
                            ]
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
                        nowe_imie_ed = st.text_input(
                            "Imię i nazwisko", value=akt_wiersz["Pracownik"]
                        )
                        nowy_email_ed = st.text_input(
                            "Adres e-mail", value=akt_wiersz.get("Email", "")
                        )
                        nowe_haslo_ed = st.text_input(
                            "Hasło", value=akt_wiersz.get("Haslo", ""), type="password"
                        )
                        idx_r = 0 if str(akt_wiersz["Rola"]) == "Pracownik" else 1
                        nowa_rola_ed = st.selectbox(
                            "Uprawnienia", ["Pracownik", "Admin"], index=idx_r
                        )

                        st.markdown("---")
                        st.markdown(
                            "💰 **Nowa stawka godzinowa (podwyżka / zmiana z datą)**"
                        )
                        ostatnia_s = pobierz_stawke_pracownika(cel, None)
                        nowa_stawka_ed = st.number_input(
                            "Stawka (zł/h)", min_value=0.0, value=ostatnia_s, step=5.0
                        )
                        data_od_nowej = st.date_input(
                            "Obowiązuje od daty", value=pd.Timestamp.today().date()
                        )

                        col_zapisz, col_anuluj = st.columns(2)
                        with col_zapisz:
                            btn_zapisz_zmiany = st.form_submit_button(
                                "💾 Zapisz zmiany", use_container_width=True
                            )
                        with col_anuluj:
                            btn_anuluj = st.form_submit_button(
                                "❌ Anuluj", use_container_width=True
                            )

                        if btn_zapisz_zmiany:
                            df_pracownicy.loc[
                                df_pracownicy["Pracownik"] == cel, "Pracownik"
                            ] = nowe_imie_ed
                            df_pracownicy.loc[
                                df_pracownicy["Pracownik"] == nowe_imie_ed, "Email"
                            ] = nowy_email_ed.strip().lower()
                            df_pracownicy.loc[
                                df_pracownicy["Pracownik"] == nowe_imie_ed, "Haslo"
                            ] = nowe_haslo_ed
                            df_pracownicy.loc[
                                df_pracownicy["Pracownik"] == nowe_imie_ed, "Rola"
                            ] = nowa_rola_ed
                            zapisz_pracownikow(df_pracownicy)

                            if nowa_stawka_ed != ostatnia_s:
                                dodaj_stawke_dla_pracownika(
                                    nowe_imie_ed, nowa_stawka_ed, data_od_nowej
                                )

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

        nowa_budowa_input = st.text_input(
            "Nazwa budowy lub adres", key="input_nowa_budowa"
        )

        if st.button("➕ Dodaj budowę do listy"):
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
        st.markdown("### Aktualnie aktywne budowy (Edycja i Usuwanie)")
        aktualne_b = wczytaj_budowy()

        if "edytowana_budowa" not in st.session_state:
            st.session_state.edytowana_budowa = None

        if aktualne_b:
            for b in aktualne_b:
                with st.container(border=True):
                    col_tekst, col_edit, col_del = st.columns([3, 1, 1])
                    with col_tekst:
                        st.markdown(
                            f"<div style='display: flex; align-items: center; height: 38px;'><b>{b}</b></div>",
                            unsafe_allow_html=True
                        )
                    with col_edit:
                        if st.button("✏️ Edytuj", key=f"edit_b_{b}", use_container_width=True):
                            st.session_state.edytowana_budowa = b
                            st.rerun()
                    with col_del:
                        if st.button("🗑️ Usuń", key=f"del_{b}", use_container_width=True):
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
                        btn_zapisz_b = st.form_submit_button("💾 Zapisz zmianę", use_container_width=True)
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

else:
    # --- PANEL DLA ZWYKŁEGO PRACOWNIKA ---
    st.subheader(f"Witaj, {zalogowany_pracownik}!")

    stawka_pracownika = pobierz_stawke_pracownika(zalogowany_pracownik, None)
    st.info(f"Twoja aktualna stawka godzinowa: **{stawka_pracownika} zł/h**")

    if not lista_budow:
        st.error(
            "❌ Brak dostępnych budów w systemie. Poproś administratora o dodanie"
            " budowy."
        )
    else:
        with st.form("form_pracy", clear_on_submit=True):
            st.subheader("Dodaj wpis czasu pracy")

            data = st.date_input("Data")
            budowa = st.selectbox("Wybierz budowę", lista_budow)

            st.markdown("🚗 **Czas dojazdu** (licznik naliczany jako 50% stawki)")
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                dojazd_od = st.time_input("Dojazd od")
            with col_d2:
                dojazd_do = st.time_input("Dojazd do")

            st.markdown("⏱️ **Czas pracy na budowie** (pełna stawka)")
            col1, col2 = st.columns(2)
            with col1:
                godzina_od = st.time_input("Godzina od")
            with col2:
                godzina_do = st.time_input("Godzina do")

            submit = st.form_submit_button("Dodaj wpis")

            if submit:
                dojazd_start_dt = pd.to_datetime(f"{data} {dojazd_od}")
                dojazd_koniec_dt = pd.to_datetime(f"{data} {dojazd_do}")
                start_dt = pd.to_datetime(f"{data} {godzina_od}")
                koniec_dt = pd.to_datetime(f"{data} {godzina_do}")

                if dojazd_koniec_dt < dojazd_start_dt:
                    st.error(
                        "Błąd: Godzina zakończenia dojazdu musi być późniejsza lub"
                        " równa rozpoczęciu dojazdu!"
                    )
                elif koniec_dt <= start_dt:
                    st.error(
                        "Błąd: Godzina zakończenia pracy musi być późniejsza niż"
                        " rozpoczęcia!"
                    )
                else:
                    konflikt = False
                    AktualneDane = wczytaj_dane()

                    if not AktualneDane.empty:
                        istniejace = AktualneDane[
                            (AktualneDane["Pracownik"] == zalogowany_pracownik)
                            & (AktualneDane["Data"] == str(data))
                        ]

                        for _, row in istniejace.iterrows():
                            ist_dojazd_start = pd.to_datetime(
                                f"{row['Data']} {row['Dojazd Od']}"
                            )
                            ist_praca_koniec = pd.to_datetime(f"{row['Data']} {row['Do']}")

                            if max(dojazd_start_dt, ist_dojazd_start) < min(
                                koniec_dt, ist_praca_koniec
                            ):
                                konflikt = True
                                break

                    if konflikt:
                        st.error(
                            "❌ Błąd: Te godziny (dojazd lub praca) pokrywają się z innym"
                            " Twoim wpisem w tym dniu! Nie możesz być w dwóch miejscach"
                            " naraz."
                        )
                    else:
                        roznica_dojazdu = (
                            dojazd_koniec_dt - dojazd_start_dt
                        ).total_seconds() / 3600
                        roznica_czasu = (koniec_dt - start_dt).total_seconds() / 3600

                        aktualna_stawka = pobierz_stawke_pracownika(
                            zalogowany_pracownik, str(data)
                        )

                        koszt_pracy = roznica_czasu * aktualna_stawka
                        stawka_dojazdu = aktualna_stawka / 2.0
                        koszt_dojazdu_zl = roznica_dojazdu * stawka_dojazdu
                        razem = koszt_pracy + koszt_dojazdu_zl

                        nowy_wpis = {
                            "Pracownik": zalogowany_pracownik,
                            "Data": str(data),
                            "Budowa": budowa,
                            "Dojazd Od": str(dojazd_od),
                            "Dojazd Do": str(dojazd_do),
                            "Czas dojazdu (godz)": round(roznica_dojazdu, 2),
                            "Od": str(godzina_od),
                            "Do": str(godzina_do),
                            "Stawka (zł/h)": aktualna_stawka,
                            "Godziny": round(roznica_czasu, 2),
                            "Koszt pracy (zł)": round(koszt_pracy, 2),
                            "Koszt dojazdu (zł)": round(koszt_dojazdu_zl, 2),
                            "Razem (zł)": round(razem, 2),
                        }

                        AktualneDane = pd.concat(
                            [AktualneDane, pd.DataFrame([nowy_wpis])], ignore_index=True
                        )
                        zapisz_dane(AktualneDane)
                        st.success(
                            f"✅ Zapisano pomyślnie! (Rozliczono wg stawki z dnia"
                            f" {data}: {aktualna_stawka} zł/h)"
                        )

    # --- WIDOK WŁASNYCH WPISÓW PRACOWNIKA ---
    st.markdown("---")
    st.subheader("📋 Twoje dotychczasowe wpisy")

    AktualneDane = wczytaj_dane()
    if not AktualneDane.empty:
        moje_dane = AktualneDane[AktualneDane["Pracownik"] == zalogowany_pracownik]

        if not moje_dane.empty:
            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("Twoje godziny", f"{moje_dane['Godziny'].sum():.2f} h")
            mc2.metric("Twój koszt pracy", f"{moje_dane['Koszt pracy (zł)'].sum():.2f} zł")
            mc3.metric("Razem do wypłaty", f"{moje_dane['Razem (zł)'].sum():.2f} zł")
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
                mime=(
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                ),
            )
        else:
            st.info("Nie masz jeszcze żadnych wpisów.")
    else:
        st.info("Brak wpisów w systemie.")
