import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Rozliczanie Kosztów Budowy", page_icon="🏗️", layout="centered"
)

# Pliki do trwałego przechowywania danych
PLIK_BAZY = "baza_danych.csv"
PLIK_PRACOWNICY = "baza_pracownikow.csv"
PLIK_BUDOWY = "baza_budow.csv"


# --- FUNKCJE POMOCNICZE DLA BAZ ---
def wczytaj_pracownikow():
  if os.path.exists(PLIK_PRACOWNICY):
    df = pd.read_csv(PLIK_PRACOWNICY, dtype=str)
    if "Rola" not in df.columns:
      df["Rola"] = "Pracownik"
      df.loc[(df["Pin"] == "0000") | (df["Pracownik"] == "Admin"), "Rola"] = (
          "Admin"
      )
      df.to_csv(PLIK_PRACOWNICY, index=False)
    return df
  else:
    df_domyslne = pd.DataFrame(
        {
            "Pin": ["1234", "5678", "0000"],
            "Pracownik": ["Jan Kowalski", "Adam Nowak", "Admin"],
            "Rola": ["Pracownik", "Pracownik", "Admin"],
        }
    )
    df_domyslne.to_csv(PLIK_PRACOWNICY, index=False)
    return df_domyslne


def zapisz_pracownikow(df):
  df.to_csv(PLIK_PRACOWNICY, index=False)


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

# --- PANEL LOGOWANIA ---
if not st.session_state.zalogowany:
  st.sidebar.header("🔐 Logowanie")
  pin_input = st.sidebar.text_input("Wpisz swój 4-cyfrowy PIN", type="password")

  if st.sidebar.button("Zaloguj się"):
    df_pracownicy = wczytaj_pracownikow()
    pasujacy = df_pracownicy[df_pracownicy["Pin"] == pin_input]

    if not pasujacy.empty:
      st.session_state.zalogowany = True
      st.session_state.aktualny_pracownik = pasujacy.iloc[0]["Pracownik"]
      st.session_state.rola = str(pasujacy.iloc[0]["Rola"]).strip()
      st.rerun()
    else:
      st.sidebar.error("❌ Błędny PIN!")

  st.info(
      "👈 Wpisz swój PIN w panelu po lewej stronie i kliknij 'Zaloguj się'."
      "\n\n*(Domyślny PIN administratora to: `0000`)*"
  )
  st.stop()

# Użytkownik zalogowany
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

# Pobranie aktualnych danych i budów na start
dane_systemowe = wczytaj_dane()
lista_budow = wczytaj_budowy()


