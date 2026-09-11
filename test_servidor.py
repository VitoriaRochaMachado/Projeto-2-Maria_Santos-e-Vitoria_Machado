import pytest 
from unittest.mock import MagicMock, patch
from servidor import app 

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@patch("servidor.conectar_banco")
def test_listar_imoveis(mock_conectar_banco, client):
    conn_mock = MagicMock()
    cursor_mock = MagicMock()

    mock_conectar_banco.return_value = conn_mock
    conn_mock.cursor.return_value = cursor_mock

    imoveis_falsos = [
        {
            "id": 1,
            "logradouro": "Paulista",
            "tipo_logradouro": "Avenida",
            "bairro": "Bela Vista",
            "cidade": "São Paulo",
            "cep": "01310-100",
            "tipo": "apartamento",
            "valor": 850000.0,
            "data_aquisicao": "2025-04-15"
        }
    ]

    cursor_mock.fetchall.return_value = imoveis_falsos

    resposta = client.get("/imoveis")

    assert resposta.status_code == 200
    assert resposta.get_json() == imoveis_falsos

    mock_conectar_banco.assert_called_once()
    conn_mock.cursor.assert_called_once_with(dictionary=True)
    cursor_mock.execute.assert_called_once_with(
        "SELECT * FROM imoveis"
    )
    cursor_mock.fetchall.assert_called_once()
    cursor_mock.close.assert_called_once()
    conn_mock.close.assert_called_once()

