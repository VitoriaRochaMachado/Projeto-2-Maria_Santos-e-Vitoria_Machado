import pytest 
from unittest.mock import MagicMock, patch
from api import app 

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@patch("api.conectar_banco")
def test_deletar_imovel_ok(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.rowcount = 1

    mock_conectar_banco.return_value = mock_conn

    response = client.delete("/imovel/1")

    assert response.stauts_code == 200
    assert response.get_json() == {"Mensagem": "imóvel excluído com sucesso"}

    mock_cursor.execute.assert_called_once_with("DELETE FROM imoveis WHERE id = % ", (1,))

    mock_conn.commit.assert_called_once_with() #verifica se o commit é executado uma única vez
    mock_cursor.close.assert_called_once_with() #testa se cursor é fecahdo uma única vez
    mock_conn.close.assert_called_once_with() # o mesmo com o conn

@patch("api.conectar_banco")
def test_deletar_imovel_inexistente(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_rowcount = 0

    mock_conectar_banco.return_value = mock_conn
    response = client.delete("/imovel/99999")

    assert response.status_code == 404
    assert response.get_json() == {"erro": "Imóvel não encontrado"}

    mock_cursor.execute.assert_called_once_with("DELETE FROM imoveis WHERE id = %s ", (99999,))

    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("api.conectar_banco")
def test_busca_tipo_ok(mock_conectar_banco, client, tipo):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = [(1,'Nicole Common', 'Travessa', 'Lake Danielle', 'Judymouth', '85184', 'casa em condominio', 488423.52, '2017-07-29'),
                                         (2, 'Price Prairie', 'Travessa', 'Colonton', 'North Garyville', '93354', 'casa em condominio', 260069.89, '2021-11-30'),
                                         (3, 'Taylor Ranch', 'Avenida', 'West Jennashire', 'Katherinefurt', '51116', 'apartamento', 815969.92, '2020-04-24'),
                                         (4, 'Stacey Isle', 'Avenida', 'Reneeberg', 'Bentleymouth', '01631', 'terreno', 352507.35, '2014-11-03')]

    mock_conectar_banco.return_value = mock_conn

    response = client.get_json('/imovel/tipo')

    assert response.status_code == 200
    assert response.get_json == [{'id':1, 'logradouro':'Nicole Common', 'tipo_logradouro':'Travessa', 'bairro':'Lake Danielle', 'cidade':'Judymouth', 'cep':'85184','tipo': 'casa em condominio', 'valor': 488423.52, 'data_aquisicao':'2017-07-29'},
                                 {'id': 2, 'logradouro':'Price Prairie', 'tipo_logradouro':'Travessa', 'bairro':'Colonton', 'cidade':'North Garyville', 'cep':'93354', 'tipo':'casa em condominio', 'valor':260069.89, 'data_aquisicao':'2021-11-30'}]

    mock_cursor.execute.assert_called_once_with(
        "SELECT logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao FROM imoveis WHERE tipo = %s", ('tipo_logradouro',)
    )

    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('api.conectar_banco')
def test_busca_tipo_vazio(mock_conectar_banco, client):
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = []

    mock_conectar_banco.return_value = mock_conn
    response = client.get("/imovel/tipo")

    assert response.status_code == 200
    assert response.get_json() == []

    mock_cursor.execute.assert_called_once_with(
            "SELECT logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao FROM imoveis WHERE tipo = %s", ('tipo_logradouro',)
        )
    
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("api.conectar_banco")
def test_busca_cidade_ok(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = [(1,'Nicole Common', 'Travessa', 'Lake Danielle', 'Judymouth', '85184', 'casa em condominio', 488423.52, '2017-07-29'),
                                         (2, 'Price Prairie', 'Travessa', 'Colonton', 'North Garyville', '93354', 'casa em condominio', 260069.89, '2021-11-30'),
                                         (3, 'Taylor Ranch', 'Avenida', 'West Jennashire', 'Katherinefurt', '51116', 'apartamento', 815969.92, '2020-04-24'),
                                         (4, 'Stacey Isle', 'Avenida', 'Reneeberg', 'Bentleymouth', '01631', 'terreno', 352507.35, '2014-11-03')]

    mock_conectar_banco.return_value = mock_conn

    response = client.get_json('/imovel/cidade')

    assert response.status_code == 200
    assert response.get_json == [{'id':1, 'logradouro':'Nicole Common', 'tipo_logradouro':'Travessa', 'bairro':'Lake Danielle', 'cidade':'Judymouth', 'cep':'85184','tipo': 'casa em condominio', 'valor': 488423.52, 'data_aquisicao':'2017-07-29'},]

    mock_cursor.execute.assert_called_once_with(
        "SELECT logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao FROM imoveis WHERE cidade = %s", ('Judymouth',)
    )

    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('api.conectar_banco')
def test_busca_cidade_vazio(mock_conectar_banco, client):
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = []

    mock_conectar_banco.return_value = mock_conn
    response = client.get("/imovel/cidade")

    assert response.status_code == 200
    assert response.get_json() == []

    mock_cursor.execute.assert_called_once_with(
            "SELECT logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao FROM imoveis WHERE cidade = %s", ('JudymouthMM',)
        )
    
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()