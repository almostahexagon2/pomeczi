import tkinter as tk

class PomecziGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Pomeczi")
        self.root.geometry("600x700")
        self.root.configure(bg='#f0f0f0')
        
        # Game state
        self.current_player = 'red'
        self.selected_piece = None
        self.game_board = [[None for _ in range(4)] for _ in range(4)]
        self.move_history = []
        self.selected_push_block = None
        self.is_pushing = False
        
        # Track available pieces for each player
        self.player_pieces = {
            'red': {'1x1': 2, '2x1': 1},
            'green': {'1x1': 2, '2x1': 1}
        }
        
        self.setup_ui()
        self.update_display()
        
    def setup_ui(self):
        # Title
        title_label = tk.Label(self.root, text="Pomeczi", font=("Arial", 24, "bold"), 
                              bg='#f0f0f0', fg='#333')
        title_label.pack(pady=10)
        
        # Game info
        self.info_frame = tk.Frame(self.root, bg='#f0f0f0')
        self.info_frame.pack(pady=10)
        
        self.current_player_label = tk.Label(self.info_frame, text="Current Player: Red", 
                                           font=("Arial", 16, "bold"), bg='#f0f0f0', fg='#d32f2f')
        self.current_player_label.pack()
        
        self.instructions_label = tk.Label(self.info_frame, 
                                         text="Select a piece to place, or click your blocks to push them",
                                         font=("Arial", 12), bg='#f0f0f0', fg='#666')
        self.instructions_label.pack()
        
        # Piece selection
        self.pieces_frame = tk.Frame(self.root, bg='#f0f0f0')
        self.pieces_frame.pack(pady=20)
        
        self.piece_buttons = {}
        for piece_type in ['1x1', '2x1']:
            btn = tk.Button(self.pieces_frame, text=f"{piece_type} Block", 
                          font=("Arial", 12), width=15, height=3,
                          command=lambda p=piece_type: self.select_piece(p),
                          relief='raised', bd=3)
            btn.pack(side=tk.LEFT, padx=10)
            self.piece_buttons[piece_type] = btn
        
        # Game grid
        self.grid_frame = tk.Frame(self.root, bg='#000', relief='raised', bd=4)
        self.grid_frame.pack(pady=20)
        
        self.cells = []
        for i in range(4):
            row = []
            for j in range(4):
                cell = tk.Button(self.grid_frame, width=10, height=5,
                               command=lambda r=i, c=j: self.handle_cell_click(r, c),
                               relief='raised', bd=2, font=("Arial", 16))
                cell.grid(row=i, column=j, padx=1, pady=1)
                row.append(cell)
            self.cells.append(row)
        
        # Controls
        controls_frame = tk.Frame(self.root, bg='#f0f0f0')
        controls_frame.pack(pady=20)
        
        undo_btn = tk.Button(controls_frame, text="Undo Move", font=("Arial", 12),
                           command=self.undo_move, bg='#ff9800', fg='white')
        undo_btn.pack(side=tk.LEFT, padx=10)
        
        reset_btn = tk.Button(controls_frame, text="Reset Game", font=("Arial", 12),
                            command=self.reset_game, bg='#f44336', fg='white')
        reset_btn.pack(side=tk.LEFT, padx=10)
    
    def select_piece(self, piece_type):
        if self.is_pushing:
            return
        
        if self.player_pieces[self.current_player][piece_type] <= 0:
            return
        
        # Clear previous selection
        for btn in self.piece_buttons.values():
            btn.configure(bg='white', relief='raised')
        
        # Select new piece
        self.selected_piece = piece_type
        self.selected_push_block = None
        self.piece_buttons[piece_type].configure(bg='#e3f2fd', relief='sunken')
        
        self.update_grid_highlights()
    
    def handle_cell_click(self, row, col):
        if self.is_pushing:
            return
        
        # Check if clicking on a block to push
        if (self.game_board[row][col] and 
            self.game_board[row][col]['player'] == self.current_player and 
            not self.selected_push_block):
            self.selected_push_block = (row, col)
            self.highlight_push_targets(row, col)
            return
        
        # Check if clicking on a push target
        if self.selected_push_block:
            direction = self.get_push_direction(self.selected_push_block[0], 
                                              self.selected_push_block[1], row, col)
            if direction and self.can_push_in_direction(self.selected_push_block[0], 
                                                      self.selected_push_block[1], direction):
                self.execute_push(self.selected_push_block[0], self.selected_push_block[1], direction)
                self.clear_highlights()
                self.selected_push_block = None
                self.switch_player()
                return
            else:
                # Invalid push, reset selection
                self.clear_highlights()
                self.selected_push_block = None
                return
        
        # Regular piece placement
        if self.selected_piece:
            if self.place_piece(row, col):
                self.clear_highlights()
                self.switch_player()
    
    def place_piece(self, row, col):
        piece_id = len(self.move_history) + 1
        
        if self.selected_piece == '1x1':
            if (self.game_board[row][col] is None and 
                self.player_pieces[self.current_player]['1x1'] > 0):
                self.game_board[row][col] = {
                    'player': self.current_player, 
                    'piece_id': piece_id, 
                    'type': '1x1'
                }
                self.player_pieces[self.current_player]['1x1'] -= 1
                self.move_history.append({
                    'row': row, 'col': col, 'player': self.current_player, 
                    'type': '1x1', 'piece_id': piece_id
                })
                self.update_display()
                return True
        
        elif self.selected_piece == '2x1':
            # Try horizontal placement
            if (col < 3 and 
                self.game_board[row][col] is None and 
                self.game_board[row][col + 1] is None and 
                self.player_pieces[self.current_player]['2x1'] > 0):
                self.game_board[row][col] = {
                    'player': self.current_player, 
                    'piece_id': piece_id, 
                    'type': '2x1-h'
                }
                self.game_board[row][col + 1] = {
                    'player': self.current_player, 
                    'piece_id': piece_id, 
                    'type': '2x1-h'
                }
                self.player_pieces[self.current_player]['2x1'] -= 1
                self.move_history.append({
                    'row': row, 'col': col, 'player': self.current_player, 
                    'type': '2x1-h', 'piece_id': piece_id
                })
                self.update_display()
                return True
            
            # Try vertical placement
            elif (row < 3 and 
                  self.game_board[row][col] is None and 
                  self.game_board[row + 1][col] is None and 
                  self.player_pieces[self.current_player]['2x1'] > 0):
                self.game_board[row][col] = {
                    'player': self.current_player, 
                    'piece_id': piece_id, 
                    'type': '2x1-v'
                }
                self.game_board[row + 1][col] = {
                    'player': self.current_player, 
                    'piece_id': piece_id, 
                    'type': '2x1-v'
                }
                self.player_pieces[self.current_player]['2x1'] -= 1
                self.move_history.append({
                    'row': row, 'col': col, 'player': self.current_player, 
                    'type': '2x1-v', 'piece_id': piece_id
                })
                self.update_display()
                return True
        
        return False
    
    def get_push_direction(self, from_row, from_col, to_row, to_col):
        delta_row = to_row - from_row
        delta_col = to_col - from_col
        
        if abs(delta_row) + abs(delta_col) != 1:
            return None
        
        if delta_row == -1:
            return 'up'
        elif delta_row == 1:
            return 'down'
        elif delta_col == -1:
            return 'left'
        elif delta_col == 1:
            return 'right'
        
        return None
    
    def can_push_single_block(self, row, col, direction):
        target_row, target_col = row, col
        
        if direction == 'up':
            target_row -= 1
        elif direction == 'down':
            target_row += 1
        elif direction == 'left':
            target_col -= 1
        elif direction == 'right':
            target_col += 1
        
        # Check if target is out of bounds (allowed for push)
        if target_row < 0 or target_row >= 4 or target_col < 0 or target_col >= 4:
            return True
        
        # Check if target cell is empty or has an opponent's block
        target_cell = self.game_board[target_row][target_col]
        return target_cell is None or target_cell['player'] != self.current_player
    
    def can_push_horizontal_block(self, row, col, direction):
        other_row, other_col = row, col + 1
        
        # Calculate new positions
        new_row1, new_col1 = row, col
        new_row2, new_col2 = other_row, other_col
        
        if direction == 'up':
            new_row1 -= 1
            new_row2 -= 1
        elif direction == 'down':
            new_row1 += 1
            new_row2 += 1
        elif direction == 'left':
            new_col1 -= 1
            new_col2 -= 1
        elif direction == 'right':
            new_col1 += 1
            new_col2 += 1
        
        # Check if positions are valid (both on board or both off board)
        cell1_on_board = 0 <= new_row1 < 4 and 0 <= new_col1 < 4
        cell2_on_board = 0 <= new_row2 < 4 and 0 <= new_col2 < 4
        
        # Can't have one cell on board and one off (halfway off)
        if cell1_on_board != cell2_on_board:
            return False
        
        # If both cells are on board, check if target positions are available
        if cell1_on_board and cell2_on_board:
            target1_empty = (self.game_board[new_row1][new_col1] is None or 
                           self.game_board[new_row1][new_col1]['player'] != self.current_player)
            target2_empty = (self.game_board[new_row2][new_col2] is None or 
                           self.game_board[new_row2][new_col2]['player'] != self.current_player)
            return target1_empty and target2_empty
        
        # If both cells are off board, it's allowed (complete push off)
        return True
    
    def can_push_vertical_block(self, row, col, direction):
        other_row, other_col = row + 1, col
        
        # Calculate new positions
        new_row1, new_col1 = row, col
        new_row2, new_col2 = other_row, other_col
        
        if direction == 'up':
            new_row1 -= 1
            new_row2 -= 1
        elif direction == 'down':
            new_row1 += 1
            new_row2 += 1
        elif direction == 'left':
            new_col1 -= 1
            new_col2 -= 1
        elif direction == 'right':
            new_col1 += 1
            new_col2 += 1
        
        # Check if positions are valid (both on board or both off board)
        cell1_on_board = 0 <= new_row1 < 4 and 0 <= new_col1 < 4
        cell2_on_board = 0 <= new_row2 < 4 and 0 <= new_col2 < 4
        
        # Can't have one cell on board and one off (halfway off)
        if cell1_on_board != cell2_on_board:
            return False
        
        # If both cells are on board, check if target positions are available
        if cell1_on_board and cell2_on_board:
            target1_empty = (self.game_board[new_row1][new_col1] is None or 
                           self.game_board[new_row1][new_col1]['player'] != self.current_player)
            target2_empty = (self.game_board[new_row2][new_col2] is None or 
                           self.game_board[new_row2][new_col2]['player'] != self.current_player)
            return target1_empty and target2_empty
        
        # If both cells are off board, it's allowed (complete push off)
        return True
    
    def can_push_in_direction(self, row, col, direction):
        block = self.game_board[row][col]
        if not block:
            return False
        
        if block['type'] == '1x1':
            return self.can_push_single_block(row, col, direction)
        elif block['type'] == '2x1-h':
            return self.can_push_horizontal_block(row, col, direction)
        elif block['type'] == '2x1-v':
            return self.can_push_vertical_block(row, col, direction)
        
        return False
    
    def execute_push(self, row, col, direction):
        block = self.game_board[row][col]
        if not block or self.is_pushing:
            return
        
        self.is_pushing = True
        print(f"Executing push: {block['player']} {block['type']} at ({row},{col}) direction: {direction}")
        
        move_id = len(self.move_history) + 1
        blocks_to_return = []
        
        # Find all cells that are part of the block being pushed
        block_cells = []
        if block['type'] == '1x1':
            block_cells.append({'row': row, 'col': col, 'block': block})
        elif block['type'] in ['2x1-h', '2x1-v']:
            # Find both cells of the 2x1 block
            for i in range(4):
                for j in range(4):
                    if (self.game_board[i][j] and 
                        self.game_board[i][j]['piece_id'] == block['piece_id']):
                        block_cells.append({'row': i, 'col': j, 'block': block})
        
        # Calculate where each cell should move
        moves = []
        for cell_info in block_cells:
            r, c = cell_info['row'], cell_info['col']
            new_row, new_col = r, c
            
            if direction == 'up':
                new_row -= 1
            elif direction == 'down':
                new_row += 1
            elif direction == 'left':
                new_col -= 1
            elif direction == 'right':
                new_col += 1
            
            if new_row < 0 or new_row >= 4 or new_col < 0 or new_col >= 4:
                # Block pushed off the map - return to opponent
                blocks_to_return.append(cell_info['block'])
            else:
                moves.append({
                    'from_row': r, 'from_col': c, 
                    'to_row': new_row, 'to_col': new_col, 
                    'block': cell_info['block']
                })
        
        # Handle chain reactions - find blocks that need to be pushed
        chain_moves = []
        processed_blocks = set()
        
        for move in moves:
            target_cell = self.game_board[move['to_row']][move['to_col']]
            if (target_cell and 
                target_cell['player'] != self.current_player and 
                target_cell['piece_id'] not in processed_blocks):
                processed_blocks.add(target_cell['piece_id'])
                
                # Find all cells of this block
                target_block_cells = []
                for i in range(4):
                    for j in range(4):
                        if (self.game_board[i][j] and 
                            self.game_board[i][j]['piece_id'] == target_cell['piece_id']):
                            target_block_cells.append({'row': i, 'col': j, 'block': self.game_board[i][j]})
                
                # Calculate chain move positions
                for cell_info in target_block_cells:
                    r, c = cell_info['row'], cell_info['col']
                    new_row, new_col = r, c
                    
                    if direction == 'up':
                        new_row -= 1
                    elif direction == 'down':
                        new_row += 1
                    elif direction == 'left':
                        new_col -= 1
                    elif direction == 'right':
                        new_col += 1
                    
                    if new_row < 0 or new_row >= 4 or new_col < 0 or new_col >= 4:
                        blocks_to_return.append(cell_info['block'])
                    else:
                        chain_moves.append({
                            'from_row': r, 'from_col': c, 
                            'to_row': new_row, 'to_col': new_col, 
                            'block': cell_info['block']
                        })
        
        # Execute all moves
        # First clear all source positions
        for move in moves:
            self.game_board[move['from_row']][move['from_col']] = None
        for move in chain_moves:
            self.game_board[move['from_row']][move['from_col']] = None
        
        # Then place all blocks in new positions
        for move in moves:
            self.game_board[move['to_row']][move['to_col']] = move['block']
        for move in chain_moves:
            self.game_board[move['to_row']][move['to_col']] = move['block']
        
        # Return blocks to opponents (blocks pushed off go to the other player)
        for block in blocks_to_return:
            piece_type = block['type'].replace('-h', '').replace('-v', '')
            opponent = 'green' if block['player'] == 'red' else 'red'
            self.player_pieces[opponent][piece_type] += 1
            print(f"Returning {piece_type} to {opponent} (was {block['player']}'s)")
        
        # Record the move
        self.move_history.append({
            'type': 'push',
            'player': self.current_player,
            'direction': direction,
            'start_row': row,
            'start_col': col,
            'blocks_to_return': blocks_to_return,
            'move_id': move_id
        })
        
        print('Push completed')
        self.update_display()
        self.is_pushing = False
    
    def highlight_push_targets(self, row, col):
        directions = ['up', 'down', 'left', 'right']
        
        for direction in directions:
            if self.can_push_in_direction(row, col, direction):
                target_row, target_col = row, col
                
                if direction == 'up':
                    target_row -= 1
                elif direction == 'down':
                    target_row += 1
                elif direction == 'left':
                    target_col -= 1
                elif direction == 'right':
                    target_col += 1
                
                if 0 <= target_row < 4 and 0 <= target_col < 4:
                    self.cells[target_row][target_col].configure(bg='#fff3e0')
    
    def clear_highlights(self):
        self.update_display()
    
    def update_grid_highlights(self):
        self.clear_highlights()
        
        if not self.selected_piece:
            return
        
        for i in range(4):
            for j in range(4):
                if self.selected_piece == '1x1' and self.game_board[i][j] is None:
                    self.cells[i][j].configure(bg='#fff3e0')
                elif self.selected_piece == '2x1':
                    # Check horizontal placement
                    if (j < 3 and 
                        self.game_board[i][j] is None and 
                        self.game_board[i][j + 1] is None):
                        self.cells[i][j].configure(bg='#fff3e0')
                    # Check vertical placement
                    elif (i < 3 and 
                          self.game_board[i][j] is None and 
                          self.game_board[i + 1][j] is None):
                        self.cells[i][j].configure(bg='#fff3e0')
    
    def update_display(self):
        # Update current player display
        color = '#d32f2f' if self.current_player == 'red' else '#388e3c'
        self.current_player_label.configure(text=f"Current Player: {self.current_player.title()}", 
                                          fg=color)
        
        # Update piece availability
        for piece_type, btn in self.piece_buttons.items():
            available = self.player_pieces[self.current_player][piece_type] > 0
            if available:
                btn.configure(state='normal', bg='white')
            else:
                btn.configure(state='disabled', bg='#f0f0f0')
        
        # Update grid
        for i in range(4):
            for j in range(4):
                cell = self.cells[i][j]
                if self.game_board[i][j]:
                    block = self.game_board[i][j]
                    if block['player'] == 'red':
                        cell.configure(bg='#ffcdd2', text='', state='normal')
                    else:
                        cell.configure(bg='#c8e6c9', text='', state='normal')
                else:
                    cell.configure(bg='white', text='', state='normal')
        
        # Clear piece selection if no pieces available
        if self.selected_piece and self.player_pieces[self.current_player][self.selected_piece] <= 0:
            self.selected_piece = None
            for btn in self.piece_buttons.values():
                btn.configure(bg='white', relief='raised')
    
    def switch_player(self):
        self.current_player = 'green' if self.current_player == 'red' else 'red'
        self.update_display()
        self.selected_piece = None
        self.selected_push_block = None
        for btn in self.piece_buttons.values():
            btn.configure(bg='white', relief='raised')
    
    def undo_move(self):
        if not self.move_history or self.is_pushing:
            return
        
        last_move = self.move_history.pop()
        
        if last_move.get('type') == 'push':
            print('Undoing push move - not fully implemented')
            return
        
        # Handle regular piece placement moves
        piece_id = last_move['piece_id']
        player = last_move['player']
        
        # Remove all cells with this piece ID
        for i in range(4):
            for j in range(4):
                if (self.game_board[i][j] and 
                    self.game_board[i][j]['piece_id'] == piece_id):
                    self.game_board[i][j] = None
        
        # Return piece to player's inventory
        piece_type = last_move['type'].replace('-h', '').replace('-v', '')
        self.player_pieces[player][piece_type] += 1
        
        # Switch back to previous player
        self.current_player = player
        self.update_display()
    
    def reset_game(self):
        self.current_player = 'red'
        self.selected_piece = None
        self.game_board = [[None for _ in range(4)] for _ in range(4)]
        self.move_history = []
        self.selected_push_block = None
        self.is_pushing = False
        
        # Reset piece counts
        self.player_pieces = {
            'red': {'1x1': 2, '2x1': 1},
            'green': {'1x1': 2, '2x1': 1}
        }
        
        for btn in self.piece_buttons.values():
            btn.configure(bg='white', relief='raised')
        
        self.update_display()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = PomecziGame()
    game.run()
