"""简单终端扫雷 (Minesweeper)

使用说明:
 - 输入格式: r 行 列   -> 翻开单元格 (reveal)
 - 输入格式: f 行 列   -> 标记/取消标记为地雷 (flag)
 - 行列索引从 0 开始 (0..rows-1, 0..cols-1)
 - 输入 q 或 quit 退出
 - 默认大小: 9x9, 炸弹 10
"""

import random
import sys
from typing import List, Set, Tuple


def make_board(rows: int, cols: int, mines: int) -> Tuple[List[List[int]], Set[Tuple[int,int]]]:
	coords = [(r, c) for r in range(rows) for c in range(cols)]
	mine_cells = set(random.sample(coords, mines))
	board = [[0 for _ in range(cols)] for _ in range(rows)]
	for (r, c) in mine_cells:
		board[r][c] = -1
		for dr in (-1, 0, 1):
			for dc in (-1, 0, 1):
				nr, nc = r + dr, c + dc
				if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != -1:
					board[nr][nc] += 1
	return board, mine_cells


def display(rows: int, cols: int, revealed: List[List[bool]], flagged: List[List[bool]],
			board: List[List[int]], show_mines: bool = False) -> None:
	# header
	print("   ", end="")
	for c in range(cols):
		print(f"{c:2}", end=" ")
	print()
	print("   " + "---" * cols)
	for r in range(rows):
		print(f"{r:2}|", end=" ")
		for c in range(cols):
			if revealed[r][c]:
				if board[r][c] == -1:
					ch = "*"
				elif board[r][c] == 0:
					ch = " "
				else:
					ch = str(board[r][c])
			else:
				if flagged[r][c]:
					ch = "F"
				else:
					if show_mines and board[r][c] == -1:
						ch = "*"
					else:
						ch = "#"
			print(f" {ch}", end=" ")
		print()


def flood_reveal(r: int, c: int, rows: int, cols: int, board: List[List[int]], revealed: List[List[bool]]):
	stack = [(r, c)]
	while stack:
		x, y = stack.pop()
		if revealed[x][y]:
			continue
		revealed[x][y] = True
		if board[x][y] == 0:
			for dx in (-1, 0, 1):
				for dy in (-1, 0, 1):
					nx, ny = x + dx, y + dy
					if 0 <= nx < rows and 0 <= ny < cols and not revealed[nx][ny]:
						if board[nx][ny] == 0:
							stack.append((nx, ny))
						else:
							revealed[nx][ny] = True


def check_win(rows: int, cols: int, board: List[List[int]], revealed: List[List[bool]]) -> bool:
	for r in range(rows):
		for c in range(cols):
			if board[r][c] != -1 and not revealed[r][c]:
				return False
	return True


def parse_cmd(s: str):
	parts = s.strip().split()
	if not parts:
		return None
	cmd = parts[0].lower()
	if cmd in ("q", "quit", "exit"):
		return ("quit",)
	if cmd in ("r", "f"):
		if len(parts) < 3:
			return None
		try:
			r = int(parts[1])
			c = int(parts[2])
		except ValueError:
			return None
		return (cmd, r, c)
	return None


def play(rows: int = 9, cols: int = 9, mines: int = 10):
	if mines >= rows * cols:
		print("炸弹数量必须少于格子总数")
		return
	board, mine_cells = make_board(rows, cols, mines)
	revealed = [[False] * cols for _ in range(rows)]
	flagged = [[False] * cols for _ in range(rows)]
	alive = True

	print(f"扫雷：{rows}x{cols}, 炸弹 {mines}")
	print("提示: 输入 'r 行 列' 翻开, 'f 行 列' 标记, 行列从 0 开始, 输入 q 退出")

	while True:
		display(rows, cols, revealed, flagged, board, show_mines=False)
		if check_win(rows, cols, board, revealed):
			print("你赢了！恭喜！")
			display(rows, cols, revealed, flagged, board, show_mines=True)
			break

		s = input("> ")
		cmd = parse_cmd(s)
		if cmd is None:
			print("无效指令。示例: r 2 3 或 f 1 1 或 q")
			continue
		if cmd[0] == "quit":
			print("退出游戏")
			break

		action, r, c = cmd[0], cmd[1], cmd[2]
		if not (0 <= r < rows and 0 <= c < cols):
			print("坐标越界")
			continue

		if action == "f":
			if revealed[r][c]:
				print("该格已翻开，不能标记")
			else:
				flagged[r][c] = not flagged[r][c]
		elif action == "r":
			if flagged[r][c]:
				print("该格已被标记为地雷，先取消标记后再翻开")
				continue
			if board[r][c] == -1:
				# 踩雷
				print("BOOM！你踩到地雷了。")
				# 展示所有地雷
				display(rows, cols, revealed, flagged, board, show_mines=True)
				break
			else:
				flood_reveal(r, c, rows, cols, board, revealed)


if __name__ == "__main__":
	# 允许从命令行传入 rows cols mines
	try:
		if len(sys.argv) >= 4:
			r = int(sys.argv[1])
			c = int(sys.argv[2])
			m = int(sys.argv[3])
			play(r, c, m)
		else:
			play()
	except KeyboardInterrupt:
		print("\n中断，退出")
