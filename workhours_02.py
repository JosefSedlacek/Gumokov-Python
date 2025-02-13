import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title='Pracovní kalendář',
    page_icon=':calendar:',
    layout='centered',
    initial_sidebar_state='expanded'
)

# -----------------------------------------------------------------------------
# NÁVOD -----------------------------------------------------------------------

def show_instructions():
    st.title("Návod - Jak používat tuto aplikaci")
    st.markdown(""" 
    ## Nahrávání souborů

    Nahrajte soubory Workhours (CSV) a Skupiny (Excel). Tyto soubory najdete na:  
    `P:\\All Access\\TB HRA KPIs\\podklady\\Kapacity`  
    Dejte pozor, abyste nahrávali soubor na správné místo - nesmíte nahrát 
    Skupiny do pole pro nahrávání Workhours a opačně. Po nahrání se tyto 
    tabulky propojí a mělo by se ukázat "Propojení bylo úspěšné". Poté můžete
    pokračovat na list "Úprava strojních hodin" nebo "Úprava lidských hodin".
    
    ---

    ## Úprava dat
    
    V této aplikaci jsou dvě samostatné sekce pro úpravy dat:
    1. **Úprava strojních hodin**
    2. **Úprava lidských hodin**

    Logika filtrování je stejná pro obě sekce, liší se jen v tom, zda se mění 
    sloupec pro strojní nebo lidské hodiny.
    
    Při upravování nabídky hodin si nejdříve vyberu, jestli upravuji strojní nebo
    lidské hodiny. Následně vyberu, pro která pracoviště upravuji. Můžu vybrat 
    i celý výrobní proces nebo skupinu pracovišť.

    ---
    
    ## Kontrola a stažení nových dat

    #### 1. Graf nabídky pro vybrané pracoviště

    Tato část slouží pro kontrolu. Zde si můžete vybrat rok a pracoviště a následně 
    se vám zobrazí graf - opět můžete vybrat, zda chcete zobrazit hodiny lidské 
    nebo strojní.

    #### 2. Stažení dat

    Až budete s úpravami hotovi, klikněte na `Stáhnout Workhours.csv`. Upravený
    soubor najdete ve stažených souborech na vašem PC. Tento soubor poté přetáhněte
    do složky:
    `P:\\All Access\\TB HRA KPIs\\podklady\\Kapacity`
    a nahraďte původní soubor tímto novým souborem. 

    POZOR: na této adrese `P:\\All Access\\TB HRA KPIs\\podklady\\Kapacity` se soubor
    musí jmenovat Workhours.csv. Pokud se bude jmenovat jinak, nenačte se do PowerBI.
    """)

# -----------------------------------------------------------------------------
# NAHRÁVÁNÍ SOUBORŮ -----------------------------------------------------------

def upload_files():
    st.title("Nahrávání souborů")
    
    # Pokud jsou data už nahraná
    if 'df' in st.session_state:
        st.subheader("Máte načtená data: Workhours a Skupiny")
        st.dataframe(st.session_state['df'].head(10))
        st.info("Data jsou již nahraná, pokračujte v kartě Úprava strojních nebo lidských hodin.")
    # Nahrávání dat
    else:
        # Nahrání csv Workhours
        uploaded_csv = st.file_uploader("Nahraj soubor Workhours (csv)", type=["csv"])
        df_csv = None
        if uploaded_csv is not None:
            df_csv = pd.read_csv(uploaded_csv, sep=';', decimal=',')
            st.subheader("Obsah souboru Workhours")
            st.dataframe(df_csv.head(4))
        
        # Nahrání excelu Skupiny
        uploaded_xlsx = st.file_uploader("Nahraj soubor Skupiny (xlsx)", type=["xlsx"])
        df_xlsx = None
        if uploaded_xlsx is not None:
            df_xlsx = pd.read_excel(uploaded_xlsx)
            st.subheader("Obsah souboru Skupiny")
            st.dataframe(df_xlsx.head(4))
        
        # Spojení csv a excelu
        if df_csv is not None and df_xlsx is not None:
            st.subheader("Propojení dat Workhours a Skupiny")
            relevant_columns = ["pracoviště", "proces", "podproces", "název"]
            df_xlsx = df_xlsx[relevant_columns]
            df = pd.merge(left=df_csv, right=df_xlsx, how="left", left_on=['Pracoviště'], right_on=['pracoviště'])
            st.success("Propojení bylo úspěšné!")
            st.dataframe(df.head(10))
            
            # SESSION_STATE
            st.session_state['df'] = df

