import pytest
import sys
from unittest.mock import MagicMock, patch
from othello.command_parser import CommandKind, CommandParser
from othello.game_modes import AIMode, NormalGame
from othello.othello_board import BoardSize, Color, Bitboard


class TestAIMode:
    @pytest.fixture
    def ai_mode(self):
        """Fixture to create a basic AIMode instance"""
        return AIMode(
            board_size=BoardSize.EIGHT_BY_EIGHT, ai_color=Color.BLACK, depth=3
        )

    def test_init_with_color_string(self):
        """Test initialization with color as string"""
        # Test with lowercase string
        ai_mode = AIMode(board_size=BoardSize.EIGHT_BY_EIGHT, ai_color="black", depth=3)
        assert ai_mode.ai_color == Color.BLACK

        # Test with uppercase string
        ai_mode = AIMode(board_size=BoardSize.EIGHT_BY_EIGHT, ai_color="WHITE", depth=3)
        assert ai_mode.ai_color == Color.WHITE

    def test_init_with_invalid_color(self):
        """Test initialization with invalid color string"""
        with pytest.raises(ValueError) as excinfo:
            AIMode(board_size=BoardSize.EIGHT_BY_EIGHT, ai_color=123, depth=3)
        assert "Invalid ai_color type" in str(excinfo.value)

    def test_init_default_params(self):
        """Test default parameters"""
        ai_mode = AIMode(ai_color="black")
        assert ai_mode.board.size == BoardSize.EIGHT_BY_EIGHT
        assert ai_mode.ai_color == Color.BLACK
        assert ai_mode.depth == 3
        assert ai_mode.algorithm == "minimax"
        assert ai_mode.heuristic == "coin_parity"

    @patch("othello.game_modes.find_best_move")
    def test_get_ai_move(self, mock_find_best_move, ai_mode):
        """Test get_ai_move method with mocked find_best_move function"""
        mock_find_best_move.return_value = (3, 4)
        possible_moves = Bitboard(0x0000000810000000)  # Some dummy bitboard

        result = ai_mode.get_ai_move(possible_moves)

        # Check if find_best_move was called with correct parameters
        mock_find_best_move.assert_called_once_with(
            ai_mode.board,
            ai_mode.depth,
            ai_mode.ai_color,
            True,
            ai_mode.algorithm,
            ai_mode.heuristic,
        )
        assert result == (3, 4)

    @patch("othello.game_modes.find_best_move")
    def test_get_ai_move_no_valid_moves(self, mock_find_best_move, ai_mode):
        """Test get_ai_move method when there are no valid moves"""
        mock_find_best_move.return_value = (-1, -1)
        possible_moves = Bitboard(0)  # Empty bitboard

        result = ai_mode.get_ai_move(possible_moves)

        assert result is None

    @patch("othello.game_modes.AIMode.display_board")
    @patch("othello.game_modes.AIMode.get_possible_moves")
    @patch("othello.game_modes.AIMode.check_game_over")
    @patch("othello.game_modes.AIMode.display_possible_moves")
    @patch("othello.game_modes.AIMode.get_ai_move")
    @patch("othello.game_modes.AIMode.process_move")
    @patch("othello.game_modes.AIMode.switch_player")
    @patch("builtins.print")
    @patch("builtins.input")
    def test_play_ai_turn(
        self,
        mock_input,
        mock_print,
        mock_switch_player,
        mock_process_move,
        mock_get_ai_move,
        mock_display_possible_moves,
        mock_check_game_over,
        mock_get_possible_moves,
        mock_display_board,
        ai_mode,
    ):
        """Test play method for AI's turn"""
        # Set up the mocks
        mock_check_game_over.return_value = False
        mock_get_possible_moves.return_value = Bitboard(
            0x0000000810000000
        )  # Some dummy bitboard
        mock_get_ai_move.return_value = (3, 4)
        mock_process_move.return_value = True

        # Set current player to AI
        ai_mode.current_player = ai_mode.ai_color

        # Mock sys.exit to prevent actual exit
        with patch("sys.exit") as mock_exit, patch(
            "othello.game_modes.CommandParser"
        ) as mock_parser:
            # Set up to exit after one iteration
            mock_input.side_effect = ["quit"]
            mock_parser.return_value.parse_str.return_value = (CommandKind.QUIT, None)

            # Call play method
            ai_mode.play()

            # Verify AI made a move
            mock_get_ai_move.assert_called_once()
            mock_process_move.assert_called_once_with(
                3, 4, mock_get_possible_moves.return_value
            )
            mock_switch_player.assert_called_once()

    @patch("othello.game_modes.AIMode.display_board")
    @patch("othello.game_modes.AIMode.get_possible_moves")
    @patch("othello.game_modes.AIMode.check_game_over")
    @patch("othello.game_modes.AIMode.display_possible_moves")
    @patch("othello.game_modes.AIMode.process_move")
    @patch("othello.game_modes.AIMode.switch_player")
    @patch("builtins.print")
    @patch("builtins.input")
    def test_play_player_turn(
        self,
        mock_input,
        mock_print,
        mock_switch_player,
        mock_process_move,
        mock_display_possible_moves,
        mock_check_game_over,
        mock_get_possible_moves,
        mock_display_board,
        ai_mode,
    ):
        """Test play method for player's turn"""
        # Set up the mocks
        mock_check_game_over.return_value = False
        mock_get_possible_moves.return_value = Bitboard(
            0x0000000810000000
        )  # Some dummy bitboard
        mock_process_move.return_value = True

        # Set current player to human (opposite of AI)
        ai_mode.ai_color = Color.BLACK
        ai_mode.current_player = Color.WHITE

        # Mock the command parser
        with patch("othello.game_modes.CommandParser") as mock_parser_class:
            mock_parser = MagicMock()
            mock_parser_class.return_value = mock_parser
            mock_parser.parse_str.return_value = (
                CommandKind.PLAY_MOVE,
                MagicMock(x_coord=2, y_coord=3),
            )

            # Mock sys.exit to prevent actual exit
            with patch("sys.exit") as mock_exit:
                # Set up to exit after processing one move
                # Player move, then quit
                mock_input.side_effect = ["e3", "quit"]

                # Call play method
                ai_mode.play()

                # Verify player made a move
                mock_process_move.assert_called_once_with(
                    2, 3, mock_get_possible_moves.return_value
                )
                mock_switch_player.assert_called_once()

    @patch("othello.game_modes.AIMode.display_board")
    @patch("othello.game_modes.AIMode.get_possible_moves")
    @patch("othello.game_modes.AIMode.check_game_over")
    @patch("othello.game_modes.AIMode.display_possible_moves")
    @patch("builtins.print")
    @patch("builtins.input")
    def test_play_invalid_move(
        self,
        mock_input,
        mock_print,
        mock_display_possible_moves,
        mock_check_game_over,
        mock_get_possible_moves,
        mock_display_board,
        ai_mode,
    ):
        """Test play method with invalid player move"""
        # Set up the mocks
        mock_check_game_over.return_value = False
        mock_get_possible_moves.return_value = Bitboard(
            0x0000000810000000
        )  # Some dummy bitboard

        # Set current player to human
        ai_mode.ai_color = Color.BLACK
        ai_mode.current_player = Color.WHITE

        # Mock the command parser
        with patch("othello.game_modes.CommandParser") as mock_parser_class:
            mock_parser = MagicMock()
            mock_parser_class.return_value = mock_parser
            mock_parser.parse_str.side_effect = [
                (CommandKind.PLAY_MOVE, MagicMock(x_coord=2, y_coord=3)),
                (CommandKind.QUIT, None),
            ]

            # Mock process_move to return False (invalid move)
            with patch.object(
                ai_mode, "process_move", return_value=False
            ) as mock_process_move:
                # Mock sys.exit to prevent actual exit
                with patch("sys.exit") as mock_exit:
                    # Set up to exit after processing one move
                    # Invalid move, then quit
                    mock_input.side_effect = ["e3", "quit"]

                    # Call play method
                    ai_mode.play()

                    # Verify behavior for invalid move
                    mock_process_move.assert_called_once_with(
                        2, 3, mock_get_possible_moves.return_value
                    )
                    # Should not switch player after invalid move
                    assert not hasattr(mock_exit, "called") or not mock_exit.called


