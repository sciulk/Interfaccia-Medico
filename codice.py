import streamlit as st
from PIL import Image
import os
import pandas as pd
import base64
import random
import requests


st.set_page_config(layout="wide")

st.markdown("<h2 style='margin-bottom:0;'>Confronto immagini endoscopiche</h2>", unsafe_allow_html=True)
st.markdown("<p style='margin-top:0;'>Clicca su A o B per indicare l'immagine che ritieni migliore.</p>", unsafe_allow_html=True)

# Directory
orig_dir = "sample_images"
proc_dir = "sample_images_processed"
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)
scelte_file = os.path.join(output_dir, "scelte_medico.csv")

# Lista immagini originali
immagini = sorted(os.listdir(orig_dir))
immagini = [img for img in immagini if os.path.exists(os.path.join(proc_dir, img))]

# Carica scelte precedenti
if os.path.exists(scelte_file):
    df_scelte = pd.read_csv(scelte_file)
    immagini_valutate = df_scelte["immagine"].tolist()
else:
    df_scelte = pd.DataFrame(columns=["immagine", "scelta", "tipo_immagine"])
    immagini_valutate = []

# Inizializza sessione
if "immagini_da_valutare" not in st.session_state:
    immagini_da_valutare = [img for img in immagini if img not in immagini_valutate]
    random.shuffle(immagini_da_valutare)
    st.session_state.immagini_da_valutare = immagini_da_valutare
    st.session_state.indice = 0
    st.session_state.ordine_random = random.choice([True, False])

# Funzione per codificare immagine
def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# Funzione per registrare la scelta
def registra_scelta(lettera, immagine_corrente):
    if lettera == "A":
        scelta_tipo = "originale" if st.session_state.ordine_random else "modificata"
    else:
        scelta_tipo = "modificata" if st.session_state.ordine_random else "originale"

    dati = {
        "immagine": immagine_corrente,
        "scelta": lettera,
        "tipo_immagine": scelta_tipo
    }

    try:
        response = requests.post(
            "https://script.google.com/macros/s/AKfycbwFHdnOqhte_O5nbjX3lJZObeOK2cc0pQRq10QtYTvUueQegksbZXtZQAgJnNgUx9zQCg/exec",
            json=dati,
            timeout=5
        )
        if response.status_code == 200:
            st.success("✅ Scelta salvata!")
        else:
            st.warning("⚠️ Errore nel salvataggio remoto.")
    except Exception as e:
        st.warning(f"⚠️ Connessione fallita: {e}")

    st.session_state.indice += 1
    st.session_state.ordine_random = random.choice([True, False])
    st.rerun()


# Mostra immagine corrente
if st.session_state.indice < len(st.session_state.immagini_da_valutare):
    immagine_corrente = st.session_state.immagini_da_valutare[st.session_state.indice]
    img_path_orig = os.path.join(orig_dir, immagine_corrente)
    img_path_proc = os.path.join(proc_dir, immagine_corrente)

    # Assegna immagini ad A e B
    if st.session_state.ordine_random:
        img_A_path = img_path_orig
        img_B_path = img_path_proc
    else:
        img_A_path = img_path_proc
        img_B_path = img_path_orig

    col1, col2 = st.columns([1, 1], gap="medium")

    with col1:
        if st.button("A", key="btnA", use_container_width=True):
            registra_scelta("A", immagine_corrente)
        img_data_A = img_to_base64(img_A_path)
        st.markdown(
            f"""<img src="data:image/png;base64,{img_data_A}" style="width:100%; max-width:500px; display:block; margin:auto; border-radius:6px;" />""",
            unsafe_allow_html=True,
        )

    with col2:
        if st.button("B", key="btnB", use_container_width=True):
            registra_scelta("B", immagine_corrente)
        img_data_B = img_to_base64(img_B_path)
        st.markdown(
            f"""<img src="data:image/png;base64,{img_data_B}" style="width:100%; max-width:500px; display:block; margin:auto; border-radius:6px;" />""",
            unsafe_allow_html=True,
        )

    # Progresso
    st.markdown(f"<center><small>{st.session_state.indice + 1} / {len(st.session_state.immagini_da_valutare)} immagini valutate</small></center>", unsafe_allow_html=True)

    # Spazio
    st.markdown("<br>", unsafe_allow_html=True)

    # Pulsante per annullare ultima scelta (centrato)
    col_center = st.columns([1, 2, 1])[1]
    with col_center:
        if st.button("🔁 Annulla ultima scelta"):
            if st.session_state.indice > 0:
                if os.path.exists(scelte_file):
                    df_scelte_corrente = pd.read_csv(scelte_file)
                    if len(df_scelte_corrente) > 0:
                        # Rimuovi ultima riga
                        df_scelte_corrente = df_scelte_corrente[:-1]
                        df_scelte_corrente.to_csv(scelte_file, index=False)

                        # Riporta indietro l'indice
                        st.session_state.indice -= 1

                        # Reimposta ordine casuale
                        st.session_state.ordine_random = random.choice([True, False])

                        st.rerun()
            else:
                st.warning("Nessuna scelta da annullare.")

else:
    st.success("✅ Tutte le immagini sono state valutate!")
    st.dataframe(pd.read_csv(scelte_file))