# -----------------------------------------------------------------------------
# ÚPRAVA STROJNÍCH HODIN ------------------------------------------------------

def edit_data_stroje():
    st.title("Úprava strojních hodin")
    if 'df' in st.session_state:

        # SESSION_STATE Načtení dataframe !!!
        df = st.session_state['df']

        # Výběr typu filtrování
        st.subheader("Výběr pracoviště:")
        filter_type = st.radio(
            "Zvolte, zda chcete pracovat s konkrétním pracovištěm, skupinou, nebo procesem:",
            ("Pracoviště (název)", "Skupina pracovišť (podproces)", "Celý proces")
        )

        selected_names = []
        selected_subprocesses = []
        selected_processes = []

        # Výběr podle zvoleného typu
        if filter_type == "Pracoviště (název)":
            selected_names = st.multiselect('Vyber jedno nebo více pracovišť (názvy pracovišť):', 
                                            df['název'].dropna().unique())
        elif filter_type == "Skupina pracovišť (podproces)":
            selected_subprocesses = st.multiselect('Vyber jednu nebo více skupin (podprocesy):', 
                                                   df['podproces'].dropna().unique())
        else:  # c) Celý proces
            selected_processes = st.multiselect('Vyber jeden nebo více výrobních procesů:', 
                                                df['proces'].dropna().unique())

        st.markdown("""
                    ---
                    ## Strojní hodiny
                    """)

        col1, col2 = st.columns([1, 1], gap="large")

        # Vytvoření widgetů pro výběr roků, měsíc/týden, dny/svátky
        with col1:
            st.subheader("Výběr dnů:")
            # Vybrat rok
            rok = st.multiselect('Vyber rok:', options=df['Rok'].unique())

            # Zvolit měsíc nebo týden
            time_selection = st.radio("Vyberte, zda chcete filtrovat podle týdne nebo měsíce:", ("Vybrat týden", "Vybrat měsíc"))
            if time_selection == "Vybrat týden":
                tyden = st.multiselect('Vyber týden:', options=df['Týden'].dropna().unique())
            else:
                mesic = st.multiselect('Vyber měsíc:', options=df['Měsíc'].dropna().unique())

            st.markdown("---")
            
            # Zvolit svátky - pracovní den - víkend
            svatky = st.multiselect('Svátky, víkend, pracovní den:', options=df['Svátky'].dropna().unique(), default=None)
            
            # Zvolit dny v týdnu (ve správném pořadí)
            dni_v_tydnu = ['Po', 'Út', 'St', 'Čt', 'Pá', 'So', 'Ne']
            available_days = [day for day in dni_v_tydnu if day in df['Den'].unique()]
            den = st.multiselect('Vyber den:', options=available_days)

        # Vstupní pole pro zadání nové hodnoty strojních hodin
        with col2:
            st.subheader("Nová hodnota:")
            nabidka_stroje = st.number_input('STROJNÍ HODINY', min_value=0.0, format="%.2f", key='nabidka_stroje_input')

            # Tlačítko pro aktualizaci dat
            if st.button('Aktualizovat strojní hodiny'):
                mask = pd.Series([True] * len(df))  # výchozí maska (všude True)

                # Filtrování podle typu
                if filter_type == "Pracoviště (název)" and selected_names:
                    mask = mask & (df['název'].isin(selected_names))
                elif filter_type == "Skupina pracovišť (podproces)" and selected_subprocesses:
                    mask = mask & (df['podproces'].isin(selected_subprocesses))
                elif filter_type == "Celý proces" and selected_processes:
                    mask = mask & (df['proces'].isin(selected_processes))

                # Filtr pro rok
                if rok:
                    mask = mask & (df['Rok'].isin(rok))

                # Filtr pro týden nebo měsíc
                if time_selection == 'Vybrat týden' and 'tyden' in locals() and tyden:
                    mask = mask & (df['Týden'].isin(tyden))
                elif time_selection == 'Vybrat měsíc' and 'mesic' in locals() and mesic:
                    mask = mask & (df['Měsíc'].isin(mesic))

                # Filtr pro svátky
                if svatky:
                    mask = mask & (df['Svátky'].isin(svatky))

                # Filtr pro den
                if den:
                    mask = mask & (df['Den'].isin(den))

                # Aktualizace hodnot strojních hodin
                if mask.any():
                    df.loc[mask, 'Nabídka (stroje) [h]'] = nabidka_stroje
                    st.success('Strojní hodiny byly aktualizovány.')
                else:
                    st.error('Žádné záznamy neodpovídají zadaným filtrům.')
                    
        # ---------------------------------------------------------------------
        # ZOBRAZOVÁNÍ STROJNÍCH HODIN -----------------------------------------
        
        # Zobrazení výsledného grafu
        st.markdown("---")
        st.subheader("Graf nabídky pro kontrolu")
        selected_nazev = st.selectbox('Vyber pracoviště pro graf:', options=df['název'].dropna().unique())
        selected_year = st.selectbox('Vyber rok:', options=df['Rok'].dropna().unique())
        graph_option = st.radio("Zvol typ dat pro graf:", ("Nabídka (stroje) [h]", "Nabídka (lidi) [h]"))

        # Filtrování dat pro graf
        filtered_df = df[(df['název'] == selected_nazev) & (df['Rok'] == selected_year)].copy()
        filtered_df['Datum'] = pd.to_datetime(filtered_df['Datum'], format='%d.%m.%Y', errors='coerce')
        # Ošetření případů, kdy se nepodaří převést datum
        filtered_df.dropna(subset=['Datum'], inplace=True)

        # Skupina po týdnech
        weekly_grouped = filtered_df.groupby('Týden').agg({graph_option: 'sum'}).reset_index()

        fig, ax = plt.subplots(figsize=(16, 5))
        ax.bar(weekly_grouped['Týden'], weekly_grouped[graph_option], width=0.6, color='skyblue')
        ax.set_title(f'{graph_option} pro {selected_nazev} (týdny, rok {selected_year})', color='white')
        ax.set_xlabel('Týden', color='white')
        ax.set_ylabel('Hodiny', color='white')

        ax.yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray')
        ax.xaxis.grid(False)

        ax.set_xticks(weekly_grouped['Týden'])
        ax.set_xticklabels([f'{int(x)}' for x in weekly_grouped['Týden']], rotation=0, ha='center', fontsize=10)

        ax.set_facecolor('#0e1117')
        fig.patch.set_facecolor('#0e1117')
        ax.tick_params(colors='white', which='both')
        st.pyplot(fig)

        st.markdown("---")
        st.subheader("Stažení aktualizovaného souboru")

        # Uložení upraveného dataframe zpět do session state
        st.session_state['df'] = df

        # Odebrání nechtěných sloupců
        df_to_download = df.drop(columns=['pracoviště', 'proces', 'podproces', 'název'], errors='ignore')

        # Příprava dat k stažení s UTF-8 BOM
        csv_data = df_to_download.to_csv(index=False, sep=';', decimal=',', encoding='utf-8')

        # Generování odkazu pro stažení
        st.download_button(
            label="Stáhnout Workhours.csv",
            data=csv_data,
            file_name="Workhours.csv",
            mime='text/csv'
        )
        st.success("Soubor je připraven ke stažení.")

    else:
        st.warning("Nejprve nahrajte soubory v sekci 'Nahrávání souborů'.")

