import unittest
from etl_taiga import main
from unittest.mock import patch, MagicMock


class TestMain(unittest.TestCase):

    @patch("main.insert_data")
    @patch("main.reset_database")
    @patch("main.pipeline_fact_cards")
    @patch("main.pipeline_status")
    @patch("main.pipeline_tags")
    @patch("main.pipeline_users")
    @patch("main.pipeline_roles")
    @patch("main.pipeline_projets")
    @patch("main.conectar_banco")
    def test_main_success(
        self,
        mock_conectar_banco,
        mock_pipeline_projets,
        mock_pipeline_roles,
        mock_pipeline_users,
        mock_pipeline_tags,
        mock_pipeline_status,
        mock_pipeline_fact_cards,
        mock_reset_database,
        mock_insert_data,
    ):
        # Mocks
        mock_session = MagicMock()
        mock_conectar_banco.return_value = mock_session
        mock_pipeline_projets.return_value = ["projeto1"]
        mock_pipeline_roles.return_value = ["role1"]
        mock_pipeline_users.return_value = ["user1"]
        mock_pipeline_tags.return_value = ["tag1"]
        mock_pipeline_status.return_value = ["status1"]
        mock_pipeline_fact_cards.return_value = ["fact_card1"]

        # Executa main
        main()

        # Verificações
        mock_conectar_banco.assert_called_once()
        mock_pipeline_projets.assert_called_once()
        mock_pipeline_roles.assert_called_once()
        mock_pipeline_users.assert_called_once_with(["role1"])
        mock_pipeline_tags.assert_called_once()
        mock_pipeline_status.assert_called_once()
        mock_pipeline_fact_cards.assert_called_once()
        mock_reset_database.assert_called_once_with(mock_session)
        mock_insert_data.assert_called_once_with(
            mock_session,
            ["projeto1"],
            ["role1"],
            ["user1"],
            ["tag1"],
            ["status1"],
            ["fact_card1"],
        )
        mock_session.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
