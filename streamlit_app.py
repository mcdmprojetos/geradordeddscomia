import html
import json
import re
import unicodedata
import os
import base64
from pathlib import Path

import pandas as pd
import streamlit as st
try:
    from google import genai
except ImportError:
    genai = None

APP_DIR = Path(__file__).resolve().parent
PDF_FILE = APP_DIR / "Seleção_Inteligente_de_Textos_de_DDS.pdf"
CRITERIA = ["Seguranca", "EPIs", "Clareza", "Objetividade", "Aplicabilidade"]
LABELS = {"Seguranca": "Segurança", "EPIs": "EPIs", "Clareza": "Clareza",
          "Objetividade": "Objetividade", "Aplicabilidade": "Aplicabilidade"}

AUTHORS = [
    ("Prof. Doutoranda Jaqueline Alves", "Universidade Federal Fluminense (UFF)",
     [("LinkedIn", "https://www.linkedin.com/in/jaqueline-alves-cmb/"),
      ("Lattes", "http://lattes.cnpq.br/9581708310870285")]),
    ("Sabrina Alves Brito", "UVA | Desenvolvedora, Rede Globo Televisão",
     [("LinkedIn", "https://www.linkedin.com/in/sabrina-a-brito/")]),
    ("Prof. Dr. Rodrigo Caiado", "Pontifícia Universidade Católica do Rio de Janeiro (PUC-Rio)",
     [("LinkedIn", "https://www.linkedin.com/in/rodrigo-caiado-a7187938/"),
      ("Lattes", "http://lattes.cnpq.br/3922452850648712")]),
    ("Prof. Dr. Gilson Lima", "Universidade Federal Fluminense (UFF)",
     [("LinkedIn", "https://www.linkedin.com/in/gilson-lima-25808323/"),
      ("Lattes", "http://lattes.cnpq.br/2248567464602970")]),
]

st.set_page_config(page_title="DDS SmartSelect", page_icon="🦺", layout="wide",
                   initial_sidebar_state="collapsed")

