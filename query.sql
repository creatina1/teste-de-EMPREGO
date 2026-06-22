CREATE TABLE contatos (
    id BIGSERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    telefone VARCHAR(20) NOT NULL
);

-- Exemplos de inserção para testes
INSERT INTO contatos (nome, telefone) VALUES
    ('João Silva', '5511999990001'),
    ('Maria Souza', '5511999990002'),
    ('Carlos Lima', '5511999990003');
