import streamlit as st
import re
import json
import base64
import requests
from html.parser import HTMLParser

# Lendo o token de forma segura via st.secrets
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_REPO = "paolivsantos/gerador-recordplus"
GITHUB_BRANCH = "main"
ARQUIVO_JSON_GITHUB = "rascunhos.json"

st.set_page_config(
    page_title="Gerador de HTML - RecordPlus",
    page_icon="📄",
    layout="wide"
)

# ---------------------------------------------------------
# FUNÇÕES DE INTEGRAÇÃO COM O GITHUB
# ---------------------------------------------------------
def carregar_rascunhos_github():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{ARQUIVO_JSON_GITHUB}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            file_data = response.json()
            file_content = base64.b64decode(file_data["content"]).decode("utf-8")
            return json.loads(file_content), file_data.get("sha")
        elif response.status_code == 404:
            return None, None
        else:
            return None, None
    except Exception:
        return None, None

def salvar_rascunhos_github(dados_dict, sha=None):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{ARQUIVO_JSON_GITHUB}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    conteudo_str = json.dumps(dados_dict, ensure_ascii=False, indent=4)
    conteudo_base64 = base64.b64encode(conteudo_str.encode("utf-8")).decode("utf-8")
    
    payload = {
        "message": "Auto-save de rascunhos via Gerador RecordPlus",
        "content": conteudo_base64,
        "branch": GITHUB_BRANCH
    }
    if sha:
        payload["sha"] = sha
        
    try:
        response = requests.put(url, headers=headers, json=payload)
        if response.status_code in [200, 201]:
            return True, response.json().get("content", {}).get("sha")
        else:
            return False, sha
    except Exception:
        return False, sha

# ---------------------------------------------------------
# INICIALIZAÇÃO DO ESTADO GLOBAL COM CALLBACK DE AUTO-SAVE
# ---------------------------------------------------------
if 'rascunhos' not in st.session_state:
    dados_git, sha_git = carregar_rascunhos_github()
    if dados_git:
        st.session_state.rascunhos = dados_git
        st.session_state.github_sha = sha_git
    else:
        st.session_state.rascunhos = {
            "Aviso de Privacidade": {"titulo": "Aviso de Privacidade RecordPlus", "secoes": []},
            "Termos de Uso": {"titulo": "Termos de Uso RecordPlus", "secoes": []},
            "Contrato de Assinatura": {"titulo": "Contrato de Assinatura RecordPlus", "secoes": []},
            "F.A.Q.": {"titulo": "F.A.Q.", "secoes": []}
        }
        st.session_state.github_sha = None

if 'github_sha' not in st.session_state:
    st.session_state.github_sha = None

if 'status_salvamento' not in st.session_state:
    st.session_state.status_salvamento = "Tudo salvo na nuvem ☁️"

# Função que será chamada automaticamente sempre que um campo for alterado
def disparar_autosave():
    sucesso, novo_sha = salvar_rascunhos_github(st.session_state.rascunhos, st.session_state.github_sha)
    if sucesso:
        st.session_state.github_sha = novo_sha
        st.session_state.status_salvamento = "Salvo automaticamente ☁️"
    else:
        st.session_state.status_salvamento = "Erro ao salvar na nuvem ⚠️"
