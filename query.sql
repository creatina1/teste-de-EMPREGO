CREATE TABLE contatos (
    id BIGSERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    telefone VARCHAR(20) NOT NULL
);

-- Exemplos de inserção para testes
INSERT INTO contatos (nome, telefone) VALUES
    ('João Monteiro', '5516997002506'),
    ('Maria Monteiro', '5516997333836');
