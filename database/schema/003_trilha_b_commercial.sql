PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS DIM_CANAL (
    ID_Canal INTEGER PRIMARY KEY,
    Nome_Canal TEXT NOT NULL UNIQUE,
    Tipo_Canal TEXT NOT NULL CHECK (Tipo_Canal IN ('ORGANICO', 'PAGO', 'PARCERIA', 'DIRETO'))
);

CREATE TABLE IF NOT EXISTS DIM_CAMPANHA (
    ID_Campanha INTEGER PRIMARY KEY,
    Nome_Campanha TEXT NOT NULL,
    Data_Inicio DATE NOT NULL,
    Data_Fim DATE NOT NULL,
    ID_Filial INTEGER,
    ID_Categoria INTEGER,
    ID_Canal INTEGER NOT NULL,
    Publico_Alvo TEXT NOT NULL,
    Tipo_Incentivo TEXT NOT NULL CHECK (
        Tipo_Incentivo IN ('DESCONTO', 'UPGRADE', 'DIARIA_GRATIS', 'FIDELIDADE', 'SEM_INCENTIVO')
    ),
    Percentual_Desconto REAL NOT NULL DEFAULT 0,
    Custo_Campanha REAL NOT NULL CHECK (Custo_Campanha >= 0),
    KPI_Primario TEXT NOT NULL,
    Premissa_Atribuicao TEXT NOT NULL,
    FOREIGN KEY (ID_Filial) REFERENCES FILIAL(ID_Filial),
    FOREIGN KEY (ID_Categoria) REFERENCES CATEGORIA(ID_Categoria),
    FOREIGN KEY (ID_Canal) REFERENCES DIM_CANAL(ID_Canal),
    CHECK (Data_Fim >= Data_Inicio),
    CHECK (Percentual_Desconto BETWEEN 0 AND 1)
);

CREATE TABLE IF NOT EXISTS FATO_FUNIL_EVENTO (
    ID_Evento INTEGER PRIMARY KEY,
    Journey_ID TEXT NOT NULL,
    ID_Cliente INTEGER NOT NULL,
    ID_Canal INTEGER NOT NULL,
    ID_Campanha INTEGER,
    ID_Filial INTEGER,
    ID_Categoria INTEGER,
    ID_Veiculo INTEGER,
    ID_Reserva INTEGER,
    Tipo_Evento TEXT NOT NULL CHECK (
        Tipo_Evento IN (
            'PESQUISA', 'COTACAO', 'RESERVA', 'CANCELAMENTO',
            'RETIRADA', 'DEVOLUCAO', 'NO_SHOW',
            'PERDA_INDISPONIBILIDADE', 'UPGRADE', 'DOWNGRADE'
        )
    ),
    Data_Evento TEXT NOT NULL,
    Valor_Cotacao REAL,
    Valor_Bruto REAL,
    Desconto REAL NOT NULL DEFAULT 0,
    Receita_Liquida_Estimada REAL,
    Dispositivo TEXT,
    Origem_Dado TEXT NOT NULL DEFAULT 'sintetico',
    FOREIGN KEY (ID_Cliente) REFERENCES CLIENTE(ID_Cliente),
    FOREIGN KEY (ID_Canal) REFERENCES DIM_CANAL(ID_Canal),
    FOREIGN KEY (ID_Campanha) REFERENCES DIM_CAMPANHA(ID_Campanha),
    FOREIGN KEY (ID_Filial) REFERENCES FILIAL(ID_Filial),
    FOREIGN KEY (ID_Categoria) REFERENCES CATEGORIA(ID_Categoria),
    FOREIGN KEY (ID_Veiculo) REFERENCES VEICULO(ID_Veiculo),
    FOREIGN KEY (ID_Reserva) REFERENCES RESERVA(ID_Reserva)
);

CREATE TABLE IF NOT EXISTS FATO_CAMPANHA_CUSTO (
    ID_Campanha INTEGER PRIMARY KEY,
    Custo_Midia REAL NOT NULL DEFAULT 0,
    Custo_Beneficio REAL NOT NULL DEFAULT 0,
    Custo_Operacional REAL NOT NULL DEFAULT 0,
    Custo_Total REAL GENERATED ALWAYS AS (
        Custo_Midia + Custo_Beneficio + Custo_Operacional
    ) STORED,
    FOREIGN KEY (ID_Campanha) REFERENCES DIM_CAMPANHA(ID_Campanha)
);

CREATE INDEX IF NOT EXISTS IX_FUNIL_JOURNEY
    ON FATO_FUNIL_EVENTO (Journey_ID, Data_Evento);

CREATE INDEX IF NOT EXISTS IX_FUNIL_CAMPANHA_DATA
    ON FATO_FUNIL_EVENTO (ID_Campanha, Data_Evento);

CREATE INDEX IF NOT EXISTS IX_FUNIL_CLIENTE_DATA
    ON FATO_FUNIL_EVENTO (ID_Cliente, Data_Evento);