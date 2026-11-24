#!/usr/bin/env python3
"""Gera o relatório técnico a partir das evidências da Fase 7 (requer reportlab)."""
from pathlib import Path
import json
from xml.sax.saxutils import escape

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

ROOT = Path(__file__).resolve().parents[1]
DELIVERY = ROOT / "entrega_fiap_fase7"
FILE = DELIVERY / "RELATORIO_TECNICO_FASE7.pdf"
ART = DELIVERY / "08_Evidencias/execucao-final"
NAVY = "#12243C"
INK = "#162A40"
BLUE = "#135C87"
TEAL = "#117B70"
MUTED = "#4E6379"
PALE = "#E8F4F7"
W, H = A4
M = 44

font_home = Path("C:/Windows/Fonts")
regular = font_home / "arial.ttf"
bold = font_home / "arialbd.ttf"
if not regular.exists():
    regular = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    bold = regular.with_name("DejaVuSans-Bold.ttf")
pdfmetrics.registerFont(TTFont("OrbitalRegular", str(regular)))
pdfmetrics.registerFont(TTFont("OrbitalBold", str(bold)))
pdfmetrics.registerFontFamily("OrbitalRegular", normal="OrbitalRegular", bold="OrbitalBold")
report = canvas.Canvas(str(FILE), pagesize=A4, pageCompression=True)
report.setTitle("Orbital Alert | Relatório técnico final | FIAP Fase 7")
report.setAuthor("Equipe Orbital Alert")
run = json.loads((ART / "demo.json").read_text(encoding="utf-8-sig"))
analysis = json.loads((DELIVERY / "05_Mineracao_Processos/dados/analise.json").read_text(encoding="utf-8-sig"))


def text(x, top, value, size=11, color=INK, strong=False):
    report.setFillColor(HexColor(color))
    report.setFont("OrbitalBold" if strong else "OrbitalRegular", size)
    report.drawString(x, H - top, value)


def block(top, value, size=11, color=INK, x=M, width=W-2*M, leading=None):
    style = ParagraphStyle("orbital", fontName="OrbitalRegular", textColor=HexColor(color),
                           fontSize=size, leading=leading or size * 1.44, alignment=TA_LEFT)
    paragraph = Paragraph(value, style)
    _, height = paragraph.wrap(width, H)
    paragraph.drawOn(report, x, H - top - height)
    return top + height


def image(top, file, max_width, max_height, x=M):
    asset = ImageReader(str(file))
    ow, oh = asset.getSize()
    scale = min(max_width / ow, max_height / oh)
    width, height = ow * scale, oh * scale
    report.drawImage(asset, x + (max_width - width)/2, H-top-height,
                     width=width, height=height, mask="auto")
    return top + height


def rect(x, top, width, height, color):
    report.setFillColor(HexColor(color))
    report.rect(x, H-top-height, width, height, fill=1, stroke=0)


def footer(page):
    rect(M, 787, W - 2*M, .8, "#B8CFDA")
    text(M, 807, "ORBITAL ALERT   /   FIAP   /   AGROSMART FASE 7", 8, MUTED, True)
    text(W-M-14, 807, str(page), 9, MUTED, True)
    report.showPage()


def heading(page, kicker, title, subtitle):
    rect(0, 0, W, 9, TEAL)
    text(M, 47, f"{page:02d}  /  {kicker.upper()}", 9, BLUE, True)
    text(M, 85, title, 26, NAVY, True)
    return block(105, subtitle, 11.5, MUTED) + 22


def entry(top, title, value):
    text(M, top, title, 13, BLUE, True)
    return block(top+8, value) + 25


def command(top, lines):
    height = 18 + len(lines)*18
    rect(M, top, W-2*M, height, PALE)
    for i, value in enumerate(lines):
        text(M+12, top+19+i*18, value, 9.3, NAVY, True)
    return top + height


rect(0, 0, W, 333, NAVY)
rect(0, 0, W, 9, "#37C2A5")
text(M, 57, "FIAP  /  GLOBAL SOLUTION  /  AGROSMART FASE 7", 10, "#91DDCF", True)
text(M, 119, "Orbital Alert", 53, "#FFFFFF", True)
text(M, 166, "Relatório técnico final", 27, "#D7EDF1")
block(195, "Monitoramento preventivo de enchentes com telemetria IoT, alertas e análise auditável.",
      15, "#CCE0E9", width=425)
text(M, 296, "EXECUÇÃO LOCAL VALIDADA EM 24 NOV 2026", 9, "#91DDCF", True)
y = image(355, ART / "web-dashboard.png", W-2*M, 325)
block(y+10, "Captura real do dashboard Expo web. As leituras do cenário foram geradas pelo simulador.",
      10, MUTED)
footer(1)

y = heading(2, "Arquitetura", "Serviços e fluxo de dados",
            "O fluxo operacional resolve o alerta. O Data Lake consolida o Risk Score e preserva os eventos de análise.")
y = image(y, DELIVERY / "01_Arquitetura/arquitetura.png", W-2*M, 420)
y = entry(y+25, "Operação", "Simulador Python → API Spring Boot em Java 21 → PostgreSQL. O limiar de chuva abre o alerta e o painel Expo consulta a API pelo Nginx.")
y = entry(y, "Análise", "RAW registra a leitura correlacionada. TRUSTED valida e deduplica. CURATED agrega por região. O score do painel mostra a origem e a data.")
entry(y, "Opcionais", "Oracle FREEPDB1 recebe o CURATED por MERGE. A recomendação usa MOCK por padrão. OCI Object Storage continua como integração futura.")
footer(2)