st.markdown("""
<style>
:root{--navy:#082b4c;--blue:#0b5f9e;--pale:#edf6fc;--green:#16845b;
--gold:#e6a817;--ink:#17212b;--muted:#5d6b78;--line:#dce5ec}
.stApp{background:#f7f9fb;color:var(--ink)}
.block-container{max-width:1180px;padding-top:1.4rem;padding-bottom:2rem}
header[data-testid="stHeader"]{background:transparent} #MainMenu,footer{visibility:hidden}
.hero{padding:1rem 1.3rem;border-radius:18px;background:linear-gradient(125deg,#062946,#0b5f9e);
box-shadow:0 12px 30px rgba(8,43,76,.16);margin-bottom:1.1rem}
.hero-tag{display:inline-block;padding:.28rem .7rem;border:1px solid rgba(255,255,255,.35);
border-radius:999px;color:#fff;font-size:.78rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase}
.hero h1{color:#fff;font-size:1.85rem;margin:.4rem 0 .2rem}
.hero .hero-subtitle{color:#dceefa;font-size:1.15rem;font-weight:500;margin:0}
.hero p{color:#c9e1f1;margin:.8rem 0 0;max-width:800px}
.section-title{color:var(--navy);margin:1.3rem 0 .7rem}
.panel{background:#fff;border:1px solid var(--line);border-radius:14px;padding:1.15rem 1.25rem;
box-shadow:0 4px 16px rgba(8,43,76,.05)}
.method-flow{display:grid;grid-template-columns:repeat(5,1fr);gap:.6rem;margin:.7rem 0 1rem}
.method-step{min-height:96px;padding:.85rem .7rem;border-radius:12px;background:var(--pale);
border-top:4px solid var(--blue);text-align:center}
.step-number{color:var(--blue);font-weight:800;font-size:.76rem}
.step-title{color:var(--navy);font-weight:750;margin-top:.3rem}
.step-text{color:var(--muted);font-size:.82rem;margin-top:.22rem}
.winner-card{padding:1.35rem 1.5rem;background:linear-gradient(135deg,#effaf5,#fff);
border:1px solid #a8dcc7;border-left:7px solid var(--green);border-radius:14px;margin:.8rem 0 1rem}
.winner-kicker{color:var(--green);font-weight:800;text-transform:uppercase;font-size:.78rem}
.winner-title{color:#0e5139;font-size:1.45rem;font-weight:800;margin:.25rem 0 .65rem}
.dds-text{white-space:pre-line;line-height:1.65}.safety-note{background:#fff8e7;
border-left:5px solid var(--gold);border-radius:8px;padding:.85rem 1rem;color:#5b4817;margin:1rem 0}
.author-card{min-height:165px;background:#fff;border:1px solid var(--line);border-radius:12px;padding:1rem}
.author-name{color:var(--navy);font-weight:800}.author-affiliation{color:var(--muted);
font-size:.86rem;min-height:62px;margin:.3rem 0 .7rem}
.author-links a{color:var(--blue);font-weight:700;text-decoration:none;margin-right:.8rem}
.event-note{text-align:center;color:var(--muted);margin:1.2rem 0 .5rem;font-size:.9rem}
div.stButton>button,div.stDownloadButton>button{border-radius:9px;font-weight:700;min-height:44px}
div.stButton>button[kind="primary"]{background:var(--blue);border-color:var(--blue)}
[data-testid="stForm"]{background:#fff;border:1px solid var(--line);border-radius:14px;
padding:1.25rem;box-shadow:0 4px 16px rgba(8,43,76,.05)}
@media(max-width:1000px){
  .method-flow{grid-template-columns:repeat(2,1fr)}
  .author-card{min-height:auto}
}
@media(max-width:600px){
  .block-container{padding:1rem .8rem 1.5rem}
  .hero{padding:.75rem .9rem;border-radius:12px}
  .hero h1{font-size:1.75rem}.hero .hero-subtitle{font-size:1rem}
  .hero p{font-size:.92rem}
  .method-flow{grid-template-columns:1fr}
  .method-step{min-height:auto;text-align:left}
  .winner-card{padding:1rem;border-left-width:5px}
  .winner-title{font-size:1.2rem}
  div.stButton>button,div.stDownloadButton>button{width:100%;min-height:48px}
}
.logo-box {
    height: 130px;
    background: white;
    border: 1px solid #dce5ec;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 18px;
    overflow: hidden;
}

.logo-box img {
    width: 100%;
    height: 100%;
    object-fit: contain;
}

@media (max-width: 600px) {
    .logo-box {
        height: 105px;
        padding: 14px;
    }
}
a:focus-visible,button:focus-visible,input:focus-visible,textarea:focus-visible{
outline:3px solid #082b4c!important;outline-offset:3px!important}
.event-logo{display:block;width:100%;max-width:320px;height:130px;object-fit:contain;margin:.8rem auto}
.accessibility-note{font-size:.9rem;line-height:1.6;color:#17212b;background:#edf6fc;padding:1rem;border-radius:10px}
</style>""", unsafe_allow_html=True)


def parse_json_response(response_text: str, expected_start: str):
    cleaned = response_text.strip().replace("~~~json", "").replace("~~~", "").strip()
    cleaned = cleaned.replace(chr(96) * 3 + "json", "").replace(chr(96) * 3, "").strip()
    start = cleaned.find(expected_start)
    end = cleaned.rfind("}" if expected_start == "{" else "]")
    if start == -1 or end == -1 or end < start:
        raise ValueError("A resposta da IA não trouxe o JSON esperado.")
    return json.loads(cleaned[start:end + 1])


