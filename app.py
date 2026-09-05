import streamlit as st

st.set_page_config(
    page_title="Gerador de HTML Personalizado",
    page_icon="🛠️",
    layout="wide"
)

# Estilização da interface do Streamlit para manter o padrão escuro
st.markdown("""
    <style>
    .stApp {
        background-color: #121212;
        color: #ffffff;
    }
    p, span, label, h1, h2, h3 {
        color: #ffffff !important;
    }
    a {
        color: #AF68BA !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Gerador de HTML com Diretrizes Visuais")
st.write("Insira seu texto ou conteúdo abaixo para gerar o bloco HTML estilizado com o fundo escuro, texto branco e links em `#AF68BA`.")

# Área de entrada do texto pelo usuário
texto_usuario = st.text_area("Digite o conteúdo do texto:", "Exemplo: Acesse nosso portal em https://exemplo.com para mais detalhes.")

# Opção para formatar links automaticamente se houver URLs no texto
def aplicar_estilos_html(texto):
    # Estrutura base do HTML seguindo as diretrizes
    html_gerado = f"""
<div style="background-color: #121212; color: #ffffff; font-family: Arial, sans-serif; padding: 20px;">
    <p style="color: #ffffff; line-height: 1.6;">{texto.replace('\n', '<br>')}</p>
</div>
<style>
    a, a:visited {{
        color: #AF68BA !important;
        text-decoration: underline;
    }}
    a:hover {{
        color: #c782d1 !important;
    }}
    .table-container {{
        background-color: #1e1e1e;
        color: #ffffff;
    }}
    th {{
        background-color: #2c2c2c !important;
        color: #ffffff !important;
        border-bottom: 2px solid #444444 !important;
    }}
    td {{
        border-bottom: 1px solid #333333 !important;
    }}
</style>
"""
    return html_gerado.strip()

if texto_usuario:
    html_resultado = aplicar_estilos_html(texto_usuario)
    
    st.subheader("HTML Gerado:")
    st.code(html_resultado, language="html")
    
    st.subheader("Pré-visualização:")
    st.markdown(html_resultado, unsafe_allow_html=True)
