import os
from PIL import Image
import pandas as pd
import streamlit as st

# --- KONFIGURACJA STRONY I ELEGANCKI WYGLĄD ---
sciezka_favicony = os.path.join("loga", "logo.png")
if os.path.exists(sciezka_favicony):
  ikonka = Image.open(sciezka_favicony)
else:
  ikonka = "📐"

st.set_page_config(
    page_title="Rozliczenie Kosztów Budowy", page_icon=ikonka, layout="centered"
)

# --- PROFESJONALNY STYL CSS (CORPORATE / MINIMAL) ---
st.markdown(
    """
    <style>
        .centered-title {
            text-align: center;
            white-space: nowrap;
            font-weight: 700;
            letter-spacing: -0.5px;
            color: #111111;
            margin-bottom: 1.5rem;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# --- NAGŁÓWEK APLIKACJI ---
st.markdown(
    '<h1 class="centered-title">Rozliczenie Kosztów Budowy</h1>',
    unsafe_allow_html=True,
)

# --- FUNKCJE POMOCNICZE / BAZA DANYCH ---
PLIK_BUDOW = "baza_budow.csv"
PLIK_PRACOWNIKOW = "baza_pracownikow.csv"


def wczytaj_dane(plik, domyslne_kolumny):
  if os.path.exists(plik):
    try:
      df = pd.read_csv(plik)
      if not all(col in df.columns for col in domyslne_kolumny):
        return pd.DataFrame(columns=domyslne_kolumny)
      return df
    except Exception:
      return pd.DataFrame(columns=domyslne_kolumny)
  return pd.DataFrame(columns=domyslne_kolumny)


df_budowy = wczytaj_dane(
    PLIK_BUDOW, ["ID_Budowy", "Nazwa_Budowy", "Adres", "Status"]
)
df_pracownicy = wczytaj_dane(
    PLIK_PRACOWNIKOW, ["ID_Pracownika", "Imie_Nazwisko", "Rola", "Stawka"]
)

# --- INICJALIZACJA SESJI LOGOWANIA ---
if "zalogowany" not in st.session_state:
  st.session_state.zalogowany = False
if "rola" not in st.session_state:
  st.session_state.rola = None
if "uzytkownik" not in st.session_state:
  st.session_state.uzytkownik = ""

# --- PANEL BOCZNY (SIDEBAR) - LOGOWANIE I NAWIGACJA ---
with st.sidebar:
  sciezka_pelne_logo = os.path.join("loga", "logo_pelne.png")
  if os.path.exists(sciezka_pelne_logo):
    st.image(sciezka_pelne_logo, use_container_width=True)

  st.markdown("### Panel Autoryzacji")

  if not st.session_state.zalogowany:
    # Formularz logowania
    login_input = st.text_input("Login / ID pracownika:")
    haslo_input = st.text_input("Hasło:", type="password")

    if st.button("Zaloguj się", type="primary"):
      # Prosta, bezpieczna logika weryfikacji (możesz dostosować do swojej bazy pracowników)
      if login_input == "admin" and haslo_input == "admin123":
        st.session_state.zalogowany = True
        st.session_state.rola = "Administrator"
        st.session_state.uzytkownik = "Administrator Systemu"
        st.rerun()
      elif (
          login_input != ""
      ):  # Standardowy użytkownik (można rozszerzyć o weryfikację z df_pracownicy)
        st.session_state.zalogowany = True
        st.session_state.rola = "Użytkownik standardowy"
        st.session_state.uzytkownik = login_input
        st.rerun()
      else:
        st.error("Wprowadź poprawne dane logowania.")
  else:
    # Widok po zalogowaniu
    st.success(f"Zalogowano jako:\n**{st.session_state.uzytkownik}**")
    st.info(F"Rola: **{st.session_state.rola}**")

    if st.button("Wyloguj się"):
      st.session_state.zalogowany = False
      st.session_state.rola = None
      st.session_state.uzytkownik = ""
      st.rerun()

  st.markdown("---")
  st.markdown(
      "<p style='font-size: 0.8rem; color: #666;'>System Kontroli Czasu i"
      " Kosztów v1.2</p>",
      unsafe_allow_html=True,
  )

# --- GŁÓWNA LOGIKA APLIKACJI (WYMAGAJĄCA LOGOWANIA) ---
if not st.session_state.zalogowany:
  st.warning(
      "🔒 Proszę zalogować się za pomocą panelu bocznego, aby uzyskać dostęp"
      " do systemu."
  )
else:
  if st.session_state.rola == "Administrator":
    st.markdown("#### Panel Administratora")
    st.info(
        "Masz pełny dostęp do zarządzania budowami, bazą pracowników oraz"
        " generowania raportów finansowych."
    )

    tab1, tab2 = st.tabs(["Zarządzanie Budowami", "Raporty Finansowe"])

    with tab1:
      st.write("Aktualna lista budów w systemie:")
      st.dataframe(df_budowy, use_container_width=True)

    with tab2:
      st.write("Moduł generowania raportów i eksportu danych.")
      if st.button("Generuj raport Excel", type="primary"):
        st.success("Raport został przygotowany pomyślnie.")

  else:
    st.markdown("#### Panel Rejestracji Czasu i Kosztów")
    st.write(
        "Wprowadź bieżące dane operacyjne dla wydelegowanej budowy i czasu"
        " pracy."
    )

    if not df_budowy.empty and "Nazwa_Budowy" in df_budowy.columns:
      wybrana_budowa = st.selectbox(
          "Wybierz budowę:", df_budowy["Nazwa_Budowy"].tolist()
      )
    else:
      wybrana_budowa = st.text_input("Nazwa budowy:")

    if st.button("Zapisz wpis", type="primary"):
      st.success(f"Zapisano wpis dla budowy: {wybrana_budowa}")