@patch("servidor.conectar_banco")
def test_buscar_imovel_existente(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conectar_banco.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    imovel_falso = {
        "id": 1,
        "logradouro": "Paulista",
        "tipo_logradouro": "Avenida",
        "bairro": "Bela Vista",
        "cidade": "São Paulo",
        "cep": "01310-100",
        "tipo": "apartamento",
        "valor": 850000.0,
        "data_aquisicao": "2025-04-15"
    }

    mock_cursor.fetchone.return_value = imovel_falso

    resposta = client.get("/imoveis/1")

    assert resposta.status_code == 200
    assert resposta.get_json() == imovel_falso

@patch("servidor.conectar_banco")
def test_buscar_imovel_inexistente(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conectar_banco.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchone.return_value = None

    resposta = client.get("/imoveis/999")

    assert resposta.status_code == 404
    assert resposta.get_json() == {
        "erro": "Imóvel não encontrado"
    }

@patch("servidor.conectar_banco")
def test_adicionar_imovel(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conectar_banco.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    
    mock_cursor.lastrowid = 10

    dados_imovel = {
        "logradouro": "Paulista",
        "tipo_logradouro": "Avenida",
        "bairro": "Bela Vista",
        "cidade": "São Paulo",
        "cep": "01310-100",
        "tipo": "apartamento",
        "valor": 850000.0,
        "data_aquisicao": "2025-04-15"
    }

    resposta = client.post(
        "/imoveis",
        json=dados_imovel
    )

    resultado_esperado = {
        "id": 10,
        "logradouro": "Paulista",
        "tipo_logradouro": "Avenida",
        "bairro": "Bela Vista",
        "cidade": "São Paulo",
        "cep": "01310-100",
        "tipo": "apartamento",
        "valor": 850000.0,
        "data_aquisicao": "2025-04-15"
    }

    assert resposta.status_code == 201
    assert resposta.get_json() == resultado_esperado

    mock_conectar_banco.assert_called_once()
    mock_conn.cursor.assert_called_once()
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

    valores_esperados = (
        "Paulista",
        "Avenida",
        "Bela Vista",
        "São Paulo",
        "01310-100",
        "apartamento",
        850000.0,
        "2025-04-15"
    )

    argumentos_execute = mock_cursor.execute.call_args.args
    valores_enviados = argumentos_execute[1]

    assert valores_enviados == valores_esperados


@patch("servidor.conectar_banco")
def test_adicionar_imovel_sem_json(
    mock_conectar_banco,
    client
):
    resposta = client.post(
        "/imoveis",
        data="null",
        content_type="application/json"
    )

    assert resposta.status_code == 400

    assert resposta.get_json() == {
        "erro": "É necessário enviar um JSON"
    }

    
    mock_conectar_banco.assert_not_called()


@patch("servidor.conectar_banco")
def test_adicionar_imovel_com_campo_faltando(
    mock_conectar_banco,
    client
):
    
    dados_incompletos = {
        "logradouro": "Paulista",
        "tipo_logradouro": "Avenida",
        "bairro": "Bela Vista",
        "cidade": "São Paulo",
        "cep": "01310-100",
        "tipo": "apartamento",
        "valor": 850000.0
    }

    resposta = client.post(
        "/imoveis",
        json=dados_incompletos
    )

    assert resposta.status_code == 400

    assert resposta.get_json() == {
        "erro": "Campos faltando",
        "campos": ["data_aquisicao"]
    }

    
    mock_conectar_banco.assert_not_called()

@patch("servidor.conectar_banco")
def test_deletar_imovel_ok(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.rowcount = 1

    mock_conectar_banco.return_value = mock_conn

    response = client.delete("/imovel/1")

    assert response.status_code == 200
    assert response.get_json() == {"Mensagem": "imóvel excluído com sucesso"}

    mock_cursor.execute.assert_called_once_with('DELETE FROM imoveis WHERE id = %s', (1,))

    mock_conn.commit.assert_called_once_with() #verifica se o commit é executado uma única vez
    mock_cursor.close.assert_called_once_with() #testa se cursor é fecahdo uma única vez
    mock_conn.close.assert_called_once_with() # o mesmo com o conn

@patch("servidor.conectar_banco")
def test_deletar_imovel_inexistente(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.rowcount = 0

    mock_conectar_banco.return_value = mock_conn
    response = client.delete("/imovel/99999")

    assert response.status_code == 404
    assert response.get_json() == {"erro": "Imóvel não encontrado"}

    mock_cursor.execute.assert_called_once_with("DELETE FROM imoveis WHERE id = %s", (99999,))

    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("servidor.conectar_banco")
def test_busca_tipo_ok(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = [(4, 'Stacey Isle', 'Avenida', 'Reneeberg', 'Bentleymouth', '01631', 'terreno', 352507.35, '2014-11-03')]

    mock_conectar_banco.return_value = mock_conn

    response = client.get('/imovel/terreno')

    assert response.status_code == 200
    assert response.get_json() == [{'id':4, 'logradouro':'Stacey Isle', 'tipo_logradouro':'Avenida', 'bairro':'Reneeberg', 'cidade':'Bentleymouth', 'cep':'01631','tipo': 'terreno', 'valor': 352507.35, 'data_aquisicao':'2014-11-03'},
                                 ]

    mock_cursor.execute.assert_called_once_with(
        "SELECT logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao FROM imoveis WHERE tipo = %s", ('terreno',)
    )

    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('servidor.conectar_banco')
def test_busca_tipo_vazio(mock_conectar_banco, client):
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = []

    mock_conectar_banco.return_value = mock_conn
    response = client.get("/imovel/terreno")

    assert response.status_code == 200
    assert response.get_json() == []

    mock_cursor.execute.assert_called_once_with(
            "SELECT logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao FROM imoveis WHERE tipo = %s", ('terreno',)
        )
    
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("servidor.conectar_banco")
def test_busca_cidade_ok(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = [( 1,
        "Nicole Common",
        "Travessa",
        "Lake Danielle",
        "Judymouth",
        "85184",
        "casa em condominio",
        488423.52,
        "2017-07-29")]

    mock_conectar_banco.return_value = mock_conn

    response = client.get('/imovel/Judymouth')

    assert response.status_code == 200
    assert response.get_json() == [{'id': 1, 'logradouro':'Nicole Common', 'tipo_logradouro':'Travessa', 'bairro':'Lake Danielle', 'cidade':'Judymouth', 'cep':'85184','tipo': 'casa em condominio', 'valor': 488423.52, 'data_aquisicao':'2017-07-29'},]

    mock_cursor.execute.assert_called_once_with(
        "SELECT id, logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao FROM imoveis WHERE cidade = %s", ('Judymouth',)
    )

    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('servidor.conectar_banco')
def test_busca_cidade_vazio(mock_conectar_banco, client):
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = []

    mock_conectar_banco.return_value = mock_conn
    response = client.get("/imovel/Teste_nao_existe")

    assert response.status_code == 200
    assert response.get_json() == []

    mock_cursor.execute.assert_called_once_with(
            "SELECT id, logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao FROM imoveis WHERE cidade = %s", ('Teste_nao_existe',)
        )
    
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()