def generate_texts(client, profile: str, topic: str) -> dict:
    prompt = f"""
Você é especialista em Segurança do Trabalho e comunicação preventiva em ambientes profissionais.

Sua tarefa é elaborar quatro alternativas de Diálogo Diário de Segurança (DDS), em português do Brasil, adaptadas ao perfil dos profissionais e à situação informada.

PERFIL DOS PROFISSIONAIS:
{profile}

TEMA, SITUAÇÃO OU CONTEXTO:
{topic}

INSTRUÇÕES:
1. Crie 4 alternativas diferentes de DDS sobre o mesmo tema.
2. Cada DDS deve ser adequado para uma conversa de segurança com duração aproximada de 3 a 5 minutos, sem ultrapassar 5 minutos de leitura em ritmo normal.
3. Utilize aproximadamente 400 a 550 palavras por alternativa. Não acrescente informações repetitivas ou desnecessárias apenas para atingir esse tamanho.
4. Adapte a linguagem ao perfil dos profissionais informado pelo usuário. Priorize linguagem clara, direta, profissional e de fácil compreensão.
5. Estruture naturalmente o DDS contemplando, quando aplicável: contextualização do tema ou situação; principais perigos e riscos; possíveis consequências; comportamentos e medidas preventivas; EPIs e/ou EPCs pertinentes; boas práticas durante a execução da atividade; e mensagem final de conscientização e prevenção.
6. Dê preferência a orientações práticas que possam ser compreendidas e aplicadas durante a rotina de trabalho.
7. Não invente acidentes, dados, estatísticas, procedimentos internos, requisitos legais ou normas da organização.
8. Quando mencionar legislação, normas regulamentadoras ou requisitos técnicos, faça isso somente quando houver segurança quanto à pertinência. Não invente números de itens, subitens ou obrigações específicas.
9. Não apresente o conteúdo como substituto dos procedimentos, treinamentos, normas ou orientações oficiais da organização.
10. Evite linguagem excessivamente técnica, frases muito longas e parágrafos extensos.
11. Não utilize tom alarmista. Priorize prevenção, conscientização e comportamento seguro.
12. As quatro alternativas devem apresentar diferenças reais de abordagem, redação ou forma de comunicação, evitando apenas trocar palavras mantendo textos praticamente iguais.
13. Entregue textos prontos para serem lidos pelo profissional responsável durante um DDS.

Retorne SOMENTE JSON válido, exatamente nesta estrutura:
{{"Texto 1":"...", "Texto 2":"...", "Texto 3":"...", "Texto 4":"..."}}
"""
    response = client.chats.create(model="gemini-3.1-flash-lite-preview").send_message(prompt)
    texts = parse_json_response(response.text, "{")
    if set(texts) != {f"Texto {n}" for n in range(1, 5)}:
        raise ValueError("A IA não retornou as quatro alternativas esperadas.")
    return texts


def evaluate_texts(client, texts: dict) -> pd.DataFrame:
    prompt = f"""
Avalie comparativamente estes DDS de 1 a 10 em: Seguranca (riscos e prevenção),
EPIs (adequação), Clareza, Objetividade e Aplicabilidade.
TEXTOS: {json.dumps(texts, ensure_ascii=False)}
Retorne somente JSON válido:
[
{{"Texto":"Texto 1","Seguranca":0,"EPIs":0,"Clareza":0,"Objetividade":0,"Aplicabilidade":0}},
{{"Texto":"Texto 2","Seguranca":0,"EPIs":0,"Clareza":0,"Objetividade":0,"Aplicabilidade":0}},
{{"Texto":"Texto 3","Seguranca":0,"EPIs":0,"Clareza":0,"Objetividade":0,"Aplicabilidade":0}},
{{"Texto":"Texto 4","Seguranca":0,"EPIs":0,"Clareza":0,"Objetividade":0,"Aplicabilidade":0}}
]
"""
    response = client.chats.create(model="gemini-2.5-flash").send_message(prompt)
    frame = pd.DataFrame(parse_json_response(response.text, "["))
    missing = set(["Texto", *CRITERIA]) - set(frame.columns)
    if missing:
        raise ValueError(f"A avaliação não trouxe: {', '.join(sorted(missing))}.")
    if len(frame) != 4 or set(frame["Texto"]) != {f"Texto {n}" for n in range(1, 5)}:
        raise ValueError("A avaliação não retornou as quatro alternativas.")
    frame[CRITERIA] = frame[CRITERIA].apply(pd.to_numeric, errors="raise")
    if not frame[CRITERIA].apply(lambda col: col.between(1, 10).all()).all():
        raise ValueError("As notas devem estar entre 1 e 10.")
    return frame[["Texto", *CRITERIA]]


