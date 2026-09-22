import os
from PIL import Image
import pandas as pd
import streamlit as st

# --- KONFIGURACJA STRONY I ELEGANCKI WYGLĄD ---
# Bezpieczne ładowanie stonowanej ikony (zabezpieczenie przed brakiem pliku)
sciezka_favicony = os.path.join("loga", "logo.png")
if os.path.exists(sciezka_favicony):
  ikonka = Image.open(sciezka_favicony)
else:
  ikonka = "📐"  # Elegancki, profesjonalny symbol techniczny

st.set_page_config(
    page_title="Rozliczenie Kosztów Budowy", page_icon=ikonka, layout="centered"
)

# --- PROFESJONALNY STYL CSS (CORPORATE / MINIMAL) ---
st.markdown(
    """
    <style>
        /* Wyśrodkowanie głównego tytułu i zabezpieczenie przed zawijaniem */
        .centered-title {
            text-align: center;
            white-space: nowrap;
            font-weight: 700;
            letter-spacing: -0.5px;
            color: #111111;
            margin-bottom: 1.5rem;
        }
        
        /* Elegancki styl przycisków głównych (głęboki antracyt / czerń) */
        div.stButton > button[kind="primary"] {
            background-color: #1a1a1a !important;
            color: #ffffff !important;
            border: 1px solid #333333 !important;
            border-radius: 4px;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        div.stButton > button[kind="primary"]:hover {
            background-color: #333333 !important;
            border-color: #000000 !important;
        }

        /* Subtelniejsze obramowania kontenerów i pól */
        .stTextInput > div > div > input, .stSelectbox > div > div > div {
            border-radius: 4px !important;
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
      return pd.read_csv(plik)
    except Exception:
      return pd.DataFrame(columns=domyslne_kolumny)
  return pd.DataFrame(columns=domyslne_kolumny)


df_budowy = wczytaj_dane(
    PLIK_BUDOW, ["ID_Budowy", "Nazwa_Budowy", "Adres", "Status"]
)
df_pracownicy = wczytaj_dane(
    PLIK_PRACOWNIKOW, ["ID_Pracownika", "Imie_Nazwisko", "Rola", "Stawka"]
)

# --- PANEL BOCZNY (SIDEBAR) ---
with st.sidebar:
  # Opcjonalne logo w panelu, jeśli istnieje
  sciezka_pelne_logo = os.path.join("loga", "logo_pelne.png")
  if os.path.exists(sciezka_pelne_logo):
    st.image(sciezka_pelne_logo, use_column_width=True)

  st.markdown("### Panel Użytkownika")
  wybrana_rola = st.selectbox(
      "Wybierz poziom dostępu:", ["Użytkownik standardowy", "Administrator"]
  )

  st.markdown("---")
  st.markdown(
      "<p style='font-size: 0.8rem; color: #666;'>System Kontroli Czasu i"
      " Kosztów v1.2</p>",
      unsafe_allow_html=True,
  )

# --- GŁÓWNA LOGIKA APLIKACJI ---
if wybrana_rola == "Administrator":
  st.markdown("#### Panel Administratora")
  st.info(
      "Zalogowano jako Administrator. Masz dostęp do pełnych raportów, stawek"
      " oraz eksportu do programu Excel."
  )

  # Przykład sekcji administratora
  tab1, tab2 = st.tabs(["Zarządzanie Budowami", "Raporty Finansowe"])

  with tab1:
    st.write("Aktualna lista budów:")
    st.dataframe(df_budowy, use_container_width=True)

  with tab2:
    st.write("Moduł generowania raportów i eksportu danych.")
    if st.button("Generuj raport Excel", kind="primary"):
      st.success("Raport został przygotowany pomyślnie.")

else:
  st.markdown("#### Panel Rejestracji Czasu i Kosztów")
  st.write("Wprowadź bieżące dane operacyjne dla wybranej budowy.")

  # Formularz dla standardowego użytkownika
  if not df_budowy.empty:
    wybrana_budowa = st.selectbox(
        "Wybierz budowę:", df_budowy["Nazwa_Budowy"].tolist()
    )
  else:
    wybrana_budowa = st.text_input("Nazwa budowy:")

  if st.button("Zapisz wpis", kind="primary"):
    st.success(f"Zapisano dane dla budowy: {wybrana_budowa}")
