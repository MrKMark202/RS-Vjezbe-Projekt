# Nogomet/ui/streamlit_app.py

import streamlit as st
import pandas as pd

from Nogomet.core.services import (
    dohvati_sve_lige,
    kreiraj_ligu,
    obrisi_ligu,
    dohvati_klubove_za_ligu,
    kreiraj_klub,
    obrisi_klub,
    dohvati_utakmice_za_ligu,
    kreiraj_utakmicu,
    dohvati_tablicu,
)


def odaberi_ligu() -> int | None:

    lige = dohvati_sve_lige()
    if not lige:
        st.info("Još nema niti jedne lige. Kreirajte ligu u sekciji 'Lige'.")
        return None

    # prikazujemo "Naziv (ID: x)" u selectboxu
    opcije = {f"{liga['naziv']} (ID: {liga['id']})": liga["id"] for liga in lige}

    odabir = st.selectbox("Odaberite ligu", list(opcije.keys()))
    return opcije[odabir]


def stranica_lige():
    st.header("Lige")

    st.subheader("Dodaj novu ligu")
    naziv = st.text_input("Naziv lige")
    if st.button("Spremi ligu"):
        if not naziv.strip():
            st.warning("Naziv lige ne može biti prazan.")
        else:
            kreiraj_ligu(naziv.strip())
            st.success(f"Liga '{naziv}' je dodana.")
            st.rerun()

    st.subheader("Popis liga")
    lige = dohvati_sve_lige()
    if not lige:
        st.write("Nema liga.")
    else:
        df = pd.DataFrame(lige)
        df = df.rename(columns={"id": "ID", "naziv": "Naziv"})
        st.dataframe(df, use_container_width=True)

        # opcija za brisanje lige
        st.markdown("---")
        st.write("Brisanje lige (brišu se i svi klubovi i utakmice u toj ligi):")
        liga_za_brisanje_id = st.selectbox(
            "Odaberite ligu za brisanje",
            options=[liga["id"] for liga in lige],
            format_func=lambda lid: next(
                (l["naziv"] for l in lige if l["id"] == lid),
                f"Liga ID {lid}",
            ),
        )
        if st.button("Obriši ligu"):
            obrisi_ligu(liga_za_brisanje_id)
            st.success("Liga je obrisana.")
            st.rerun()


def stranica_klubovi():
    st.header("Klubovi")

    liga_id = odaberi_ligu()
    if liga_id is None:
        return

    st.subheader("Dodaj novi klub u odabranu ligu")
    naziv = st.text_input("Naziv kluba")
    if st.button("Spremi klub"):
        if not naziv.strip():
            st.warning("Naziv kluba ne može biti prazan.")
        else:
            kreiraj_klub(liga_id, naziv.strip())
            st.success(f"Klub '{naziv}' je dodan.")
            st.rerun()

    st.subheader("Klubovi u odabranoj ligi")
    klubovi = dohvati_klubove_za_ligu(liga_id)
    if not klubovi:
        st.write("Nema klubova u ovoj ligi.")
    else:
        df = pd.DataFrame(klubovi)
        df = df.rename(columns={"id": "ID", "naziv": "Naziv", "liga_id": "Liga ID"})
        st.dataframe(df, use_container_width=True)

        st.markdown("---")
        st.write("Brisanje kluba (brišu se i sve njegove utakmice):")
        klub_za_brisanje_id = st.selectbox(
            "Odaberite klub za brisanje",
            options=[klub["id"] for klub in klubovi],
            format_func=lambda kid: next(
                (k["naziv"] for k in klubovi if k["id"] == kid),
                f"Klub ID {kid}",
            ),
        )
        if st.button("Obriši klub"):
            obrisi_klub(klub_za_brisanje_id)
            st.success("Klub je obrisan.")
            st.rerun()


def stranica_utakmice():
    st.header("Utakmice")

    liga_id = odaberi_ligu()
    if liga_id is None:
        return

    klubovi = dohvati_klubove_za_ligu(liga_id)
    if len(klubovi) < 2:
        st.info("Za unos utakmica potrebno je imati barem dva kluba u ligi.")
        return

    st.subheader("Dodaj novu utakmicu")

    # mapiramo ID <-> naziv
    klubovi_po_id = {klub["id"]: klub["naziv"] for klub in klubovi}

    domaci_odabir = st.selectbox(
        "Domaći klub",
        options=list(klubovi_po_id.keys()),
        format_func=lambda kid: klubovi_po_id[kid],
    )
    gosti_odabir = st.selectbox(
        "Gostujući klub",
        options=list(klubovi_po_id.keys()),
        format_func=lambda kid: klubovi_po_id[kid],
    )

    domaci_goals = st.number_input("Golovi domaćih", min_value=0, step=1, value=0)
    gosti_goals = st.number_input("Golovi gostiju", min_value=0, step=1, value=0)

    if st.button("Spremi utakmicu"):
        if domaci_odabir == gosti_odabir:
            st.warning("Domaći i gosti ne mogu biti isti klub.")
        else:
            kreiraj_utakmicu(
                liga_id,
                domaci_odabir,
                gosti_odabir,
                int(domaci_goals),
                int(gosti_goals),
            )
            st.success("Utakmica je dodana.")
            st.rerun()

    st.subheader("Popis utakmica u odabranoj ligi")
    utakmice = dohvati_utakmice_za_ligu(liga_id)
    if not utakmice:
        st.write("Nema utakmica u ovoj ligi.")
    else:
        # obogatimo podatke imenima klubova
        prikaz = []
        for u in utakmice:
            prikaz.append(
                {
                    "ID": u["id"],
                    "Liga ID": u["liga_id"],
                    "Domaći": klubovi_po_id.get(u["domaci_id"], f"ID {u['domaci_id']}"),
                    "Gosti": klubovi_po_id.get(u["gosti_id"], f"ID {u['gosti_id']}"),
                    "Rezultat": f"{u['domaci_goals']} : {u['gosti_goals']}",
                }
            )

        df = pd.DataFrame(prikaz)
        st.dataframe(df, use_container_width=True)


def stranica_tablica():
    st.header("Tablica")

    liga_id = odaberi_ligu()
    if liga_id is None:
        return

    tablica = dohvati_tablicu(liga_id)
    if not tablica:
        st.write("Nema dostupne statistike (nema utakmica ili klubova).")
        return

    df = pd.DataFrame(tablica)
    df = df.rename(
        columns={
            "klub_id": "Klub ID",
            "klub_naziv": "Klub",
            "odigrane": "Odigrane",
            "pobjede": "Pobjede",
            "nerjesene": "Neriješene",
            "porazi": "Porazi",
            "golovi_dani": "Golovi dani",
            "golovi_primljeni": "Golovi primljeni",
            "gol_razlika": "Gol razlika",
            "bodovi": "Bodovi",
        }
    )

    st.subheader("Poredak klubova")
    st.dataframe(df, use_container_width=True)


def run():
    st.set_page_config(page_title="Nogomet Lige", layout="wide")
    st.title("Nogomet – upravljanje ligama, klubovima i utakmicama")

    izbor = st.sidebar.radio(
        "Navigacija",
        ("Lige", "Klubovi", "Utakmice", "Tablica"),
    )

    if izbor == "Lige":
        stranica_lige()
    elif izbor == "Klubovi":
        stranica_klubovi()
    elif izbor == "Utakmice":
        stranica_utakmice()
    elif izbor == "Tablica":
        stranica_tablica()