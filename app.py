import streamlit as st
import re

st.set_page_config(
    page_title="Gerador de HTML - RecordPlus",
    page_icon="📄",
    layout="wide"
)

st.title("Gerador de HTML Dinâmico - RecordPlus")
st.write("Crie e ajuste o conteúdo da página estruturando seções, listas e tabelas de forma simples.")

# Guia de Formatação
with st.expander("💡 Guia Rápido de Formatação", expanded=True):
    st.markdown("""
    Você pode usar formatações simples nos campos de texto para estilizar o conteúdo:
    * **Negrito**: Use `**palavra ou frase**` (Ex: `O **RecordPlus** é seguro`)
    * **Itálico**: Use `*palavra ou frase*` (Ex: `*Atenção aos prazos*`)
    * **Links**: Use `[Texto do Link](https://exemplo.com)`
    * **Listas**: Inicie as linhas com `-` ou `*` para criar itens em lista.
    * **Tabelas**: Insira o cabeçalho separado por vírgulas e as linhas logo abaixo.
    """)

def converter_texto_para_html(texto):
    if not texto:
        return ""
    
    linhas = texto.split('\n')
    html_linhas = []
    dentro_de_lista = False

    for linha in linhas:
        linha_strip = linha.strip()

        if linha_strip.startswith('- ') or linha_strip.startswith('* '):
            if not dentro_de_lista:
                html_linhas.append('<ul>')
                dentro_de_lista = True
            
            item_texto = linha_strip[2:]
            item_texto = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" target="_blank">\1</a>', item_texto)
            item_texto = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', item_texto)
            item_texto = re.sub(r'\*(.*?)\*', r'<i>\1</i>', item_texto)
            
            html_linhas.append(f'    <li>{item_texto}</li>')
            continue
        else:
            if dentro_de_lista:
                html_linhas.append('</ul>')
                dentro_de_lista = False

        if not linha_strip:
            continue

        linha = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" target="_blank">\1</a>', linha)
        linha = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', linha)
        linha = re.sub(r'\*(.*?)\*', r'<i>\1</i>', linha)
        
        html_linhas.append(f'<p>{linha}</p>')

    if dentro_de_lista:
        html_linhas.append('</ul>')

    return '\n'.join(html_linhas)

with st.sidebar:
    st.header("Configurações da Página")
    titulo_principal = st.text_input("Título Principal da Página", "Aviso de Privacidade RecordPlus")

if 'secoes' not in st.session_state:
    st.session_state.secoes = []

st.subheader("Conteúdo e Seções da Página")

col_b1, col_b2 = st.columns(2)
with col_b1:
    if st.button("➕ Adicionar Seção de Texto/Lista"):
        st.session_state.secoes.append({'tipo': 'texto', 'titulo': '', 'conteudo': ''})
with col_b2:
    if st.button("📊 Adicionar Tabela"):
        st.session_state.secoes.append({'tipo': 'tabela', 'titulo': '', 'cabecalho': '', 'linhas': ''})

html_secoes_geradas = ""

if not st.session_state.secoes:
    st.info("Nenhuma seção adicionada ainda. Clique nos botões acima para começar a montar a página.")

for i, secao in enumerate(st.session_state.secoes):
    tipo_atual = secao.get('tipo', 'texto')
    num_secao = i + 1
    titulo_exibicao = secao['titulo'].strip() if secao['titulo'] else "Nova Seção"
    
    if tipo_atual == 'texto':
        with st.expander(f"Seção {num_secao} [Texto/Lista]: {titulo_exibicao}", expanded=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.session_state.secoes[i]['titulo'] = st.text_input(f"Título da Seção {num_secao}", value=secao['titulo'], key=f"tit_{i}")
                st.session_state.secoes[i]['conteudo'] = st.text_area(f"Conteúdo (Aceita **negrito**, *itálico*, links e listas com -)", value=secao['conteudo'], key=f"cont_{i}", height=120)
            with col2:
                st.write("")
                st.write("")
                if st.button("🗑️ Remover", key=f"del_{i}"):
                    st.session_state.secoes.pop(i)
                    st.rerun()
            
            t_sec = st.session_state.secoes[i]['titulo']
            c_sec = converter_texto_para_html(st.session_state.secoes[i]['conteudo'])
            
            if t_sec:
                html_secoes_geradas += f"\n    <h3>{t_sec}</h3>"
            if c_sec:
                html_secoes_geradas += f"\n    {c_sec}\n"

    elif tipo_atual == 'tabela':
        with st.expander(f"Seção {num_secao} [Tabela]: {titulo_exibicao}", expanded=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.session_state.secoes[i]['titulo'] = st.text_input(f"Título da Tabela {num_secao}", value=secao['titulo'], key=f"ttab_{i}")
                st.session_state.secoes[i]['cabecalho'] = st.text_input(f"Cabeçalho da Tabela (separado por vírgula)", value=secao.get('cabecalho', ''), key=f"cab_{i}")
                st.session_state.secoes[i]['linhas'] = st.text_area(f"Linhas da Tabela (cada linha em uma quebra, colunas separadas por vírgula)", value=secao.get('linhas', ''), key=f"lin_{i}", height=100)
            with col2:
                st.write("")
                st.write("")
                if st.button("🗑️ Remover", key=f"del_{i}"):
                    st.session_state.secoes.pop(i)
                    st.rerun()
            
            t_tab = st.session_state.secoes[i]['titulo']
            cab_tab = [c.strip() for c in st.session_state.secoes[i]['cabecalho'].split(',')] if st.session_state.secoes[i]['cabecalho'] else []
            linhas_raw = st.session_state.secoes[i]['linhas'].split('\n') if st.session_state.secoes[i]['linhas'] else []
            
            html_tabela = ""
            if cab_tab or linhas_raw:
                html_tabela += '\n    <div class="table-container">\n        <table>'
                if cab_tab:
                    html_tabela += '\n            <thead>\n                <tr>'
                    for th in cab_tab:
                        html_tabela += f'\n                    <th>{th}</th>'
                    html_tabela += '\n                </tr>\n            </thead>'
                
                html_tabela += '\n            <tbody>'
                for l in linhas_raw:
                    if l.strip():
                        colunas = [col.strip() for col in l.split(',')]
                        html_tabela += '\n                <tr>'
                        for idx, td in enumerate(colunas):
                            if idx == 0:
                                html_tabela += f'\n                    <td class="cookie-type">{td}</td>'
                            else:
                                html_tabela += f'\n                    <td class="cookie-description">{td}</td>'
                        html_tabela += '\n                </tr>'
                html_tabela += '\n            </tbody>\n        </table>\n    </div>\n'

            if t_tab:
                html_secoes_geradas += f"\n    <h3>{t_tab}</h3>"
            html_secoes_geradas += html_tabela

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
