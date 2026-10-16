PRAGMA foreign_keys = on;

CREATE TABLE CATEGORIA (
ID_Categoria INTEGER PRIMARY KEY AUTOINCREMENT,
Nome_Categoria Varchar(50) NOT NULL,
Descricao_Categoria Varchar(50) NOT NULL,
Valor_Diaria Decimal(10,2) NOT NULL
);

CREATE TABLE FILIAL (
ID_Filial INTEGER PRIMARY KEY AUTOINCREMENT,
Nome_Filial Varchar(50) NOT NULL,
Endereco_Filial Varchar(100) NOT NULL,
Cidade_Filial Varchar(50) NOT NULL,
Estado_Filial Char(2) NOT NULL,
Telefone_Filial Varchar(11) NOT NULL
);

CREATE TABLE CLIENTE (
ID_Cliente INTEGER PRIMARY KEY AUTOINCREMENT,
Nome_Cliente Varchar(50) not NULL,
CPF_Cliente Varchar(14) UNIQUE NOT NULL,
CNH_Cliente Varchar(11) UNIQUE not NULL,
Data_Nascimento_Cliente Date not NULL,
Telefone_Cliente Varchar(11) not NULL,
Email_Cliente Varchar(100) NOT NULL,
Endereco_Cliente Varchar(100) NOT NULL
);

CREATE TABLE MODELO (
ID_Modelo INTEGER PRIMARY KEY AUTOINCREMENT,
Marca_Modelo Varchar(50) NOT NULL,
Nome_Modelo Varchar(50) NOT NULL,
Ano_Fabricacao_Modelo Year NOT NULL,
ID_Categoria INT NOT NULL,
FOREIGN KEY(ID_Categoria) REFERENCES CATEGORIA(ID_Categoria)
);

CREATE TABLE VEICULO (
ID_Veiculo INTEGER PRIMARY KEY AUTOINCREMENT,
Placa_Veiculo Char(7) UNIQUE NOT NULL,
Chassis_Veiculo Varchar(50) UNIQUE NOT NULL,
Cor_Veiculo Varchar(50) NOT NULL,
Quilometragem_Atual_Veiculo INT NOT NULL,
Status_Veiculo Varchar(50) CHECK (Status_Veiculo IN ('Disponível', 'Locação', 'Manutenção')) NOT NULL,
ID_Modelo INT NOT NULL,
ID_Filial_Atual INT NOT NULL,
FOREIGN KEY(ID_Modelo) REFERENCES MODELO(ID_Modelo),
FOREIGN KEY(ID_Filial_Atual) REFERENCES FILIAL (ID_Filial)
);

CREATE TABLE SEGURO (
ID_Seguro INTEGER PRIMARY KEY AUTOINCREMENT,
Nome_Seguro Varchar(50) NOT NULL,
Descricao_Seguro Varchar(100) NOT NULL,
Custo_Diario Decimal(10,2) NOT NULL
);

CREATE TABLE RESERVA (
ID_Reserva INTEGER PRIMARY KEY AUTOINCREMENT,
Data_Reserva Date NOT NULL,
Data_Retirada_Prevista Date NOT NULL,
Data_Devolucao_Prevista Date NOT NULL,
Valor_Final_Previsto Decimal(10,2) NOT NULL,
Status_Reserva TEXT NOT NULL CHECK (Status_Reserva IN ('Confirmada', 'Pendente', 'Em Locação', 'Cancelada', 'Finalizada')),
ID_Cliente INT NOT NULL,
ID_Veiculo INT not NULL,
ID_Filial_Retirada INT not NULL,
ID_Filial_Devolucao INT NOT NULL,
FOREIGN KEY(ID_Cliente) REFERENCES CLIENTE (ID_Cliente),
FOREIGN KEY(ID_Veiculo) REFERENCES VEICULO(ID_Veiculo),
FOREIGN KEY(ID_Filial_Retirada) REFERENCES FILIAL (ID_Filial),
FOREIGN KEY(ID_Filial_Devolucao) REFERENCES FILIAL (ID_Filial)
);

CREATE TABLE ALUGUEL (
ID_Aluguel INTEGER PRIMARY KEY AUTOINCREMENT,
Data_Retirada_Real Date NOT NULL,
Data_Devolucao_Real Date NULL,
Dias_Locacao INTEGER calculated AS (julianday(Data_Devolucao_Real) - julianday(Data_Retirada_Real)) NULL,
Quilometragem_Retirada INT NOT NULL,
Quilometragem_Devolucao INT NULL,
Valor_Final Decimal(10,2) NULL,
ID_Reserva INT NOT NULL,
ID_Veiculo INT NOT NULL,
ID_Cliente INT NOT NULL,
ID_Filial_Retirada INT NOT NULL,
ID_Filial_Devolucao INT NOT NULL,
ID_Seguro INT NOT NULL ,
FOREIGN KEY(ID_Reserva) REFERENCES RESERVA (ID_Reserva),
FOREIGN KEY(ID_Veiculo) REFERENCES VEICULO(ID_Veiculo),
FOREIGN KEY(ID_Cliente) REFERENCES CLIENTE (ID_Cliente),
FOREIGN KEY(ID_FIlial_Retirada) REFERENCES FILIAL (ID_Filial),
FOREIGN KEY(ID_Filial_Devolucao) REFERENCES FILIAL (ID_Filial),
FOREIGN KEY(ID_Seguro) REFERENCES SEGURO (ID_Seguro)
);

CREATE TABLE PAGAMENTO (
ID_Pagamento INTEGER PRIMARY KEY AUTOINCREMENT,
Data_Pagamento DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
Valor_Pagamento Decimal(10,2) NOT NULL,
Metodo_Pagamento Varchar(50) NOT NULL,
ID_Aluguel INT NOT NULL,
FOREIGN KEY(ID_Aluguel) REFERENCES ALUGUEL(ID_Aluguel)
CONSTRAINT CHK_Metodo_P CHECK (Metodo_Pagamento IN ('Credito', 'Debito', 'Pix', 'Boleto', 'Especie'))
);

CREATE TABLE FUNCIONARIO (
ID_Funcionario INTEGER PRIMARY KEY AUTOINCREMENT,
Nome_Funcionario Varchar(50) not NULL,
Cargo_Funcionario Varchar(50) NOT NULL,
Salario_Funcionario Decimal(10,2) NOT NULL,
Data_Contratacao_Funcionario Date NOT NULL,
ID_Filial INT not NULL,
FOREIGN KEY(ID_Filial) REFERENCES FILIAL (ID_Filial)
);

CREATE TABLE MANUTENCAO (
ID_Manutencao INTEGER PRIMARY KEY AUTOINCREMENT,
Data_Retirada_Manutencao Date NOT NULL,
Data_Conclusao_Manutencao Date NULL,
Descricao_Manutencao Varchar(100) NOT NULL,
Custo_Manutencao Decimal(10,2) NOT NULL,
ID_Veiculo INT NOT NULL,
FOREIGN KEY(ID_Veiculo) REFERENCES VEICULO (ID_Veiculo)
);