# --- PANEL ADMINISTRATORA ---
if rola_uzytkownika == "Admin":
  st.subheader("👑 Panel Administratora")

  menu_admin = st.radio(
      "Wybierz sekcję:",
      [
          "📊 Raport wszystkich wpisów",
          "👥 Zarządzanie Pracownikami",
          "🏗️ Zarządzanie Budowami",
      ],
      horizontal=True,
  )
  st.markdown("---")

  if menu_admin == "📊 Raport wszystkich wpisów":
    st.markdown("### Raport godzin i kosztów całej firmy")
    if not dane_systemowe.empty:
      st.dataframe(dane_systemowe, use_container_width=True)


      def convert_df_to_excel(df):
        from io import BytesIO

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
          df.to_excel(writer, index=False, sheet_name="Rozliczenie_Calkowite")
        return output.getvalue()


      excel_data = convert_df_to_excel(dane_systemowe)
      st.download_button(
          label="📥 Pobierz pełny raport wszystkich pracowników (.xlsx)",
          data=excel_data,
          file_name="pelny_raport_budowy.xlsx",
          mime=(
              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
          ),
      )
    else:
      st.warning("Brak jakichkolwiek wpisów w systemie.")

  elif menu_admin == "👥 Zarządzanie Pracownikami":
    st.markdown("### Dodaj nowego pracownika")
    df_pracownicy = wczytaj_pracownikow()

    with st.form("form_dodaj_pracownika", clear_on_submit=True):
      nowe_imie = st.text_input("Imię i nazwisko pracownika")
      nowy_pin = st.text_input("4-cyfrowy PIN", max_chars=4, type="password")
      wybrana_rola = st.selectbox(
          "Uprawnienia", ["Pracownik", "Admin"]
      )
      submit_pracownik = st.form_submit_button("Dodaj pracownika")

      if submit_pracownik:
        if not nowe_imie or not nowy_pin:
          st.warning("Uzupełnij imię oraz PIN.")
        elif len(nowy_pin) < 4:
          st.error("PIN musi składać się z co najmniej 4 znaków.")
        elif nowy_pin in df_pracownicy["Pin"].values:
          st.error("❌ Ten PIN jest już zajęty przez innego pracownika!")
        else:
          nowy_wiersz = pd.DataFrame(
              {
                  "Pin": [nowy_pin],
                  "Pracownik": [nowe_imie],
                  "Rola": [wybrana_rola],
              }
          )
          df_pracownicy = pd.concat(
              [df_pracownicy, nowy_wiersz], ignore_index=True
          )
          zapisz_pracownikow(df_pracownicy)
          st.success(
              f"✅ Pomyślnie dodano pracownika: {nowe_imie} ({wybrana_rola})"
          )
          st.rerun()

    st.markdown("---")
    st.markdown("### Aktualna lista pracowników w systemie")
    tabela_pokazowa = df_pracownicy.copy()
    tabela_pokazowa["Pin"] = "****"
    st.dataframe(tabela_pokazowa, use_container_width=True)

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
    st.markdown("### Aktualnie aktywne budowy (Zarządzaj / Usuń)")
    aktualne_b = wczytaj_budowy()

    if aktualne_b:
      for b in aktualne_b:
        col_tekst, col_btn = st.columns([4, 1])
        with col_tekst:
          st.write(f"🏗️ **{b}**")
        with col_btn:
          if st.button("🗑️ Usuń", key=f"del_{b}"):
            usun_budowe(b)
            st.success(f"Usunięto budowę: {b}")
            st.rerun()
    else:
      st.info("Brak aktywnych budów.")

else:
  # --- PANEL DLA ZWYKŁEGO PRACOWNIKA ---
  st.subheader(f"Witaj, {zalogowany_pracownik}!")

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

      # Czas dojazdu (od - do) umieszczony nad godzinami pracy
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

      stawka = st.number_input(
          "Twoja stawka godzinowa (zł)", min_value=0.0, value=30.0, step=5.0
      )

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
              "Błąd: Godzina zakończenia pracy musi быть późniejsza niż"
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
              # Sprawdzamy kolizję dla całego przedziału (od początku dojazdu do końca pracy)
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

            koszt_pracy = roznica_czasu * stawka
            stawka_dojazdu = stawka / 2.0
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
                "Stawka (zł/h)": stawka,
                "Godziny": round(roznica_czasu, 2),
                "Koszt pracy (zł)": round(koszt_pracy, 2),
                "Koszt dojazdu (zł)": round(koszt_dojazdu_zl, 2),
                "Razem (zł)": round(razem, 2),
            }

            AktualneDane = pd.concat(
                [AktualneDane, pd.DataFrame([nowy_wpis])], ignore_index=True
            )
            zapisz_dane(AktualneDane)
            st.success("✅ Zapisano pomyślnie!")

  # --- WIDOK WŁASNYCH WPISÓW PRACOWNIKA ---
  st.markdown("---")
  st.subheader("📋 Twoje dotychczasowe wpisy")

  AktualneDane = wczytaj_dane()
  if not AktualneDane.empty:
    moje_dane = AktualneDane[AktualneDane["Pracownik"] == zalogowany_pracownik]

    if not moje_dane.empty:
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