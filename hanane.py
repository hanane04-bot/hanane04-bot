import streamlit as st
import pandas as pd
from io import BytesIO

# Function to load data from Excel file with caching
@st.cache(allow_output_mutation=True)
def load_data(uploaded_file):
    excel_data = uploaded_file.read()
    df = pd.read_excel(BytesIO(excel_data))
    return df

# Function to save data to Excel file
def save_data(df, file_path):
    with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)

# Function to download the updated Excel file
def download_file(df, file_path):
    save_data(df, file_path)  # Save the final changes to the original file
    with open(file_path, "rb") as file:
        file_content = file.read()
    st.download_button(label="Télécharger le fichier mis à jour", data=file_content, file_name="updated_data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Custom CSS for styling
st.markdown(
    """
    <style>
    body {
        background-color: #f0f0f0;
        color: #333333;
        font-family: Arial, sans-serif;
        padding: 20px;
    }
    .stTextInput input {
        width: 100%;
        padding: 8px;
        margin-bottom: 10px;
        border: 1px solid #ccc;
        border-radius: 4px;
        box-sizing: border-box;
        font-size: 14px;
    }
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
    }
    .stButton > button:hover {
        background-color: #45a049;
    }
    .stHeader {
        margin-top: 20px;
        margin-bottom: 10px;
        font-size: 20px;
        font-weight: bold;
    }
    .stSuccessMessage {
        color: green;
        font-size: 16px;
        margin-top: 10px;
    }
    .stWarningMessage {
        color: orange;
        font-size: 16px;
        margin-top: 10px;
    }
    .stErrorMessage {
        color: red;
        font-size: 16px;
        margin-top: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Main Streamlit app
def main():
    st.title('AGENCE NATIONAL DES PORTS ')

    # Option for the user to upload an Excel file
    uploaded_file = st.file_uploader("Importer un fichier Excel", type=["xlsx", "xls"])

    if uploaded_file is not None:
        try:
            # Load data from the uploaded file
            df = load_data(uploaded_file)
            st.write("Contenu du fichier Excel importé :")
            st.write(df)  # Display the imported DataFrame

            # Store the DataFrame in session state for mutability
            if 'df' not in st.session_state:
                st.session_state.df = df

            # Save the original file path for saving modifications
            st.session_state.original_file_path = uploaded_file.name

        except Exception as e:
            st.markdown(f'<p class="stErrorMessage">Une erreur s\'est produite lors du chargement du fichier : {e}</p>', unsafe_allow_html=True)
    else:
        st.info('Veuillez importer un fichier Excel pour commencer.')

    # Section to filter data dynamically by column (Placed first)
    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown('<h2 class="stHeader"> Filtrer </h2>', unsafe_allow_html=True)

    if 'df' in st.session_state:
        column_to_filter = st.selectbox('Sélectionner la colonne pour le filtrage :', options=st.session_state.df.columns)

        if column_to_filter:
            unique_values = st.session_state.df[column_to_filter].unique()
            filter_value = st.selectbox(f'Sélectionner une valeur pour {column_to_filter} :', options=unique_values)

            if st.button('Filtrer'):
                if filter_value:
                    filtered_df = st.session_state.df[st.session_state.df[column_to_filter] == filter_value]
                    st.write(filtered_df)

    # Section to add a new entry
    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown('<h2 class="stHeader">Ajouter une nouvelle entrée </h2>', unsafe_allow_html=True)

    if 'df' in st.session_state:
        new_entry = {}
        for col in st.session_state.df.columns:
            new_entry[col] = st.text_input(f"{col}")

        if st.button('Ajouter'):
            # Check if the key (CODE LOCAL) already exists
            if new_entry['CODE LOCAL'] in st.session_state.df['CODE LOCAL'].values:
                st.markdown(f'<p class="stWarningMessage">Le CODE LOCAL "{new_entry["CODE LOCAL"]}" existe déjà. Veuillez utiliser une autre clé.</p>', unsafe_allow_html=True)
            else:
                st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_entry])], ignore_index=True)
                save_data(st.session_state.df, st.session_state.original_file_path)  # Save to original file
                st.markdown('<p class="stSuccessMessage">Nouvelle entrée ajoutée avec succès.</p>', unsafe_allow_html=True)

                # Refresh data in session state after modification
                st.session_state.df = pd.read_excel(st.session_state.original_file_path)

    # Section to modify an existing entry
    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown('<h2 class="stHeader">Modifier une entrée</h2>', unsafe_allow_html=True)

    if 'df' in st.session_state:
        key_to_modify = st.text_input('Entrer la clé pour modifier :')

        if st.button('Modifier'):
            if key_to_modify:
                found = False
                for index, row in st.session_state.df.iterrows():
                    if row['CODE LOCAL'] == key_to_modify:
                        for col in st.session_state.df.columns:
                            new_value = st.text_input(f"Nouvelle valeur pour '{col}'", value=row[col])
                            st.session_state.df.loc[index, col] = new_value
                        save_data(st.session_state.df, st.session_state.original_file_path)  # Save to original file
                        st.markdown(f'<p class="stSuccessMessage">Données pour la clé "{key_to_modify}" modifiées avec succès.</p>', unsafe_allow_html=True)
                        found = True
                        break

                if not found:
                    st.markdown(f'<p class="stWarningMessage">Aucune entrée trouvée avec la clé "{key_to_modify}".</p>', unsafe_allow_html=True)

            # Refresh data in session state after modification
            st.session_state.df = pd.read_excel(st.session_state.original_file_path)

    # Section to delete an existing entry
    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown('<h2 class="stHeader">Supprimer une entrée</h2>', unsafe_allow_html=True)

    if 'df' in st.session_state:
        key_to_delete = st.text_input('Entrer la clé pour supprimer :')

        if st.button('Supprimer'):
            if key_to_delete:
                st.session_state.df = st.session_state.df[st.session_state.df['CODE LOCAL'] != key_to_delete]
                save_data(st.session_state.df, st.session_state.original_file_path)  # Save to original file
                st.markdown(f'<p class="stSuccessMessage">Entrée avec la clé "{key_to_delete}" supprimée avec succès.</p>', unsafe_allow_html=True)

            # Refresh data in session state after deletion
            st.session_state.df = pd.read_excel(st.session_state.original_file_path)

    # Display updated DataFrame
    if 'df' in st.session_state:
        st.markdown('<hr>', unsafe_allow_html=True)
        st.markdown('<h2 class="stHeader">Données mises à jour</h2>', unsafe_allow_html=True)
        st.write(st.session_state.df)

    # Download button for updated file
    if 'df' in st.session_state:
        download_file(st.session_state.df, st.session_state.original_file_path)

if __name__ == "__main__":
    main()
