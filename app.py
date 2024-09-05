import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Chemin vers le sous-dossier raw_data
csv_file_path = './raw_data/notes_bac_2024.csv'

# Lecture du fichier CSV
df_csv = pd.read_csv(csv_file_path, sep=';', encoding='utf-8')

# Filtrer et renommer les colonnes
columns_to_keep = {
    'Division de classe': 'Classe',
    'Nom candidat': 'Nom',
    'Prénom candidat': 'Prenom',
    'T001 - 1 - Français écrit - Ponctuel': 'note_ecrit',
    'T002 - 1 - Français oral - Ponctuel': 'note_oral'
}
df_filtred = df_csv[list(columns_to_keep.keys())].rename(columns=columns_to_keep)

# Convertir les notes en numériques et supprimer les NaN
df_filtred['note_ecrit'] = pd.to_numeric(df_filtred['note_ecrit'], errors='coerce')
df_filtred['note_oral'] = pd.to_numeric(df_filtred['note_oral'], errors='coerce')
df_filtred = df_filtred.dropna(subset=['note_ecrit', 'note_oral'])

# Titre de l'application
st.title('Analyse des Résultats Bac Français 2024 - LFIAM')

# --- Partie 1 : Analyse globale ---
st.header('1. Analyse globale de tous les résultats')

# Créer deux colonnes
col1, col2 = st.columns([3, 2])

# Afficher le DataFrame global dans la première colonne
with col1:
    st.write("Résultats par élèves :")
    st.dataframe(df_filtred)


st.write("Distributions et comparaisons des notes d'écrit et d'oral : ")
# Afficher le résumé statistique global dans la deuxième colonne
with col2:
    st.write("Résumé statistique :")
    stats_summary = df_filtred[['note_ecrit', 'note_oral']].describe()
    st.dataframe(stats_summary)

# Créer une figure 2x2 pour les graphiques globaux
fig_global, axes = plt.subplots(2, 2, figsize=(16, 12))

# Définir les couleurs pour l'écrit et l'oral
color_ecrit = '#e9c46a'
color_oral = '#2a9d8f'

# 1. Histogramme de la distribution des notes d'écrit (global)
axes[0, 0].hist(df_filtred['note_ecrit'], bins=10, color=color_ecrit, edgecolor='black')
axes[0, 0].set_title('Répartition des notes d\'écrit', fontsize=14)
axes[0, 0].set_xlabel('Note')
axes[0, 0].set_ylabel('Nombre d\'élèves')

# 2. Histogramme de la distribution des notes d'oral (global)
axes[0, 1].hist(df_filtred['note_oral'], bins=10, color=color_oral, edgecolor='black')
axes[0, 1].set_title('Répartition des notes d\'oral', fontsize=14)
axes[0, 1].set_xlabel('Note')
axes[0, 1].set_ylabel('Nombre d\'élèves')

# 3. Boxplot des notes d'écrit et d'oral (global)
sns.boxplot(data=df_filtred[['note_ecrit', 'note_oral']], palette=[color_ecrit, color_oral], ax=axes[1, 0])
axes[1, 0].set_title('Boxplot des notes d\'écrit et d\'oral', fontsize=14)

# 4. Barplot des moyennes des notes d'écrit et d'oral (global)
moyennes = df_filtred[['note_ecrit', 'note_oral']].mean()
sns.barplot(x=moyennes.index, y=moyennes.values, palette=[color_ecrit, color_oral], ax=axes[1, 1])
axes[1, 1].set_title('Comparaison des moyennes des notes', fontsize=14)
axes[1, 1].set_ylabel('Moyenne')

plt.tight_layout()
st.pyplot(fig_global)

st.markdown("""
### Analyse des performances en écrit et en oral :

- **Hétérogénéité à l'oral** : Les élèves ont de meilleures moyennes à l'oral, mais la différence entre les notes minimales et maximales est plus marquée (3 à 20) qu'à l'écrit (7 à 20), indiquant une plus grande variabilité.
- **Concentration à l'écrit** : Les notes d'écrit sont plus homogènes, concentrées autour de 8 à 14, avec moins de dispersion.
- **Performance générale** : Les élèves réussissent mieux à l'oral, mais l'écart des performances montre que certains excellent tandis que d'autres rencontrent des difficultés.
""")


# --- Partie 2 : Analyse filtrée par classe ---
st.header('2. Analyse par classe')

# # Sidebar pour filtrer par classe
# classe_list = df_filtred['Classe'].unique()
# classe_selection = st.sidebar.multiselect("Sélectionnez les classes à afficher", classe_list, default=classe_list)

# Filtrer par classe dans la page principale
classe_list = df_filtred['Classe'].unique()
classe_selection = st.multiselect("Sélectionnez les classes à afficher", classe_list, default=classe_list)


# Filtrer le dataframe en fonction des classes sélectionnées
df_filtered_by_classe = df_filtred[df_filtred['Classe'].isin(classe_selection)]

# Calcul des indicateurs (moyenne, écart-type, min, max) pour chaque classe
indicateurs_par_classe = df_filtered_by_classe.groupby('Classe').agg({
    'note_ecrit': ['mean', 'std', 'min', 'max'],
    'note_oral': ['mean', 'std', 'min', 'max']
}).reset_index()

# Arrondir les valeurs à 2 décimales et renommer les colonnes pour plus de clarté
indicateurs_par_classe.columns = ['Classe', 'Moyenne Écrit', 'Écart-type Écrit', 'Min Écrit', 'Max Écrit',
                                  'Moyenne Oral', 'Écart-type Oral', 'Min Oral', 'Max Oral']
indicateurs_par_classe = indicateurs_par_classe.round(2)

# Afficher le DataFrame des indicateurs par classe
st.write("Indicateurs par classe :")
st.dataframe(indicateurs_par_classe)

# Fusionner les notes d'écrit et d'oral dans un format long pour le boxplot
df_melted = df_filtered_by_classe.melt(id_vars=['Classe'], value_vars=['note_ecrit', 'note_oral'],
                                       var_name='Type de Note', value_name='Note')
df_melted['Type de Note'] = df_melted['Type de Note'].replace({'note_ecrit': 'Écrit', 'note_oral': 'Oral'})

# Configurer une figure avec deux graphiques empilés l'un sur l'autre
fig_classe, axes = plt.subplots(2, 1, figsize=(12, 12))

# 1. Barplot des moyennes des notes d'écrit et d'oral par classe
indicateurs_par_classe.set_index('Classe')[['Moyenne Écrit', 'Moyenne Oral']].plot(kind='bar', ax=axes[0], color=[color_ecrit, color_oral])
axes[0].set_title('Moyennes des notes par classe')
axes[0].set_ylabel('Moyenne')

# 2. Boxplot pour chaque classe avec deux boxplots (écrit et oral)
sns.boxplot(data=df_melted, x='Classe', y='Note', hue='Type de Note', palette=[color_ecrit, color_oral], ax=axes[1])
axes[1].set_title('Comparaison des notes d\'écrit et d\'oral par classe')
axes[1].set_xlabel('Classe')
axes[1].set_ylabel('Note')
axes[1].legend(title='Type de Note')

# Afficher le tout
plt.tight_layout()
st.pyplot(fig_classe)
