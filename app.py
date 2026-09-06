import streamlit as st

st.set_page_config(
    page_title="Gerador de HTML - RecordPlus",
    page_icon="📄",
    layout="wide"
)

# Estilização do painel do Streamlit
st.markdown("""
    <style>
    .stApp {
        background-color: #121212;
        color: #ffffff;
    }
    p, span, label, h1, h2, h3 {
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Gerador de HTML para Embed - RecordPlus")
st.write("Preencha os campos abaixo para atualizar o conteúdo mantendo exatamente o mesmo layout padrão.")

# Organização em abas ou seções para facilitar o preenchimento
with st.form("form_gerador"):
    st.subheader("Cabeçalho e Títulos")
    titulo_pagina = st.text_input("Título Principal da Página", "Aviso de Privacidade RecordPlus")
    
    st.subheader("Conteúdo Principal")
    paragrafo_intro = st.text_area(
        "Parágrafo introdutório",
        "O RecordPlus leva a sério a privacidade e reconhece que você se preocupa como utilizamos e compartilhamos das suas informações pessoais..."
    )
    
    # Botão para gerar o código
    submit_button = st.form_submit_button(label="Gerar HTML Final")

if submit_button:
    # Template HTML estruturado idêntico ao modelo fornecido, injetando os textos dinâmicos
    html_gerado = f"""<!DOCTYPE html>
<html data-theme="dark" lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, user-scalable=no">
    <title>RecordPlus | Vídeos, rádios, podcasts para você curtir como quiser.</title>
    <link id="icon" rel="icon" type="image/png" href="https://www.recordplus.com/content/images/faviconrecordplus.ico">
    <link href="https://www.recordplus.com/content/all.css" rel="stylesheet">
    <link rel="stylesheet" href="https://www.recordplus.com/content/theme.css">
    <link rel="stylesheet" href="https://www.recordplus.com/content/styles.css">
    <link rel="stylesheet" href="https://www.recordplus.com/content/help.css">
    <link rel="stylesheet" href="https://www.recordplus.com/content/Header.css">
</head>
<body>
    <div id="modal_container"></div>
    <div class="menu-overlay"></div>
    
    <div class="header">
        <div class="menu-left-wrapper">
            <a href="https://www.recordplus.com/">
                <img alt="Play PLUS" class="img-header" src="https://www.recordplus.com/content/images/im_logo_recordplus.png">
            </a>
        </div>
        <div class="buutton-login-wrapper">
            <p>Já possui conta?</p>
            <a class="main-button-transparent button-small" href="https://www.recordplus.com/account/login">
                Acesse
            </a>
        </div>
    </div>

    <div class="container-help mt-100">
        <h1 class="home-section-termos-title">{titulo_pagina}</h1>
        <span class="category-line-termos line-termos"></span>

        <p>{paragrafo_intro}</p>
        
        <!-- O restante da estrutura fixa ou dinâmica da página entra aqui -->
    </div>

    <footer data-theme="light">
        <div class="bottom-footer">
            <ul class="list-footer">
                <li><a href="https://www.recordplus.com/help/termosdeuso">Termos de Uso </a><span>|</span></li>
                <li><a href="https://www.recordplus.com/help/politica">Privacidade</a>  <span>|</span></li>
            </ul>
        </div>
    </footer>
</body>
</html>"""

    st.success("HTML gerado com sucesso!")
    
    # Exibe o código pronto para cópia
    st.subheader("Código HTML gerado:")
    st.code(html_gerado, language="html")
    
    # Visualização de como o bloco se comporta
    st.subheader("Pré-visualização:")
    st.markdown(html_gerado, unsafe_allow_html=True)
