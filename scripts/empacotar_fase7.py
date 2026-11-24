#!/usr/bin/env python3
"""Empacota somente o snapshot Git rastreado e verifica seus entregáveis."""
import argparse
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
import subprocess
from tempfile import NamedTemporaryFile
from urllib.parse import unquote, urlsplit
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "orbital-alert-fiap-gs2026"
DOCS = f"{PREFIX}/entrega_fiap_fase7"
MANIFEST = "MANIFESTO_FASE7.json"

REQUIRED = (
    "README_ENTREGA.md", "COMO_RODAR.md", "CHECKLIST_FINAL.md", "RELATORIO_TECNICO_FASE7.pdf",
    "01_Arquitetura/arquitetura.mmd", "01_Arquitetura/arquitetura.svg", "01_Arquitetura/arquitetura.png",
    "02_Execucao_Plataforma/RESULTADOS.md", "03_DevSecOps/evidencias/github-actions.json",
    "04_Monitoramento/evidencias/indicadores.json", "05_Mineracao_Processos/dados/event_log.csv",
    "05_Mineracao_Processos/dados/variantes-tempos.png", "06_Pitch/Orbital_Alert_Pitch.pptx",
    "07_Videos/VIDEO_TECNICO.md", "07_Videos/VIDEO_PITCH.md", "07_Videos/LINKS_DOS_VIDEOS.md",
    "08_Evidencias/execucao-final/demo.json", "08_Evidencias/execucao-final/web-dashboard.png",
    "09_Codigo/REFERENCIAS.md",
)
DIRECTORIES = ("01_Arquitetura", "02_Execucao_Plataforma", "03_DevSecOps", "04_Monitoramento",
               "05_Mineracao_Processos", "06_Pitch", "07_Videos", "08_Evidencias", "09_Codigo")
BANNED_DIRS = {".git", "node_modules", "target", ".venv", "venv", ".expo", "__pycache__", ".oci", "wallet", "ci-artifacts"}
BANNED_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".dbf", ".pyc", ".zip", ".jar"}
TEXT_SUFFIXES = {".txt", ".md", ".yml", ".yaml", ".json", ".jsonl", ".xml", ".py", ".java",
                 ".properties", ".sh", ".ps1", ".ts", ".tsx", ".js", ".cjs", ".sql", ".csv", ".example"}
SECRET_PATTERN = re.compile(
    rb"-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----|\b(?:gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{40,}|"
    rb"AKIA[A-Z0-9]{16}|sk-(?:proj-)?[A-Za-z0-9_-]{35,})\b"
)


def check_path(name):
    path = PurePosixPath(name)
    if path.is_absolute() or "\\" in name or ".." in path.parts or path.parts[0] != PREFIX:
        raise ValueError(f"Caminho ZIP inválido: {name}")
    if (set(part.lower() for part in path.parts) & BANNED_DIRS or path.suffix.lower() in BANNED_SUFFIXES
            or (path.name.startswith(".env") and path.name != ".env.example") or path.name.endswith(".env")):
        raise ValueError(f"Arquivo indevido rastreado: {name}")


def check_documents(contents):
    paths = set(contents)
    required = {f"{DOCS}/{file}" for file in REQUIRED}
    required |= {f"{PREFIX}/{file}" for file in ("compose.yaml", "PROGRESSO.md", "scripts/subir.ps1", "backend/pom.xml")}
    if missing := required - paths:
        raise ValueError(f"Arquivos ausentes: {sorted(missing)}")
    for folder in DIRECTORIES:
        if not any(name.startswith(f"{DOCS}/{folder}/") for name in paths):
            raise ValueError(f"Diretório vazio: {folder}")

    count = 0
    for name, data in contents.items():
        if not (name.startswith(DOCS + "/") and name.endswith(".md")):
            continue
        for raw in re.findall(r"\]\(([^()\s]+)\)", data.decode("utf-8-sig")):
            target = urlsplit(raw)
            if target.scheme or not target.path:
                continue
            dest = posixpath.normpath(posixpath.join(posixpath.dirname(name), unquote(target.path)))
            if dest not in paths and not any(p.startswith(dest + "/") for p in paths):
                raise ValueError(f"Link local não encontrado: {name} -> {raw}")
            count += 1

    run = json.loads(contents[f"{DOCS}/08_Evidencias/execucao-final/demo.json"].decode("utf-8-sig"))
    analysis = json.loads(contents[f"{DOCS}/05_Mineracao_Processos/dados/analise.json"].decode("utf-8-sig"))
    if not (run["runId"] == analysis["runId"] and len(run["checks"]) == 13
            and analysis["caseCount"] == 3 and analysis["eventCount"] == 15):
        raise ValueError("As evidências do cenário e da mineração divergem")
    if not contents[f"{DOCS}/RELATORIO_TECNICO_FASE7.pdf"].startswith(b"%PDF-"):
        raise ValueError("PDF inválido")
    with ZipFile(BytesIO(contents[f"{DOCS}/06_Pitch/Orbital_Alert_Pitch.pptx"])) as deck:
        slides = [name for name in deck.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)]
        if deck.testzip() or len(slides) != 7:
            raise ValueError("PowerPoint inválido")
    return count


def package(destination, revision):
    commit = subprocess.check_output(["git", "rev-parse", "--verify", revision + "^{commit}"], cwd=ROOT, text=True).strip()
    archive = subprocess.check_output(["git", "archive", "--format=zip", f"--prefix={PREFIX}/", commit], cwd=ROOT)
    contents = {}
    with ZipFile(BytesIO(archive)) as tracked:
        for member in tracked.infolist():
            if member.is_dir():
                continue
            check_path(member.filename)
            if (member.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError(f"Sem links simbólicos: {member.filename}")
            data = tracked.read(member)
            if PurePosixPath(member.filename).suffix.lower() in TEXT_SUFFIXES and SECRET_PATTERN.search(data):
                raise ValueError(f"Possível segredo: {member.filename}")
            contents[member.filename] = data

    links = check_documents(contents)
    ordered = sorted(contents)
    manifest = {"commit": commit, "files": len(ordered), "linksVerified": links,
                "sha256": {name: sha256(contents[name]).hexdigest() for name in ordered}}
    destination.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(dir=destination.parent, prefix="orbital-", suffix=".tmp", delete=False) as f:
        scratch = Path(f.name)
    try:
        with ZipFile(scratch, "w", compression=ZIP_DEFLATED, compresslevel=7) as output:
            for name in ordered:
                output.writestr(name, contents[name])
            output.writestr(MANIFEST, json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
        with ZipFile(scratch) as output:
            if output.testzip() or any(sha256(output.read(name)).hexdigest() != digest
                                      for name, digest in manifest["sha256"].items()):
                raise ValueError("ZIP final apresentou divergência de conteúdo")
        scratch.replace(destination)
    finally:
        scratch.unlink(missing_ok=True)
    digest = sha256(destination.read_bytes()).hexdigest()
    destination.with_suffix(".zip.sha256").write_text(digest + "  " + destination.name + "\n", encoding="utf-8")
    print(f"{destination} | {len(ordered)} arquivos + manifesto | {links} links | SHA-256 {digest}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip", type=Path)
    parser.add_argument("--ref", default="HEAD")
    args = parser.parse_args()
    package(args.zip.resolve(), args.ref)
