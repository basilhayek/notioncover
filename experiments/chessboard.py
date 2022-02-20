import chess
import chess.svg
from cairosvg import svg2png
board = chess.Board()
svgboard = chess.svg.board(board, size=800)
svg2png(bytestring=svgboard,write_to='./output.png')