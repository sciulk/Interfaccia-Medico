import streamlit as st
from PIL import Image
import os
import pandas as pd
import base64
import random
from io import StringIO

st.set_page_config(layout="wide")

st.markdown("<h2 style='margin-bottom:0;'>Confronto immagini endoscopiche</h2>", unsafe_allow_html=True)
st.markdown("<p style='margin-top:0;'>Clicca su A o B per indicare l'immagine che ritieni migliore.</p>", unsafe_allow_html=True)

# Directory immagini
orig_dir = "sample_images"
proc_dir = "sample_images_processed"

# Lista immagini disponibili in entrambe le cartelle
immagini = sorted(os.listdir(orig_dir))
immagini = [img for img in immagini if os.path.exists(os.path.join(proc_dir, img))]

# Inizializza dataframe delle scelte in memoria (solo sessione corrente)
if "df_scelte" not in st.session_state:
    st.session_state.df_scelte = pd.DataFrame(columns=["immagine", "scelta", "tipo_immagine"])

# Inizializza immagini da valutare
if "immagini_da_valutare" not in st.session_state:
    immagini_da_valutare = immagini.copy()
    random.shuffle(immagini_da_valutare)
    st.session_state.immagini_da_valutare = immagini_da_valutare
    st.session_state.indice = 0
    st.session_state.ordine_random = random.choice([True, False])

# Funzione per codificare immagine in base64
def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# Funzione per registrare scelta in sessione
def registra_scelta(lettera, immagine_corrente):
    if lettera == "A":
        scelta_tipo = "originale" if st.session_state.ordine_random else "modificata"
    else:
        scelta_tipo = "modificata" if st.session_state.ordine_random else "originale"

    nuova_riga = pd.DataFrame([[immagine_corrente, lettera, scelta_tipo]],
                              columns=["immagine", "scelta", "tipo_immagine"])
    st.session_state.df_scelte = pd.concat([st.session_state.df_scelte, nuova_riga], ignore_index=True)
    st.session_state.indice += 1
    st.session_state.ordine_random = random.choice([True, False])
    st.rerun()

# Mostra immagini da confrontare
if st.session_state.indice < len(st.session_state.immagini_da_valutare):
    immagine_corrente = st.session_state.immagini_da_valutare[st.session_state.indice]
    img_path_orig = os.path.join(orig_dir, immagine_corrente)
    img_path_proc = os.path.join(proc_dir, immagine_corrente)

    if st.session_state.ordine_random:
        img_A_path, img_B_path = img_path_orig, img_path_proc
    else:
        img_A_path, img_B_path = img_path_proc, img_path_orig

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

    st.markdown(f"<center><small>{st.session_state.indice + 1} / {len(st.session_state.immagini_da_valutare)} immagini valutate</small></center>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col_center = st.columns([1, 2, 1])[1]
    with col_center:
        if st.button("🔁 Annulla ultima scelta"):
            if st.session_state.indice > 0:
                st.session_state.df_scelte = st.session_state.df_scelte.iloc[:-1]
                st.session_state.indice -= 1
                st.session_state.ordine_random = random.choice([True, False])
                st.rerun()
            else:
                st.warning("Nessuna scelta da annullare.")

else:
    st.success("✅ Tutte le immagini sono state valutate!")

    st.dataframe(st.session_state.df_scelte)

    # Scarica risultati
    csv_buffer = StringIO()
    st.session_state.df_scelte.to_csv(csv_buffer, index=False)
    st.download_button(
        label="📥 Scarica risultati",
        data=csv_buffer.getvalue(),
        file_name="scelte_medico.csv",
        mime="text/csv"
    )
