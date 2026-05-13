import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from schema_generator import generate_json_schema, generate_csv_sample
from prompt import JSON_SCHEMA_PROMPT_CATEGORY_1, JSON_SCHEMA_PROMPT_CATEGORY_2, JSON_SCHEMA_PROMPT_CATEGORY_3, JSON_SCHEMA_PROMPT_CATEGORY_4
from pandas.errors import ParserError
import re

PROMPT_MAP = {
    "Categoría 1: Tablas simples": JSON_SCHEMA_PROMPT_CATEGORY_1,
    "Categoría 2: Filas compuestas": JSON_SCHEMA_PROMPT_CATEGORY_2,
    "Categoría 3: Columnas compuestas": JSON_SCHEMA_PROMPT_CATEGORY_3,
    "Categoría 4: Mixto (Filas y columnas compuestas)": JSON_SCHEMA_PROMPT_CATEGORY_4,
}

st.title("Herramienta de aplanamiento")
st.write("Convierte imagenes de tablas en muestras de CSV aplanadas.")


def clear_state():
    for key in ['schema', 'csv_sample', 'generating', 'generating_csv']:
        if key in st.session_state:
            del st.session_state[key]


def extract_csv_text(raw_text: str) -> str:
    text = raw_text.strip()
    fence_match = re.search(r"```(?:csv)?\s*(.*?)\s*```", text, flags=re.IGNORECASE | re.DOTALL)
    if fence_match:
        text = fence_match.group(1).strip()
    return text

table_image = st.file_uploader("Cargar imagen de tabla", type=["jpg", "jpeg", "png"], on_change=clear_state)

if table_image is not None:
    st.image(table_image, caption="Imagen de tabla cargada")

    selected_category = st.selectbox("Seleccionar Categoría", list(PROMPT_MAP.keys()))

    if st.button("Generar esquema", disabled=st.session_state.get('generating', False)):
        st.session_state.generating = True
        st.rerun()

    if st.session_state.get('generating', False):
        with st.spinner("Generando esquema..."):
            st.session_state.schema = generate_json_schema(table_image.getvalue(), PROMPT_MAP[selected_category])
        st.session_state.generating = False
        st.rerun()

if 'schema' in st.session_state:
    st.subheader("Esquema JSON generado")
    
    keys = list(st.session_state.schema.keys())
    num_cols = max(1, len(keys))
    cols = st.columns(num_cols)
    level_to_delete = None
    
    for i, level in enumerate(keys):
        values = st.session_state.schema[level]
        with cols[i]:
            header_col, del_col = st.columns([3, 1])
            with header_col:
                st.markdown(f"**📁 {level}**")
            with del_col:
                if st.button("❌", key=f"del_{level}"):
                    level_to_delete = level

            text_content = "\n".join(values)
            updated_text = st.text_area(
                "Extracted Values (one per line):", 
                value=text_content, 
                key=f"ta_{level}",
                height=max(100, len(values) * 30),
                label_visibility="collapsed"
            )
            
            updated_values = [v.strip() for v in updated_text.split('\n') if v.strip()]
            
            if updated_values != values:
                st.session_state.schema[level] = updated_values
                st.rerun()

            add_col1, add_col2 = st.columns([3, 1])
            with add_col1:
                new_val = st.text_input("Añadir valor", key=f"input_{level}", label_visibility="collapsed")
            with add_col2:
                if st.button("Add", key=f"btn_{level}"):
                    if new_val and new_val not in st.session_state.schema[level]:
                        st.session_state.schema[level].append(new_val)
                        st.rerun()

    if level_to_delete:
        del st.session_state.schema[level_to_delete]
        new_schema = {}
        for idx, (k, v) in enumerate(st.session_state.schema.items(), start=1):
            new_schema[f"nv{idx}"] = v
        st.session_state.schema = new_schema
        st.rerun()

    st.write("---")
    if st.button("➕ Añadir nivel"):
        next_num = len(st.session_state.schema) + 1
        st.session_state.schema[f'nv{next_num}'] = []
        st.rerun()

    st.write("---")
    if st.button("Aprobar esquema", disabled=st.session_state.get('generating_csv', False)):
        st.session_state.generating_csv = True
        st.rerun()

    if st.session_state.get('generating_csv', False):
        with st.spinner("Generando muestra CSV..."):
            st.session_state.csv_sample = generate_csv_sample(table_image.getvalue(), st.session_state.schema)
        st.session_state.generating_csv = False
        st.rerun()
        
    if 'csv_sample' in st.session_state:
        st.subheader("Muestra de CSV generada")
        csv_text = extract_csv_text(st.session_state.csv_sample)

        try:
            csv_df = pd.read_csv(
                pd.io.common.StringIO(csv_text),
                engine="python",
                on_bad_lines="warn",
            )
            st.dataframe(csv_df, use_container_width=True)
        except (ParserError, ValueError):
            st.warning("No se pudo interpretar la muestra como CSV válido. Se muestra el texto original.")
            st.code(csv_text, language="csv")