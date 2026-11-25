import streamlit as st

st.title("5th Class")


import streamlit as st

# Configuración de la página
st.title("Práctica de componentes de Streamlit")

# -----------------------------
# CHECKBOX Y RADIO BUTTON
# -----------------------------

def change():
    print(st.session_state.checker)

st.subheader("1. Checkbox")

state = st.checkbox(
    "Checkbox",
    value=True,
    on_change=change,
    key="checker"
)

st.write("Estado del checkbox:", state)


st.subheader("2. Radio Button")

radio_btn = st.radio(
    "In which country do you live?",
    options=("Guatemala", "México", "Estados Unidos", "España")
)

st.write("País seleccionado:", radio_btn)


# -----------------------------
# BUTTON Y SELECTBOX
# -----------------------------

def btn_click():
    print("Button Clicked")

st.subheader("3. Button")

if st.button("Click me!"):
    btn_click()
    st.success("¡Button Clicked!")


st.subheader("4. Selectbox")

select = st.selectbox(
    "What is your favorite car?",
    options=("Ferrari", "Ford", "Toyota")
)

st.write("Your favorite car is:", select)
