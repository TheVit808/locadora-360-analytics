import sqlite3


def obter_conexao():
  # Abre a conexão com o caminho do  banco
  conn = sqlite3.connect("./data/raw_sample/DB_LOCADORA.seed.db")

  # Ativa as chaves estrangeiras para conexão
  conn.execute("PRAGMA foreign_keys = ON;")

  # (Opcional, mas altamente recomendado) Permite acessar as colunas pelo nome, ex: row['id']
  conn.row_factory = sqlite3.Row

  return conn