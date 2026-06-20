create type status_loja as enum ('ativa', 'inativa');
create type status_usuario as enum ('ativo','inativo','bloqueado');
create type status_produto as enum ('ativo', 'indisponivel','descontinuado');

create table empresa(
id_empresa serial primary key,
nome_empresa varchar(100) not null,
cnpj varchar(14) unique not null,
telefone varchar(20),
email varchar(150),
data_cadastro timestamp default current_timestamp not null);

create table lojas(
id_loja serial primary key,
id_empresa integer not null references empresa(id_empresa) on delete restrict,
nome_loja varchar(100) not null,
endereco_loja varchar(255),
cidade varchar(100),
estado char(2),
telefone varchar(20),
status_loja status_loja default 'ativa' not null);

create table usuarios (
id_usuario serial primary key,
id_lojas integer references lojas(id_loja) on delete set null,
nome_usuario varchar(100) not null,
email varchar(150) unique not null,
senha_usuario varchar(50) not null,
nivel_acesso integer not null default 1,
status_usuario status_usuario default 'ativo' not null,
ultimo_login timestamp);

create table categorias(
id_categoria serial primary key,
nome_categoria varchar(50),
descricao_categoria text);

create table produtos(
id_produto serial primary key,
id_categoria integer references categorias(id_categoria) on delete set null,
nome_produto varchar(150) not null,
descricao text,
marca varchar(100),
preco_venda numeric(10,2) not null check (preco_venda >= 0),
preco_produto numeric(10,2) not null check (preco_produto >= 0),
status_produto status_produto default 'ativo' not null,
data_cadastro timestamp default current_timestamp not null);

create table estoque(
id_estoque serial primary key unique,
id_loja integer not null references lojas(id_loja) on delete cascade,
id_produto INTEGER NOT NULL REFERENCES produtos(id_produto) ON DELETE CASCADE,
quantidade INTEGER NOT NULL DEFAULT 0 CHECK (quantidade >= 0),
quantidade_minima INTEGER NOT NULL DEFAULT 0 CHECK (quantidade_minima >= 0),
ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
CONSTRAINT unique_produto_por_loja UNIQUE (id_loja, id_produto)
);

CREATE TABLE movimentacoes_estoque (
    id_movimentacao SERIAL PRIMARY KEY,
    id_estoque INTEGER NOT NULL REFERENCES estoque(id_estoque),
    tipo_movimento VARCHAR(10) CHECK (tipo_movimento IN ('entrada', 'saida')) NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    saldo_anterior INTEGER NOT NULL,
    saldo_novo INTEGER NOT NULL,
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);