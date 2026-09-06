import streamlit as st
import re

st.set_page_config(
    page_title="Gerador de HTML - RecordPlus",
    page_icon="📄",
    layout="wide"
)

st.title("Gerador de HTML Dinâmico - RecordPlus")
st.write("Adicione seções livremente. Use **negrito**, *itálico* ou links nos textos de forma simples.")

# Função simples para converter Markdown básico do usuário em tags HTML adequadas
def converter_markdown_para_html(texto):
    if not texto:
        return ""
    # Substitui links [Texto](URL) por <a href="URL" target="_blank">Texto</a>
    texto = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" target="_blank">\1</a>', texto)
    # Substitui **texto** por <b>texto</b> ou <strong>
    texto = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', texto)
    # Substitui *texto* por <i>texto</i>
    texto = re.sub(r'\*(.*?)\*', r'<i>\1</i>', texto)
    # Quebras de linha viram <br>
    texto = texto.replace('\n', '<br>')
    return texto

# Configurações globais do documento
with st.sidebar:
    st.header("Configurações da Página")
    titulo_principal = st.text_input("Título Principal da Página", "Aviso de Privacidade RecordPlus")

# Gerenciamento dinâmico de seções (adicionar/remover blocos)
st.subheader("Conteúdo e Seções da Página")

if 'secoes' not in st.session_state:
    st.session_state.secoes = [{'tipo': 'Título e Parágrafo', 'titulo': 'Atualizações', 'conteudo': 'Digite seu texto aqui...'}]

# Botão para adicionar nova seção na tela
if st.button("➕ Adicionar Nova Seção"):
    st.session_state.secoes.append({'tipo': 'Título e Parágrafo', 'titulo': '', 'conteudo': ''})

html_secoes_geradas = ""

# Renderiza os inputs para cada seção criada
for i, secao in enumerate(st.session_state.secoes):
    with st.expander(f"Seção {i+1}: {secao['titulo'] or 'Nova Seção'}", expanded=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.session_state.secoes[i]['titulo'] = st.text_input(f"Título da Seção {i+1}", value=secao['titulo'], key=f"tit_{i}")
            st.session_state.secoes[i]['conteudo'] = st.text_area(f"Texto da Seção {i+1} (Aceita **negrito**, *itálico* e links)", value=secao['conteudo'], key=f"cont_{i}")
        with col2:
            st.write("")
            st.write("")
            if st.button("🗑️ Remover", key=f"del_{i}"):
                st.session_state.secoes.pop(i)
                st.rerun()
        
        # Constrói o HTML desta seção específica usando o conversor
        t_sec = st.session_state.secoes[i]['titulo']
        c_sec = converter_markdown_para_html(st.session_state.secoes[i]['conteudo'])
        
        if t_sec:
            html_secoes_geradas += f"\n    <h3>{t_sec}</h3>"
        if c_sec:
            html_secoes_geradas += f"\n    <p>{c_sec}</p>\n"

# Botão para gerar o código final
if st.button("🚀 Gerar HTML Completo"):
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
        <h1 class="home-section-termos-title">{titulo_principal}</h1>
        <span class="category-line-termos line-termos"></span>
        {html_secoes_geradas}
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
    st.subheader("Código HTML final para cópia:")
    st.code(html_gerado, language="html")
