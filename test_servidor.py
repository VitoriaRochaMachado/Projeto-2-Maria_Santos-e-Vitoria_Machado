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

    resultado = resposta.get_json()

    assert resposta.status_code == 200
    assert resultado[0]["id"] == 1
    assert resultado[0]["logradouro"] == "Paulista"

    verificar_links_imovel(resultado[0], 1)
    

    mock_conectar_banco.assert_called_once()
    conn_mock.cursor.assert_called_once_with(dictionary=True)
    cursor_mock.execute.assert_called_once_with(
        "SELECT * FROM imoveis"
    )
    cursor_mock.fetchall.assert_called_once()
    cursor_mock.close.assert_called_once()
    conn_mock.close.assert_called_once()

@patch("servidor.conectar_banco")
def test_buscar_imoveis_existente(mock_conectar_banco, client):
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
    resultado = resposta.get_json()

    assert resultado["id"] == 1
    assert resultado["logradouro"] == "Paulista"
    assert resultado["tipo"] == "apartamento"
    
    verificar_links_imovel(resultado, 1)
    

@patch("servidor.conectar_banco")
def test_buscar_imoveis_inexistente(mock_conectar_banco, client):
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
def test_adicionar_imoveis(mock_conectar_banco, client):
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

    resultado = resposta.get_json()

    assert resposta.status_code == 201
    assert resultado["id"] == 10
    assert resultado["logradouro"] == "Paulista"
    assert resultado["tipo"] == "apartamento"
    
    verificar_links_imovel(resultado, 10)

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
def test_adicionar_imoveis_sem_json(
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
def test_adicionar_imoveis_com_campo_faltando(
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
def test_atualizar_imoveis(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conectar_banco.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    dados_atualizados = {
        "logradouro": "Paulista Nova",
        "tipo_logradouro": "Avenida",
        "bairro": "Bela Vista",
        "cidade": "São Paulo",
        "cep": "01310-100",
        "tipo": "apartamento",
        "valor": 900000.0,
        "data_aquisicao": "2025-04-15"
    }

    imovel_atualizado = {
        "id": 1,
        "logradouro": "Paulista Nova",
        "tipo_logradouro": "Avenida",
        "bairro": "Bela Vista",
        "cidade": "São Paulo",
        "cep": "01310-100",
        "tipo": "apartamento",
        "valor": 900000.0,
        "data_aquisicao": "2025-04-15"
    }

    # Primeiro fetchone: verifica que o imóvel existe.
    # Segundo fetchone: devolve o imóvel atualizado.
    mock_cursor.fetchone.side_effect = [
        {"id": 1},
        imovel_atualizado
    ]

    resposta = client.put(
        "/imoveis/1",
        json=dados_atualizados
    )


        

    resultado = resposta.get_json()

    assert resposta.status_code == 200
    assert resultado["id"] == 1
    assert resultado["logradouro"] == "Paulista Nova"
    assert resultado["valor"] == 900000.0

    verificar_links_imovel(resultado, 1)

    mock_conectar_banco.assert_called_once()
    mock_conn.cursor.assert_called_once_with(dictionary=True)

    # A função executa três comandos:
    # SELECT para verificar, UPDATE e SELECT para retornar.
    assert mock_cursor.execute.call_count == 3

    chamadas = mock_cursor.execute.call_args_list

    assert chamadas[0].args == (
        "SELECT id FROM imoveis WHERE id = %s",
        (1,)
    )

    assert "UPDATE imoveis" in chamadas[1].args[0]

    valores_esperados = (
        "Paulista Nova",
        "Avenida",
        "Bela Vista",
        "São Paulo",
        "01310-100",
        "apartamento",
        900000.0,
        "2025-04-15",
        1
    )

    assert chamadas[1].args[1] == valores_esperados

    assert chamadas[2].args == (
        "SELECT * FROM imoveis WHERE id = %s",
        (1,)
    )

    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("servidor.conectar_banco")
def test_atualizar_imoveis_inexistente(
    mock_conectar_banco,
    client
):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conectar_banco.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Simula que o imóvel não foi encontrado.
    mock_cursor.fetchone.return_value = None

    dados_atualizados = {
        "logradouro": "Paulista Nova",
        "tipo_logradouro": "Avenida",
        "bairro": "Bela Vista",
        "cidade": "São Paulo",
        "cep": "01310-100",
        "tipo": "apartamento",
        "valor": 900000.0,
        "data_aquisicao": "2025-04-15"
    }

    resposta = client.put(
        "/imoveis/999",
        json=dados_atualizados
    )

    assert resposta.status_code == 404

    assert resposta.get_json() == {
        "erro": "Imóvel não encontrado"
    }

    mock_cursor.execute.assert_called_once_with(
        "SELECT id FROM imoveis WHERE id = %s",
        (999,)
    )

    # Não deve atualizar nem salvar nada.
    mock_conn.commit.assert_not_called()

    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("servidor.conectar_banco")
def test_atualizar_imoveis_sem_json(
    mock_conectar_banco,
    client
):
    resposta = client.put(
        "/imoveis/1",
        data="null",
        content_type="application/json"
    )

    assert resposta.status_code == 400

    assert resposta.get_json() == {
        "erro": "É necessário enviar um JSON"
    }

    # O erro acontece antes da conexão.
    mock_conectar_banco.assert_not_called()


@patch("servidor.conectar_banco")
def test_atualizar_imoveis_com_campo_faltando(
    mock_conectar_banco,
    client
):
    # Não colocamos data_aquisicao.
    dados_incompletos = {
        "logradouro": "Paulista Nova",
        "tipo_logradouro": "Avenida",
        "bairro": "Bela Vista",
        "cidade": "São Paulo",
        "cep": "01310-100",
        "tipo": "apartamento",
        "valor": 900000.0
    }

    resposta = client.put(
        "/imoveis/1",
        json=dados_incompletos
    )

    assert resposta.status_code == 400

    assert resposta.get_json() == {
        "erro": "Campos faltando",
        "campos": ["data_aquisicao"]
    }

    # O erro acontece antes da conexão.
    mock_conectar_banco.assert_not_called()
    
@patch("servidor.conectar_banco")
def test_deletar_imoveis_ok(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.rowcount = 1

    mock_conectar_banco.return_value = mock_conn

    resposta = client.delete("/imoveis/1")

    assert resposta.status_code == 200

    resultado = resposta.get_json()

    assert resultado["Mensagem"] == "imóvel excluído com sucesso"
    assert resultado["_links"]["collection"]["href"] == "/imoveis"

    mock_cursor.execute.assert_called_once_with('DELETE FROM imoveis WHERE id = %s', (1,))

    mock_conn.commit.assert_called_once_with() #verifica se o commit é executado uma única vez
    mock_cursor.close.assert_called_once_with() #testa se cursor é fecahdo uma única vez
    mock_conn.close.assert_called_once_with() # o mesmo com o conn

@patch("servidor.conectar_banco")
def test_deletar_imoveis_inexistente(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.rowcount = 0

    mock_conectar_banco.return_value = mock_conn
    response = client.delete("/imoveis/99999")

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

    mock_cursor.fetchall.return_value = [{'id':4,
                                          'logradouro': 'Stacey Isle', 
                                          'tipo_logradouro':'Avenida', 
                                          'bairro':'Reneeberg', 
                                          'cidade':'Bentleymouth', 
                                          'cep':'01631', 
                                          'tipo':'terreno', 
                                          'valor':352507.35, 
                                          'data_aquisicao':'2014-11-03'}]

    mock_conectar_banco.return_value = mock_conn

    resposta = client.get('/imoveis/tipo/terreno')

    assert resposta.status_code == 200

    resultado = resposta.get_json()

    assert resultado[0]["id"] == 4
    assert resultado[0]["logradouro"] == "Stacey Isle"
    assert resultado[0]["tipo"] == "terreno"

    verificar_links_imovel(resultado[0], 4)

    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('servidor.conectar_banco')
def test_busca_tipo_vazio(mock_conectar_banco, client):
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = []

    mock_conectar_banco.return_value = mock_conn
    resposta = client.get("/imoveis/tipo/terreno")

    assert resposta.status_code == 200
    chamada = mock_cursor.execute.call_args

    assert "SELECT id, logradouro, tipo_logradouro, bairro" in chamada.args[0]
    assert "FROM imoveis" in chamada.args[0]
    assert "WHERE tipo = %s" in chamada.args[0]
    assert chamada.args[1] == ("terreno",)
    
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("servidor.conectar_banco")
def test_busca_cidade_ok(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = [{'id':1,
        'logradouro':"Nicole Common",
        'tipo_logradouro':"Travessa",
        'bairro':"Lake Danielle",
        'cidade':"Judymouth",
        'cep':"85184",
        'tipo':"casa em condominio",
        'valor':488423.52,
        'data_aquisicao': "2017-07-29"}]

    mock_conectar_banco.return_value = mock_conn

    resposta = client.get('/imoveis/cidade/Judymouth')

    assert resposta.status_code == 200

    resultado = resposta.get_json()

    assert resultado[0]["id"] == 1
    assert resultado[0]["cidade"] == "Judymouth"

    verificar_links_imovel(resultado[0], 1)

    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch('servidor.conectar_banco')
def test_busca_cidade_vazio(mock_conectar_banco, client):
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = []

    mock_conectar_banco.return_value = mock_conn
    response = client.get("/imoveis/cidade/Teste_nao_existe")

    assert response.status_code == 200
    chamada = mock_cursor.execute.call_args

    assert "SELECT id, logradouro, tipo_logradouro, bairro" in chamada.args[0]
    assert "FROM imoveis" in chamada.args[0]
    assert "WHERE cidade = %s" in chamada.args[0]
    assert chamada.args[1] == ("Teste_nao_existe",)
    
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

def verificar_links_imovel(imovel, id):
    assert "_links" in imovel

    assert imovel["_links"]["self"]["href"] == f"/imoveis/{id}"

    assert imovel["_links"]["collection"]["href"] == "/imoveis"

    assert imovel["_links"]["update"]["href"] == f"/imoveis/{id}"
    assert imovel["_links"]["update"]["method"] == "PUT"

    assert imovel["_links"]["delete"]["href"] == f"/imoveis/{id}"
    assert imovel["_links"]["delete"]["method"] == "DELETE"