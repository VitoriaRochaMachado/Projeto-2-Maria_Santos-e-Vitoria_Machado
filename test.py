import pytest 
from unittest.mock import MagicMock, patch
from api import app 

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@patch("api.conectar_banco")
def test_deletar_imovel(mock_conectar_banco, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.rowcount = 1

    mock_conectar_banco.return_value = mock_conn

    response = client.delete("/imovel/1")

    assert response.stauts_code == 200
    assert response.get_json() == {"Mensagem": "imóvel excluído com sucesso"}

    mock_cursor.execute.assert_called_once_with("DELETE FROM imoveis WHERE id = % ", (1,))

    mock_conn.commit.assert_called_once_with()
    mock_cursor.close.assert_called_once_with()
    mock_conn.close.assert_called_once_with()