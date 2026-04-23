import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from schema_generator import generate_json_schema, generate_csv_sample

st.title("Herramienta de aplanamiento")
st.write("Convierte imagenes de tablas en muestras de CSV aplanadas.")


def clear_state():
    for key in ['schema', 'csv_sample', 'generating', 'generating_csv']:
        if key in st.session_state:
            del st.session_state[key]

table_image = st.file_uploader("Cargar imagen de tabla", type=["jpg", "jpeg", "png"], on_change=clear_state)

if table_image is not None:
    st.image(table_image, caption="Imagen de tabla cargada")

    if st.button("Generar esquema", disabled=st.session_state.get('generating', False)):
        st.session_state.generating = True
        st.rerun()

    if st.session_state.get('generating', False):
        with st.spinner("Generando esquema..."):
            st.session_state.schema = generate_json_schema(table_image.getvalue())
        st.session_state.generating = False
        st.rerun()

if 'schema' in st.session_state:
    st.subheader("Esquema JSON generado")
    for i, (level, values) in enumerate(st.session_state.schema.items()):
        # Indentation effect using columns
        indent_col, content_col = st.columns([max(0.01, 0.05 * i), 1]) 
        
        with content_col:
            # Expandable Node
            with st.expander(f"📁 {level}", expanded=True):
                
                # Display current tags using text_area to avoid shortening long values
                text_content = "\n".join(values)
                updated_text = st.text_area(
                    "Extracted Values (one per line):", 
                    value=text_content, 
                    key=f"ta_{level}",
                    height=max(100, len(values) * 30)
                )
                
                updated_values = [v.strip() for v in updated_text.split('\n') if v.strip()]
                
                # Update state if user modified the text
                if updated_values != values:
                    st.session_state.schema[level] = updated_values
                    st.rerun()

                # Quick Addition Input
                add_col1, add_col2 = st.columns([3, 1])
                with add_col1:
                    new_val = st.text_input("Añadir valor faltante", key=f"input_{level}", label_visibility="collapsed")
                with add_col2:
                    if st.button("Add", key=f"btn_{level}"):
                        if new_val and new_val not in st.session_state.schema[level]:
                            st.session_state.schema[level].append(new_val)
                            st.rerun()
    # 3. Add / Remove Level Controls
    st.write("---")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("➕ Añadir nivel"):
            # Calculate next level number based on current length
            next_num = len(st.session_state.schema) + 1
            st.session_state.schema[f'nv{next_num}'] = []
            st.rerun()

    with col2:
        if st.button("➖ Quitar último nivel") and len(st.session_state.schema) > 1:
            # Remove the highest nv level
            last_key = list(st.session_state.schema.keys())[-1]
            del st.session_state.schema[last_key]
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
        csv_df = pd.read_csv(pd.io.common.StringIO(st.session_state.csv_sample))
        st.dataframe(csv_df, use_container_width=True)