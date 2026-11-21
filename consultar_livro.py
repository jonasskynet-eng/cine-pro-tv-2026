"""
Script de Consulta Rápida ao Banco de Dados de Livros da Faculdade (Uninter)
Uso:
  python consultar_livro.py python
  python consultar_livro.py calculo
  python consultar_livro.py html
  python consultar_livro.py logistica
  python consultar_livro.py todos
"""

import sys
import sqlite3
import pathlib
import unicodedata

DB_PATH = pathlib.Path(__file__).parent / "banco_de_dados_livros.sqlite"

def normalizar(texto):
    if not texto:
        return ""
    return "".join(
        c for c in unicodedata.normalize("NFD", str(texto))
        if unicodedata.category(c) != "Mn"
    ).lower()

def consultar(termo="todos"):
    if not DB_PATH.exists():
        print(f"Erro: Banco de dados não encontrado em {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = """
    SELECT 
        c.sigla,
        d.codigo,
        d.nome,
        d.status,
        d.prazo_final,
        l.titulo,
        l.autores,
        l.editora,
        l.isbn_digital,
        l.plataforma,
        l.link_acesso
    FROM livros l
    JOIN disciplinas d ON l.disciplina_id = d.id
    JOIN cursos c ON d.curso_id = c.id
    ORDER BY c.id, d.id;
    """

    cursor.execute(query)
    linhas = cursor.fetchall()
    conn.close()

    termo_norm = normalizar(termo)
    resultados = []

    for r in linhas:
        sigla, codigo, disc, status, prazo, titulo, autores, editora, isbn, plat, link = r
        if termo_norm == "todos":
            resultados.append(r)
        else:
            linha_texto = f"{sigla} {codigo} {disc} {titulo} {autores} {editora} {isbn} {plat}"
            if termo_norm in normalizar(linha_texto):
                resultados.append(r)

    if not resultados:
        print(f"\n❌ Nenhum livro encontrado para o termo: '{termo}'\n")
        return

    print(f"\n📚 BANCO DE DADOS DE LIVROS UNINTER — {len(resultados)} resultado(s) para '{termo}':")
    print("=" * 80)
    for r in resultados:
        sigla, codigo, disc, status, prazo, titulo, autores, editora, isbn, plat, link = r
        print(f"[{sigla}] {disc} (Cód: {codigo})")
        print(f"📖 Livro: {titulo}")
        print(f"✍️  Autor(es): {autores} | Editora: {editora}")
        print(f"🔖 ISBN: {isbn} | Plataforma: {plat}")
        print(f"🌐 Link de Acesso: {link}")
        print(f"⏳ Situação: {status} (Prazo final: {prazo})")
        print("-" * 80)
    print()

if __name__ == "__main__":
    busca = "todos"
    if len(sys.argv) > 1:
        busca = " ".join(sys.argv[1:])
    consultar(busca)
