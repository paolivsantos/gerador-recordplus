import streamlit as st

# Configuração da página (deve ser o primeiro comando do Streamlit)
st.set_page_config(
    page_title="Meu Projeto Streamlit",
    page_icon="🎨",
    layout="wide"
)

# Injeção de CSS personalizado
st.markdown("""
    <style>
    /* Fundo geral da aplicação e cor do texto */
    .stApp {
        background-color: #121212;
        color: #ffffff;
    }
    
    /* Forçar cor de textos gerais para branco */
    p, span, label, h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    
    /* Links personalizados */
    a, a:visited {
        color: #AF68BA !important;
        text-decoration: underline;
    }
    
    a:hover {
        color: #c782d1 !important;
    }
    
    /* Estilização para tabelas e containers */
    .table-container {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    
    th {
        background-color: #2c2c2c !important;
        color: #ffffff !important;
        border-bottom: 2px solid #444444 !important;
    }
    
    td {
        border-bottom: 1px solid #333333 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Conteúdo principal da aplicação
st.title("Painel do Projeto")
st.write("Este é o seu ambiente configurado com o tema escuro e os links customizados.")

# Exemplo de link interativo
st.markdown("Confira mais detalhes acessando a [documentação do Streamlit](https://docs.streamlit.io).")

# Exemplo de componente interativo simples
nome = st.text_input("Digite o seu nome:")
if nome:
    st.success(f"Seja bem-vindo, {nome}!")