# -----------------------------------------------------------------------------
# ÚPRAVA LIDSKÝCH HODIN -------------------------------------------------------

def edit_data_lidi():
    st.title("Úprava lidských hodin")
    if 'df' in st.session_state:

        # Načtení dataframe
        df = st.session_state['df']

        # Výběr typu filtrování
        st.subheader("Výběr pracoviště:")
        filter_type = st.radio(
            "Zvolte, zda chcete pracovat s konkrétním pracovištěm, skupinou, nebo procesem:",
            ("Pracoviště (název)", "Skupina pracovišť (podproces)", "Celý proces")
        )

        selected_names = []
        selected_subprocesses = []
        selected_processes = []

        # Výběr podle zvoleného typu
        if filter_type == "Pracoviště (název)":
            selected_names = st.multiselect('Vyber jedno nebo více pracovišť (názvy pracovišť):', df['název'].dropna().unique())
        elif filter_type == "Skupina pracovišť (podproces)":
            selected_subprocesses = st.multiselect('Vyber jednu nebo více skupin (podprocesy):', df['podproces'].dropna().unique())
        else:  # c) Celý proces
            selected_processes = st.multiselect('Vyber jeden nebo více výrobních procesů:', df['proces'].dropna().unique())

        st.markdown("""
                    ---
                    ## Lidské hodiny
                    """)

        col1, col2 = st.columns([1, 1], gap="large")

        # Vytvoření widgetů pro výběr roků, měsíc/týden, dny/svátky
        with col1:
            st.subheader("Výběr dnů:")
            rok = st.multiselect('Vyber rok:', options=df['Rok'].unique())

            # zvolit měsíc nebo týden
            time_selection = st.radio("Vyberte, zda chcete filtrovat podle týdne nebo měsíce:", ("Vybrat týden", "Vybrat měsíc"))
            if time_selection == "Vybrat týden":
                tyden = st.multiselect('Vyber týden:', options=df['Týden'].dropna().unique())
            else:
                mesic = st.multiselect('Vyber měsíc:', options=df['Měsíc'].dropna().unique())

            st.markdown("---")

            svatky = st.multiselect('Svátky, víkend, pracovní den:', options=df['Svátky'].dropna().unique(), default=None)

            dni_v_tydnu = ['Po', 'Út', 'St', 'Čt', 'Pá', 'So', 'Ne']
            available_days = [day for day in dni_v_tydnu if day in df['Den'].unique()]
            den = st.multiselect('Vyber den:', options=available_days)

        # Vstupní pole pro zadání nové hodnoty lidských hodin
        with col2:
            st.subheader("Nová hodnota:")
            nabidka_lidi = st.number_input('LIDSKÉ HODINY', min_value=0.0, format="%.2f", key='nabidka_lidi_input')

            # Tlačítko pro aktualizaci dat
            if st.button('Aktualizovat lidské hodiny'):
                mask = pd.Series([True] * len(df))  # výchozí maska (všude True)

                # Filtrování podle typu
                if filter_type == "Pracoviště (název)" and selected_names:
                    mask = mask & (df['název'].isin(selected_names))
                elif filter_type == "Skupina pracovišť (podproces)" and selected_subprocesses:
                    mask = mask & (df['podproces'].isin(selected_subprocesses))
                elif filter_type == "Celý proces" and selected_processes:
                    mask = mask & (df['proces'].isin(selected_processes))

                # Filtr pro rok
                if rok:
                    mask = mask & (df['Rok'].isin(rok))

                # Filtr pro týden nebo měsíc
                if time_selection == 'Vybrat týden' and 'tyden' in locals() and tyden:
                    mask = mask & (df['Týden'].isin(tyden))
                elif time_selection == 'Vybrat měsíc' and 'mesic' in locals() and mesic:
                    mask = mask & (df['Měsíc'].isin(mesic))

                # Filtr pro svátky
                if svatky:
                    mask = mask & (df['Svátky'].isin(svatky))

                # Filtr pro den
                if den:
                    mask = mask & (df['Den'].isin(den))

                # Aktualizace hodnot lidských hodin
                if mask.any():
                    df.loc[mask, 'Nabídka (lidi) [h]'] = nabidka_lidi
                    st.success('Lidské hodiny byly aktualizovány.')
                else:
                    st.error('Žádné záznamy neodpovídají zadaným filtrům.')
                    
        # ---------------------------------------------------------------------
        # ZOBRAZOVÁNÍ LIDSKÝCH HODIN ------------------------------------------
        
        # Zobrazení výsledného grafu
        st.markdown("---")
        st.subheader("Graf nabídky pro kontrolu")
        selected_nazev = st.selectbox('Vyber pracoviště pro graf:', options=df['název'].dropna().unique())
        selected_year = st.selectbox('Vyber rok:', options=df['Rok'].dropna().unique())
        graph_option = st.radio("Zvol typ dat pro graf:", ("Nabídka (lidi) [h]", "Nabídka (stroje) [h]"))

        # Filtrování dat pro graf
        filtered_df = df[(df['název'] == selected_nazev) & (df['Rok'] == selected_year)].copy()
        filtered_df['Datum'] = pd.to_datetime(filtered_df['Datum'], format='%d.%m.%Y', errors='coerce')
        # Ošetření případů, kdy se nepodaří převést datum
        filtered_df.dropna(subset=['Datum'], inplace=True)

        # Skupina po týdnech
        weekly_grouped = filtered_df.groupby('Týden').agg({graph_option: 'sum'}).reset_index()

        fig, ax = plt.subplots(figsize=(16, 5))
        ax.bar(weekly_grouped['Týden'], weekly_grouped[graph_option], width=0.6, color='skyblue')
        ax.set_title(f'{graph_option} pro {selected_nazev} (týdny, rok {selected_year})', color='white')
        ax.set_xlabel('Týden', color='white')
        ax.set_ylabel('Hodiny', color='white')

        ax.yaxis.grid(True, linestyle='--', linewidth=0.5, color='gray')
        ax.xaxis.grid(False)

        ax.set_xticks(weekly_grouped['Týden'])
        ax.set_xticklabels([f'{int(x)}' for x in weekly_grouped['Týden']], rotation=0, ha='center', fontsize=10)

        ax.set_facecolor('#0e1117')
        fig.patch.set_facecolor('#0e1117')
        ax.tick_params(colors='white', which='both')
        st.pyplot(fig)

        st.markdown("---")
        st.subheader("Stažení aktualizovaného souboru")

        # Uložení upraveného dataframe zpět do session state
        st.session_state['df'] = df

        # Odebrání nechtěných sloupců
        df_to_download = df.drop(columns=['pracoviště', 'proces', 'podproces', 'název'], errors='ignore')

        # Příprava dat k stažení s UTF-8 BOM
        csv_data = df_to_download.to_csv(index=False, sep=';', decimal=',', encoding='utf-8')

        # Generování odkazu pro stažení
        st.download_button(
            label="Stáhnout Workhours.csv",
            data=csv_data,
            file_name="Workhours.csv",
            mime='text/csv'
        )
        st.success("Soubor je připraven ke stažení.")

    else:
        st.warning("Nejprve nahrajte soubory v sekci 'Nahrávání souborů'.")

# -----------------------------------------------------------------------------
# MAIN ------------------------------------------------------------------------

def main():
    st.sidebar.title("Menu:")
    menu = st.sidebar.radio("Vyberte sekci", ["Návod", "Nahrávání souborů", "Úprava strojních hodin", "Úprava lidských hodin"])

    if menu == "Návod":
        show_instructions()
    elif menu == "Nahrávání souborů":
        upload_files()
    elif menu == "Úprava strojních hodin":
        edit_data_stroje()
    elif menu == "Úprava lidských hodin":
        edit_data_lidi()
        
if __name__ == "__main__":
    main()
