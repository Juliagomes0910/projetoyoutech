CREATE TABLE IF NOT EXISTS vagas (
    id_vaga INTEGER PRIMARY KEY,
    cargo_vaga TEXT NOT NULL,
    requi_vaga TEXT NOT NULL,
    salario_vaga REAL NOT NULL,
    img_vaga TEXT NOT NULL,
    local_vaga TEXT NOT NULL,
    tipo_vaga TEXT NOT NULL
);