def calculate_ranking(evaluations: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    # Todos os cinco critérios do DDS são de benefício: nota maior é melhor.
    # Desvio-padrão amostral (ddof=1), conforme o código fornecido.
    original = evaluations.set_index("Texto")[CRITERIA].astype(float)
    normalized = original.div(original.sum(axis=0), axis=1)
    means = normalized.mean(axis=0)
    deviations = normalized.std(axis=0, ddof=1)
    coefficients = deviations.div(means).fillna(0)
    weight_table = pd.DataFrame({"Média": means, "Desvio-padrão": deviations,
                                 "Coeficiente de variação": coefficients})
    cv_sum = coefficients.sum()
    weight_table["Peso AHP-Gaussiano"] = (
        1 / len(CRITERIA) if cv_sum == 0 else coefficients / cv_sum
    )
    scores = (normalized * weight_table["Peso AHP-Gaussiano"]).sum(axis=1)
    ranking = pd.DataFrame({"Texto": scores.index, "Pontuação": scores})
    ranking = ranking.sort_values("Pontuação", ascending=False).reset_index(drop=True)
    ranking.insert(0, "Posição", ranking["Pontuação"].round(12).rank(ascending=False, method="min").astype(int))
    ranking["Percentual"] = ranking["Pontuação"] / ranking["Pontuação"].sum() * 100
    return ranking, weight_table



def estimated_reading_time(text: str) -> int:
    """Estima o tempo de leitura oral do DDS em minutos."""
    words = len(str(text).split())
    words_per_minute = 130
    return max(1, round(words / words_per_minute))

def get_client():
    if genai is None:
        raise RuntimeError("Biblioteca Gemini indisponível.")
    api_key = os.getenv("GEMINI_API_KEY")
    try:
        if not api_key and "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
    except FileNotFoundError:
        pass
    if not api_key:
        raise RuntimeError("Configure GEMINI_API_KEY nos Secrets do Streamlit.")
    return genai.Client(api_key=api_key)

def fold_text(text):
    return "".join(c for c in unicodedata.normalize("NFD", text.lower()) if unicodedata.category(c) != "Mn")

# Banco editorial inicial. Conteúdo geral, sujeito a revisão técnica da organização.
LOCAL_TOPICS = [
    ("Quedas e organização", ("oleo", "piso", "queda", "escorreg", "organizacao", "limpeza"),
     "Observe obstáculos, resíduos e condições do piso que possam causar quedas. Comunique a condição, sinalize conforme o procedimento e providencie o tratamento por pessoa autorizada. Mantenha os caminhos livres; não improvise a limpeza de uma substância desconhecida."),
    ("Máquinas e manutenção", ("maquina", "equipamento", "manutencao", "mecanico", "energia"),
     "Identifique fontes de energia e possibilidades de movimento inesperado. Antes de intervir, siga o procedimento de isolamento, bloqueio e verificação da organização, executado por pessoas autorizadas. Não remova proteções nem considere um equipamento seguro apenas porque foi desligado."),
    ("Movimentação de materiais", ("carga", "peso", "ergonomia", "transporte", "postura"),
     "Observe peso, formato, percurso e condições de movimentação. Utilize os recursos e a ajuda previstos para a tarefa. Não improvise o levantamento de uma carga que não consegue controlar com segurança. Comunique desconforto e consulte as orientações da atividade."),
    ("Produtos químicos", ("quimic", "solvente", "tinta", "produto", "substancia"),
     "Confirme a identificação do produto e consulte sua ficha de dados de segurança e os procedimentos aplicáveis. Não misture produtos nem use recipientes sem identificação. As medidas de manuseio, proteção e resposta a derramamento dependem da substância e da avaliação da atividade."),
    ("Trabalho em altura", ("altura", "andaime", "telhado", "escada"),
     "Confirme se existem condições de queda de pessoas ou materiais. A atividade depende de planejamento, autorização e recursos de proteção definidos pelos responsáveis. Não improvise acessos ou sistemas de proteção. Esclareça como agir em emergência antes do início."),
    ("Eletricidade", ("eletric", "choque", "painel", "tomada", "cabo"),
     "Observe sinais de dano em cabos e equipamentos sem tocar em partes suspeitas. Comunique a condição. Intervenções elétricas exigem profissionais autorizados e os procedimentos da organização. Não improvise conexões nem presuma ausência de tensão."),
]

def local_topic_guidance(topic):
    folded = fold_text(topic)
    matches = [(name, guidance) for name, keys, guidance in LOCAL_TOPICS if any(k in folded for k in keys)]
    return matches[:3]

def evaluate_local_texts(texts):
    """Rubrica textual heurística; não comprova correção técnica ou segurança."""
    rows = []
    for name, text in texts.items():
        t = fold_text(text)
        sentences = [x.split() for x in re.split(r"[.!?]", text) if x.strip()]
        avg = sum(map(len, sentences)) / max(1, len(sentences))
        words = len(text.split())
        coverage = lambda keys: sum(k in t for k in keys)
        rows.append({"Texto": name,
            "Seguranca": min(10, 1 + coverage(["perigo", "risco", "prevenc", "procedimento", "comunique", "emergencia", "protec", "nao improv", "responsavel"])),
            "EPIs": 1 + 3 * int("epis" in t) + 3 * int("protecao coletiva" in t) + 3 * int("riscos reais" in t),
            "Clareza": 10 if avg <= 20 else 8 if avg <= 28 else 6,
            "Objetividade": 10 if 300 <= words <= 550 else 8 if 180 <= words < 300 else 6,
            "Aplicabilidade": min(10, 1 + coverage(["verifi", "confirm", "comunique", "antes", "durante", "finalizar", "responsavel", "combin", "regist"]))})
    return pd.DataFrame(rows)[["Texto", *CRITERIA]]


def generate_local_texts(profile: str, topic: str) -> dict:
    """Roteiros locais: sem API, normas inventadas ou avaliação automática."""
    context = f"Profissionais: {profile}\nSituação informada: {topic}"
    matches = local_topic_guidance(topic)
    guidance = "\n\n".join(f"{name}: {text}" for name, text in matches) or "Tema fora do banco local: este roteiro é geral. Confirme as medidas específicas com o responsável pela segurança da atividade."
    common = (
        "Antes de começar, conversem sobre a situação descrita. Identifiquem os perigos presentes "
        "e quem pode ser afetado, incluindo colegas, visitantes e pessoas que circulam nas proximidades. "
        "Não presumam que uma condição é segura apenas porque a atividade já foi realizada antes.\n\n"
        "Verifiquem as condições da área, os acessos, a organização e os recursos necessários. "
        "Se houver uma condição insegura, comuniquem ao responsável e sigam o procedimento da organização "
        "para interromper ou não iniciar a atividade. Uma mudança no cenário exige nova verificação.\n\n"
        "As medidas de proteção coletiva e os EPIs devem ser definidos conforme os riscos reais, "
        "a avaliação da atividade e as orientações da organização. Este roteiro não determina quais "
        "equipamentos são adequados para uma tarefa específica. Confirmem essa orientação com o responsável.\n\n"
        "Durante a execução, mantenham comunicação entre os envolvidos. Não improvisem métodos, "
        "ferramentas ou proteções. Ao perceber uma condição diferente da prevista, parem para esclarecer "
        "como prosseguir com segurança. Em emergências, sigam o plano da organização.\n\n"
        "Ao finalizar, verifiquem a condição da área e registrem ou comuniquem os problemas encontrados. "
        "A prevenção depende de reconhecer os riscos, combinar medidas e verificar se elas estão funcionando."
    )
    approaches = [
        ("Conversa preventiva", "Qual perigo desta situação precisamos controlar primeiro?", "Cada participante deve apontar uma condição que precisa ser verificada antes do início."),
        ("Roteiro antes, durante e depois", "O que precisamos conferir em cada momento da atividade?", "Organizem a conversa em três momentos: preparação, execução e encerramento. Combinem quem verificará cada medida."),
        ("Perguntas para a equipe", "O que mudou hoje e pode afetar nossa segurança?", "Peçam que a equipe explique quais condições impediriam o início da tarefa e a quem comunicar um problema."),
        ("Compromisso de prevenção", "Qual ação concreta podemos combinar agora?", "Escolham uma medida prevista no procedimento, definam o responsável e confirmem sua execução antes de iniciar."),
    ]
    return {f"Texto {i}": f"DDS — {title}\n\n{context}\n\n{question}\n\n{action}\n\n{guidance}\n\n{common}\n\nFechamento: cada pessoa pode apresentar uma dúvida. Confirmem as orientações específicas com o responsável antes da atividade."
            for i, (title, question, action) in enumerate(approaches, 1)}


def show_logos():
    logos = [
        ("UFF_logo.jpg", "UFF"),
        ("veiga_logo.png", "UVA"),
        ("puc_logo.png", "PUC-Rio"),
    ]

    for column, (filename, label) in zip(st.columns(3), logos):
        with column:
            path = APP_DIR / filename

            if path.exists():
                mime = (
                    "image/jpeg"
                    if path.suffix.lower() in {".jpg", ".jpeg"}
                    else "image/png"
                )

                encoded = base64.b64encode(
                    path.read_bytes()
                ).decode("ascii")

                st.markdown(
                    f"""
                    <div class="logo-box">
                        <img
                            src="data:{mime};base64,{encoded}"
                            width="240" height="94"
                            alt="Logotipo {html.escape(label)}"
                        >
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="logo-box">{html.escape(label)}</div>',
                    unsafe_allow_html=True,
                )



def render_author(name, affiliation, links):
    links_html = "".join(
        f'<a href="{html.escape(url)}" target="_blank" rel="noopener noreferrer">{html.escape(label)}</a>'
        for label, url in links
    )
    st.markdown(f"""<div class="author-card"><div class="author-name">{html.escape(name)}</div>
    <div class="author-affiliation">{html.escape(affiliation)}</div>
    <div class="author-links">{links_html}</div></div>""", unsafe_allow_html=True)


def printable_dds(title: str, text: str) -> str:
    """Cria uma página HTML limpa que pode ser aberta e impressa pelo navegador."""
    safe_title = html.escape(title)
    safe_text = html.escape(text).replace("\n", "<br>")
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><title>{safe_title}</title>
<style>
body{{font-family:Arial,sans-serif;color:#17212b;max-width:760px;margin:48px auto;
padding:0 28px;line-height:1.65}}h1{{color:#082b4c;border-bottom:3px solid #0b5f9e;
padding-bottom:12px}}.note{{margin-top:32px;padding:12px;background:#fff8e7;
border-left:5px solid #e6a817;font-size:13px}}@media print{{body{{margin:0;max-width:none}}
.note{{break-inside:avoid}}}}</style></head><body><h1>{safe_title}</h1>
<p>{safe_text}</p><div class="note"><strong>Atenção:</strong> material de apoio.
Verifique sua compatibilidade com os procedimentos, normas e requisitos de segurança
aplicáveis à organização.</div></body></html>"""


st.markdown("""<section class="hero">
<span class="hero-tag">Sistema de apoio à decisão</span>
<h1>DDS SmartSelect</h1><p class="hero-subtitle">Seleção Inteligente de Diálogos Diários de Segurança</p>
<p>Trabalho aprovado no ENEGEP USP 2026</p></section>""", unsafe_allow_html=True)

st.markdown('<h2 class="section-title">Gerar nova recomendação</h2>', unsafe_allow_html=True)
with st.form("dds_form"):
    profile = st.text_input(
        "Perfil dos profissionais",
        value="",
        placeholder="Ex.: Mecânicos de manutenção que atuam em equipamentos industriais.",
        help="Informe função, experiência ou características que ajudem a adequar a linguagem ao público."
    )
    topic = st.text_area(
        "Tema ou situação a ser abordada",
        value="",
        placeholder=(
            "Ex.: Durante uma manutenção foi identificado óleo no piso próximo ao equipamento. "
            "Abordar riscos de queda, organização da área e medidas preventivas."
        ),
        height=145,
        help="Descreva de forma simples o assunto, risco, incidente, quase acidente ou situação que deseja abordar."
    )
    submitted = st.form_submit_button(
        "✨ Gerar e selecionar DDS",
        type="primary",
        use_container_width=True
    )


if submitted:
    if not profile.strip() or not topic.strip():
        st.warning("Preencha o perfil do público e o tema.")
    else:
        client = None
        generation_source = "Gemini"
        with st.spinner("Preparando alternativas de DDS..."):
            try:
                client = get_client()
                texts = generate_texts(client, profile.strip(), topic.strip())
            except Exception:
                texts = generate_local_texts(profile.strip(), topic.strip())
                generation_source = "Roteiro local gratuito"
            evaluations = ranking = weights = None
            if generation_source == "Gemini":
                try:
                    evaluations = evaluate_texts(client, texts)
                    ranking, weights = calculate_ranking(evaluations)
                except Exception:
                    pass
        evaluation_source = "Gemini"
        if evaluations is None:
            evaluations = evaluate_local_texts(texts)
            ranking, weights = calculate_ranking(evaluations)
            evaluation_source = "Regras locais — avaliação textual heurística"
        st.session_state["result"] = (texts, evaluations, ranking, weights)
        st.session_state["generation_source"] = generation_source
        st.session_state["evaluation_source"] = evaluation_source
        st.session_state["result_version"] = st.session_state.get("result_version", 0) + 1


if "result" in st.session_state:
    texts, evaluations, ranking, weights = st.session_state["result"]
    source = st.session_state.get("generation_source", "Gemini")
    st.caption(f"Origem dos textos: {source}.")
    if source == "Roteiro local gratuito":
        st.info("Modo local gratuito: roteiro geral organizado com o contexto informado. Não é texto criado por IA. Revise e acrescente as medidas específicas da atividade antes de usar.")
    if st.session_state.get("evaluation_source", "").startswith("Regras locais"):
        st.caption("Avaliação automática local por presença de elementos e características de redação. Não confirma correção técnica, adequação dos EPIs ou ausência de riscos. Notas locais não são equivalentes a notas da IA.")
    winner = ranking.iloc[0]["Texto"] if ranking is not None else st.selectbox("Escolha um roteiro para ler e baixar", list(texts), key=f"selected_{st.session_state.get('result_version', 0)}")
    winner_score = float(ranking.iloc[0]["Pontuação"]) if ranking is not None else None
    selection_label = "Alternativa priorizada pelo modelo multicritério" if ranking is not None else "Roteiro escolhido para revisão"
    score_label = f" · Pontuação {winner_score:.4f}" if winner_score is not None else ""
    if ranking is not None and (ranking["Pontuação"].max() - ranking["Pontuação"].min()) < 1e-10:
        st.info("As alternativas empataram. A ordem de exibição não indica superioridade.")
    reading_minutes = estimated_reading_time(str(texts[winner]))
    winner_text = html.escape(str(texts[winner])).replace("\n", "<br>")
    st.markdown('<h2 class="section-title">DDS recomendado</h2>', unsafe_allow_html=True)
    st.markdown(f"""<div class="winner-card">
    <div class="winner-kicker">{selection_label}</div>
    <div class="winner-title">{html.escape(winner)}{score_label}</div>
    <div style="color:#5d6b78;font-weight:700;margin-bottom:.75rem;">⏱ Tempo estimado de leitura: {reading_minutes} min</div>
    <div class="dds-text">{winner_text}</div></div>""", unsafe_allow_html=True)

    download_text = (
        f"DDS SmartSelect - {winner}\nOrigem: {source}\nAvaliação: {st.session_state.get('evaluation_source', 'Pendente')}\n\n{texts[winner]}\n\n"
        "Atenção: material de apoio. Verifique sua compatibilidade com os "
        "procedimentos, normas e requisitos de segurança da organização."
    )
    download_area, print_area = st.columns(2)
    with download_area:
        st.download_button(
            "⬇️ Baixar DDS em texto",
            data=download_text.encode("utf-8"),
            file_name="DDS_recomendado.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with print_area:
        st.download_button(
            "🖨️ Baixar versão para imprimir",
            data=printable_dds(f"DDS recomendado - {winner}", f"Origem: {source}\nAvaliação: {st.session_state.get('evaluation_source', 'Pendente')}\n\n{texts[winner]}").encode("utf-8"),
            file_name="DDS_recomendado_para_impressao.html",
            mime="text/html",
            use_container_width=True,
        )
    st.markdown("""<div class="safety-note"><strong>Atenção:</strong> o DDS gerado é
    material de apoio à comunicação preventiva. O profissional responsável deve verificar
    sua compatibilidade com os procedimentos, normas e requisitos da organização.</div>""",
    unsafe_allow_html=True)

    if ranking is not None:
        with st.expander("🔎 Ver análise completa e cálculo do método"):
            tab1, tab2, tab3, tab4 = st.tabs(
                ["Ranking", "Quatro alternativas", "Matriz de avaliação", "Pesos do método"])
            with tab1:
                shown = ranking.copy()
                shown["Pontuação"] = shown["Pontuação"].round(4)
                left, right = st.columns([1.2, 1])
                with left:
                    st.bar_chart(ranking.set_index("Texto")["Pontuação"], color="#0b5f9e")
                with right:
                    st.dataframe(shown, hide_index=True, use_container_width=True)
            with tab2:
                for name, text in texts.items():
                    with st.expander(name, expanded=name == winner):
                        if name == winner:
                            st.success("Alternativa recomendada")
                        st.write(text)
            with tab3:
                st.dataframe(evaluations.rename(columns=LABELS), hide_index=True,
                             use_container_width=True)
                st.caption("Notas de 1 a 10. Origem: " + st.session_state.get("evaluation_source", "Pendente") + ". O cálculo multicritério não valida a segurança do conteúdo.")
            with tab4:
                shown_weights = weights.rename(index=LABELS).copy()
                shown_weights.index.name = "Critério"
                st.dataframe(shown_weights.style.format("{:.4f}"), use_container_width=True)
                st.markdown("""O **AHP-Gaussiano** obtém pesos a partir da variabilidade
                das avaliações. Quanto mais um critério diferencia as alternativas, maior tende
                a ser seu peso. A pontuação final é a soma ponderada dos valores normalizados.""")

st.markdown('<h2 class="section-title">Como funciona?</h2>', unsafe_allow_html=True)
st.markdown("""<div class="method-flow">
<div class="method-step"><div class="step-number">ETAPA 1</div><div class="step-title">Contexto</div><div class="step-text">Digite o perfil dos profissionais e descreva o contexto necessário</div></div>
<div class="method-step"><div class="step-number">ETAPA 2</div><div class="step-title">Geração</div><div class="step-text">Quatro alternativas por IA ou roteiros locais gratuitos</div></div>
<div class="method-step"><div class="step-number">ETAPA 3</div><div class="step-title">Avaliação</div><div class="step-text">Notas pela IA ou por regras locais em cinco critérios</div></div>
<div class="method-step"><div class="step-number">ETAPA 4</div><div class="step-title">AHP-Gaussiano</div><div class="step-text">O sistema aplica o método de decisão</div></div>
<div class="method-step"><div class="step-number">ETAPA 5</div><div class="step-title">Recomendação</div><div class="step-text">Ranking e melhor DDS</div></div>
</div>""", unsafe_allow_html=True)

st.markdown('<h2 class="section-title">Sobre o método</h2>', unsafe_allow_html=True)
st.markdown("""<div class="panel">O <strong>DDS SmartSelect</strong> integra IA
Generativa e AHP-Gaussiano, com alternativa local gratuita em caso de indisponibilidade. Os roteiros locais são gerais e precisam de adaptação pelo responsável. A avaliação pode ser feita pela IA ou por regras textuais locais segundo
segurança, EPIs, clareza, objetividade e aplicabilidade. Essas avaliações formam uma
matriz de decisão, processada para produzir pesos, ranking e recomendação. Assim, o
sistema não apenas gera um texto: ele compara alternativas de maneira estruturada.</div>""",
unsafe_allow_html=True)

st.markdown('<h2 class="section-title">Pesquisa desenvolvida por</h2>', unsafe_allow_html=True)
for column, author in zip(st.columns(4), AUTHORS):
    with column:
        render_author(*author)

st.markdown('<h2 class="section-title">Instituições e artigo científico</h2>',
            unsafe_allow_html=True)
logo_area, article_area = st.columns([2.15, 1], gap="large")
with logo_area:
    show_logos()
with article_area:
    st.markdown("### Artigo científico")
    st.caption("Trabalho aprovado no ENEGEP USP 2026.")
    if PDF_FILE.exists():
        with open(PDF_FILE, "rb") as pdf:
            st.download_button(
                "📄 Acessar artigo completo",
                data=pdf.read(),
                file_name=PDF_FILE.name,
                mime="application/pdf",
                use_container_width=True,
            )
    else:
        st.info(f'Inclua o arquivo "{PDF_FILE.name}" no diretório do app.')


# Logo do evento no final da página (arquivo já existente no repositório).
event_logo = APP_DIR / "enegep_usp.png"
if event_logo.exists():
    encoded_event = base64.b64encode(event_logo.read_bytes()).decode("ascii")
    st.markdown(f'<img class="event-logo" src="data:image/png;base64,{encoded_event}" width="320" height="130" alt="Logotipo do ENEGEP na USP, edição de 2026">', unsafe_allow_html=True)
st.markdown('<p class="event-note">Trabalho aprovado no ENEGEP USP 2026</p>', unsafe_allow_html=True)
with st.expander("Acessibilidade deste site"):
    st.markdown("**Site desenvolvido com recursos de acessibilidade.** Utilizamos campos identificados, descrições de logotipos, contraste de cores e organização do conteúdo para facilitar a leitura.")
    st.markdown("**Avaliação automatizada:** Lighthouse, em 30/09/2026, com pontuação de acessibilidade 84/100 na versão avaliada. O relatório apontou restrição de zoom e ausência de região principal de navegação. Essas pendências estão em acompanhamento; a pontuação não representa certificação de conformidade.")
    st.caption("Esta versão recebeu ajustes de layout e ainda precisa de nova avaliação. A verificação da página não certifica a acessibilidade dos arquivos baixados. Testes manuais com teclado, ampliação e leitor de tela complementam a avaliação automática.")
