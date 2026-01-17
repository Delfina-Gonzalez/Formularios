
import streamlit as st
import pandas as pd
from pathlib import Path

# Copio el proceso de carga-----------------------------------------------

# Raíz del proyecto
try:
    BASE_DIR = Path(__file__).parent
except NameError:
    BASE_DIR = Path.cwd()

DATA_DIR = BASE_DIR / "data"

# Carpeta de datos
DATA_DIR = BASE_DIR / "data"

# Buscar archivo Excel
excel_files = list(DATA_DIR.glob("*.xlsx"))

if not excel_files:
    raise FileNotFoundError("No se encontró ningún archivo .xlsx en la carpeta data")

# Tomamos el primero
excel_path = excel_files[0]

# Validar hojas existentes
xls = pd.ExcelFile(excel_path)
required_sheets = {
    "Formularios totales",
    "Formularios completados"
}

missing = required_sheets - set(xls.sheet_names)
if missing:
    raise ValueError(f"Faltan hojas requeridas: {missing}")

# Cargar hojas
df_formularios = pd.read_excel(
    excel_path,
    sheet_name="Formularios totales"
)

df_completados = pd.read_excel(
    excel_path,
    sheet_name="Formularios completados"
)
#----------------------------------------------------------------------
# Calculos y visualización en Streamlit
st.markdown("### 📝 Formularios pendientes por usuario")

# Todos los formularios obligatorios
df_forms = df_formularios[["id", "title"]].rename(
    columns={"id": "FormularioID", "title": "Formulario"}
)

# Usuarios disponibles (únicos)
usuarios = sorted(df_completados["userId"].unique())

usuario_sel = st.selectbox(
    "Seleccionar usuario",
    usuarios
)

# Formularios completados por el usuario seleccionado
forms_completados_usuario = df_completados.loc[
    df_completados["userId"] == usuario_sel,
    "parentId"
].unique()

# Faltantes
df_pendientes_usuario = df_forms[
    df_forms["FormularioID"].isin(forms_completados_usuario) == False
]

# Mostrar
if df_pendientes_usuario.empty:
    st.success(f"✅ El usuario {usuario_sel} completó todos los formularios obligatorios")
else:
    st.warning(f"Formularios pendientes: {len(df_pendientes_usuario)}")
    st.dataframe(
        df_pendientes_usuario[["FormularioID"]],
        use_container_width=True
    )

st.markdown("### Formularios pendientes por usuario (descargable)")

# Armar tabla de pendientes para TODOS los usuarios
pendientes = []

for user in df_completados["userId"].unique():
    completados = df_completados.loc[
        df_completados["userId"] == user,
        "parentId"
    ].unique()

    df_pend = df_forms[
        ~df_forms["FormularioID"].isin(completados)
    ].copy()

    df_pend["ID Usuario"] = user
    pendientes.append(df_pend)

df_pendientes_total = pd.concat(pendientes, ignore_index=True)

# Mostrar
st.dataframe(
    df_pendientes_total[["ID Usuario", "Formulario"]],
    use_container_width=True
)

# Opción de descargarlo
csv_forms = df_pendientes_total.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Descargar lista de formularios obligatorios",
    data=csv_forms,
    file_name='formularios_obligatorios.csv',
    mime='text/csv',
)