y = heading(3, "Execução", "Reprodução no Windows",
            "Abra o Docker Desktop com o engine Linux e execute na raiz do repositório.")
y = command(y, [r".\scripts\subir.ps1", r".\scripts\demonstrar.ps1 -Mineracao -Resultado .\demo.json"])
y = entry(y+28, "Painel", "Abra <b>http://127.0.0.1:8080/</b>, clique em <b>Abrir painel</b> e entre na região AgroSmart · Demo. Se a porta mudar, use o endereço mostrado pelo script.")
y = entry(y, "Entradas e saídas", f"Na rodada <b>{escape(run['runId'])}</b>, 45 mm/h foram persistidos sem alerta. Com 95 mm/h, a API gerou um alerta HIGH. O CURATED da região publicou <b>{run['risk']['context']['riskScore']}/100</b>, FLOOD e média de 70 mm/h. Um sensor inexistente retornou HTTP 404.")
y = entry(y, "Persistência", "Na validação do Compose, as leituras, o alerta e o CURATED permaneceram ao recriar os containers. A migração RAIN → RAINFALL foi executada duas vezes num banco legado e preservou os IDs.")
y = entry(y, "Encerramento", r".\scripts\encerrar.ps1 conserva os volumes. O perfil Oracle é opcional. Duas cargas locais anteriores do mesmo snapshot mantiveram uma única linha na tabela analítica.")
footer(3)

y = heading(4, "Qualidade e operação", "Segurança e monitoramento",
            "A pilha local conecta os jobs e o backend pela rede interna. O navegador usa somente o frontend publicado em loopback.")
y = entry(y, "Controle de acesso", "O serviço exige Bearer de ingestão para leituras e Bearer de administração para gravações administrativas. Os testes verificaram 401 sem identidade e 403 com o papel incorreto. O login legado verifica BCrypt e devolve perfil. A identidade individual precisa de evolução.")
y = entry(y, "CI no GitHub", "Java, JUnit, JaCoCo e SpotBugs passaram. Python, Ruff e pip-audit passaram. TypeScript, exportação Expo, build de containers e smoke passaram. npm audit e a etapa Trivy falharam. Os quatro jobs publicaram artefatos.")
y = entry(y, "Achados", "O ajuste compatível reduziu a auditoria npm de 44 para 33 registros, restando 1 crítico e 10 altos. O relatório DevSecOps mantém os achados e o status do scanner. O build do front serve o bundle estático.")
y = entry(y, "Observabilidade", "Actuator interno e /api/status expõem leituras recebidas e processadas, falhas e alertas. O scheduler registra tentativas sob uma trava, preserva o último sucesso e publica logs JSON com data UTC.")
y = entry(y, "Teste de falha", "Uma leitura autorizada de sensor inexistente foi rejeitada. Um lote com diretório RAW ausente registrou FAILED e preservou lastSuccess. Uma tentativa concorrente registrou SKIPPED_LOCKED.")
block(y, '<link href="https://github.com/Vitorfs2509/orbital-alert-fiap-gs2026/actions/runs/45422251550" color="#135C87">Execução remota do GitHub Actions · 45422251550</link>', 10)
footer(4)

y = heading(5, "Mineração", "Três caminhos observados",
            f"Registros reais do cenário {run['runId']}, com entradas simuladas e timestamps em UTC.")
y = entry(y, "Amostra", f"{analysis['caseCount']} casos de leitura, {analysis['eventCount']} eventos correlacionados e {analysis['batchEventCount']} eventos do lote em CSV separado. Cada variante ocorreu uma vez: normal, com alerta e rejeitada.")
y = image(y, DELIVERY / "05_Mineracao_Processos/dados/variantes-tempos.png", W-2*M, 230)
y = entry(y+22, "Tempo entre etapas", "RAW → TRUSTED teve a maior mediana, <b>534,59 ms</b>, em duas observações. O intervalo inclui a espera pelo lote. TRUSTED → CURATED teve mediana de 101,82 ms.")
entry(y, "O que essa evidência sustenta", "Os caminhos, a rejeição e os vínculos foram observados. A amostra não sustenta estimativas de escala nem um gargalo recorrente. Medir espera, processamento e I/O separadamente em novas execuções é a próxima validação.")
footer(5)

y = heading(6, "Produto e evolução", "Público e limites do MVP",
            "A proposta aproxima alertas, evidências de leitura e contexto para apoiar uma ação preventiva.")
y = entry(y, "Público", "Analistas da Defesa Civil e equipes municipais são usuários prioritários. Moradores em áreas de risco são beneficiários. O painel ajuda a relacionar a região, a leitura, a severidade e a recomendação consultiva.")
y = entry(y, "Escopo demonstrado", f"A demonstração final passou {len(run['checks'])} verificações e teve captura real do navegador. A integração Oracle opcional foi validada separadamente. A Fase 6 contém avaliação com personas simuladas.")
y = entry(y, "Evolução", "Validar sensores em campo, autenticação individual e controle institucional. Tratar advisories do Expo e do sistema base. Adicionar retenção, recuperação, métricas históricas e ensaios de carga representativos.")
y = entry(y, "Materiais no pacote", "Arquitetura em Mermaid/PNG/SVG, guia Windows, relatório DevSecOps, amostras JSON de monitoramento, logs/eventos CSV, scripts e código-fonte. O índice 08_Evidencias identifica a origem de cada registro.")
entry(y, "Submissão", "Gravar o vídeo técnico e o pitch, inserir os dois links no arquivo de vídeos e submeter o material conforme a rubrica da FIAP.")
footer(6)
report.save()
print(FILE)