@patch("builtins.input")
def test_play_forfeit(self, mock_input, capsys):
    """Test that FORFEIT command works correctly in AIMode."""
    # Setup input mock
    mock_input.return_value = "forfeit"

    with patch(
        "othello.game_modes.AIMode.__init__",
        side_effect=lambda self, *args, **kwargs: self.__patch_init__(*args, **kwargs),
    ):
        ai_mode = AIMode(ai_color="black")
        # Set current player to human
        ai_mode.ai_color = Color.BLACK
        ai_mode.current_player = Color.WHITE

        # Mock the command parser
        with patch("othello.game_modes.CommandParser") as mock_parser_class:
            mock_parser = MagicMock()
            mock_parser_class.return_value = mock_parser
            mock_parser.parse_str.return_value = (CommandKind.FORFEIT, None)

            # Mock other methods
            ai_mode.display_board = MagicMock()
            ai_mode.get_possible_moves = MagicMock(return_value=Bitboard(1))
            ai_mode.check_game_over = MagicMock(return_value=False)
            ai_mode.display_possible_moves = MagicMock()
            ai_mode.switch_player = MagicMock()

            # Run the test
            with pytest.raises(SystemExit) as e:
                ai_mode.play()

            # Verify exit code
            assert e.value.code == 0

            # Verify output and player switch
            captured = capsys.readouterr()
            assert "forfeited" in captured.out
            assert "wins" in captured.out
            ai_mode.switch_player.assert_called_once()
