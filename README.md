# Locadora 360 Analytics

Projeto analítico e operacional para uma locadora de veículos, construído sobre SQLite e dados sintéticos. O repositório consolida o modelo físico da locadora, regras de integridade da Trilha A, triggers para prevenção de conflitos de agenda e consultas para acompanhamento de exceções operacionais.

## Escopo técnico

- **Banco:** SQLite;
- **Dados:** sintéticos, com base de referência em `data/raw_sample/DB_LOCADORA.seed.db`;
- **Banco de testes:** `data/locadora_test.db`;
- **Entidades principais:** categorias, filiais, clientes, modelos, veículos, seguros, reservas, aluguéis, pagamentos, funcionários e manutenções;
- **Volume do snapshot local:** 2.794 reservas, 2.794 aluguéis, 2.794 pagamentos, 150 veículos, 500 clientes, 139 manutenções, 15 modelos, 10 filiais e 5 categorias;
- **Power BI:** modelo em `powerbi/locadora.pbix`;
- **Documentação adicional:** DER e apresentação do modelo em `docs/`.

A decisão de consolidação está documentada em [`docs/decisao-consolidacao.md`](docs/decisao-consolidacao.md): os nomes físicos do banco com dados são o contrato da Trilha A, enquanto os scripts originais são preservados para rastreabilidade.

## Modelo de dados

O modelo é centrado no ciclo de locação:

```text
CATEGORIA ──< MODELO ──< VEICULO ──< RESERVA ──< ALUGUEL ──< PAGAMENTO
                              │           │            │
                              │           └────────────┘
                              └──── MANUTENCAO

CLIENTE ──< RESERVA / ALUGUEL
FILIAL  ──< VEICULO, RESERVA, ALUGUEL, FUNCIONARIO
SEGURO  ──< RESERVA / ALUGUEL
```

O schema original está em [`database/schema/original_Tables.sql`](database/schema/original_Tables.sql). A extensão da Trilha A, em [`database/schema/002_trilha_a_integridade.sql`](database/schema/002_trilha_a_integridade.sql), adiciona a tabela de auditoria `RESERVA_EVENTO` e índices para consultas de intervalos em reservas, aluguéis e manutenções.

## Integridade operacional

As regras implementadas em [`database/triggers/integridade_reserva.sql`](database/triggers/integridade_reserva.sql) cobrem:

- intervalo de reserva válido, com devolução posterior à retirada;
- prevenção de reservas sobrepostas para o mesmo veículo;
- permissão de intervalos adjacentes no padrão `[início, fim)`;
- cancelamentos e finalizações fora do bloqueio de disponibilidade;
- bloqueio de reserva durante aluguel ativo;
- bloqueio de reserva durante manutenção ativa;
- bloqueio de manutenção que conflita com reserva confirmada ou pendente;
- validação das mesmas restrições em alterações de reserva/manutenção;
- registro de criação e mudança de status em `RESERVA_EVENTO`.

A view [`database/views/vw_conflitos_reserva.sql`](database/views/vw_conflitos_reserva.sql) cria as consultas `vw_conflitos_reservas`, `vw_disponibilidade_categoria` e `vw_excecoes_operacionais`. O relatório [`reports/concorrencia_e_disponibilidade.sql`](reports/concorrencia_e_disponibilidade.sql) agrupa conflitos, status da frota e quantidade de conflitos por veículo.

O snapshot atual possui **527 registros** em [`reports/operational_exceptions.csv`](reports/operational_exceptions.csv), classificados como exceções de alta severidade para revisão operacional.

## Testes

A suíte em [`tests/test_regras_negocio.py`](tests/test_regras_negocio.py) valida inserções válidas, sobreposição parcial e total, intervalos adjacentes, cancelamentos, alteração de datas, manutenção, aluguel ativo, chaves estrangeiras e view de conflitos. Os testes usam uma cópia temporária de `DB_LOCADORA.seed.db` e aplicam o schema e os triggers da Trilha A via [`tests/conftest.py`](tests/conftest.py).

Execução verificada no snapshot atual:

```text
10 passed, 1 skipped
```

O caso ignorado ocorre quando a view de conflitos não está disponível no banco de teste; a fixture aplica o schema e os triggers, mas não carrega automaticamente o script de views.

## Execução local

Requisitos: Python 3.11+ e os pacotes declarados em `requirements.txt` (`pytest`, `pytest-cov`, `coverage` e dependências auxiliares).

```bash
python3 -m pip install -r requirements.txt
python3 -m pytest -q
```

Para abrir o banco com chaves estrangeiras habilitadas:

```python
from src.db import connect

with connect() as db:
    rows = db.execute("SELECT * FROM vw_excecoes_operacionais").fetchall()
```

O módulo [`src/db.py`](src/db.py) resolve o banco de testes relativo à raiz do projeto, configura `row_factory = sqlite3.Row`, ativa `PRAGMA foreign_keys = ON` e define `busy_timeout` de 5 segundos. O script legado [`conexao.py`](conexao.py) continua apontando diretamente para o banco seed e é mantido para compatibilidade/rastreabilidade.

## Integração contínua

O workflow disponível em [`.vscode/.github/workflows/ci.yml`](.vscode/.github/workflows/ci.yml) instala Python 3.11, instala `requirements.txt` e executa `python -m pytest -q` em pushes para `main`/`feat/**` e em pull requests para `main`.

> **Atenção:** para ser descoberto automaticamente pelo GitHub Actions, o workflow deve estar em `.github/workflows/`. O arquivo atualmente versionado está em `.vscode/.github/workflows/ci.yml`; essa localização deve ser revisada antes de depender da CI remota.

## Organização

```text
data/raw_sample/          Banco SQLite seed de referência
data/                     Banco SQLite de testes

database/schema/          Schema original e extensão da Trilha A
database/triggers/        Regras de reservas, manutenção e eventos
database/views/           Views de conflitos e disponibilidade
docs/                     Decisões, DER e apresentação do modelo
reports/                  Consultas e exceções operacionais
src/                      Conexão SQLite reutilizável
 tests/                   Fixtures e testes de regras de negócio
powerbi/                  Modelo Power BI
requirements.txt          Dependências Python
```

## Limitações e próximos passos

Os dados são sintéticos e o projeto ainda está concentrado na integridade operacional da Trilha A. Antes de uso produtivo, recomenda-se corrigir a localização do workflow de CI, carregar as views na fixture de testes, centralizar a configuração de conexão, ampliar cobertura para pagamentos/devoluções e transformar as exceções operacionais em um fluxo de acompanhamento com atualização incremental.
