import pygame
import random

# Start pygame
pygame.init()

# Game settings
GRID_SIZE = 20  # how many squares in the grid
SQUARE_SIZE = 30  # size of each square in pixels
WIDTH = GRID_SIZE * SQUARE_SIZE
HEIGHT = GRID_SIZE * SQUARE_SIZE
GAME_SPEED = 10  # frames per second

# Colors (R,G,B)
BLACK = (0, 0, 0)      # background
DARK_GRAY = (30, 30, 30)   # darker squares for grid pattern
LIGHT_GRAY = (50, 50, 50)  # lighter squares for grid pattern
GREEN = (0, 255, 0)    # snake body
WHITE = (255, 255, 255)  # snake head
RED = (255, 0, 0)      # fruit

# Self-avoidance factor - higher values make the snake avoid itself more strongly
AVOIDANCE_FACTOR = 0.5

class SnakeGame:
    def __init__(self):
        # Set up the game window
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("AI snake with slight self-avoidance")
        self.clock = pygame.time.Clock()
        
        # Start a new game
        self.start_new_game()
    
    def start_new_game(self):
        # Snake starts with one segment
        self.snake = [(5, 5)]  # (x, y) coordinates
        
        # Place fruit somewhere random
        self.fruit = (15, 15)
        
        self.score = 0
        self.game_over = False
        
        # Find the path to the fruit
        self.path = self.find_path()
    
    def place_new_fruit(self):
        # Put fruit in random spot (not on the snake)
        while True:
            new_fruit = (random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1))
            if new_fruit not in self.snake:
                self.fruit = new_fruit
                break
        
        # Find new path to the fruit
        self.path = self.find_path()
    
    def find_path(self):
        "Find path to fruit with diagonal pattern and slight self-avoidance"
        # Starting point (snake head) and goal (fruit)
        start = self.snake[0]
        goal = self.fruit
        
        # If we're already on the same row or column, use straight line
        if start[0] == goal[0] or start[1] == goal[1]:
            return self.find_direct_path(start, goal)
        else:
            return self.find_diagonal_pattern_path(start, goal)
    
    def find_direct_path(self, start, goal):
        "Create a direct path with slight self-avoidance"
        # A* algorithm for finding the best path
        open_set = [(self.manhattan_distance(start, goal), start)]
        came_from = {start: None}
        g_score = {start: 0}
        
        while open_set:
            # Find the spot with the lowest score
            current_idx = 0
            for i in range(len(open_set)):
                if open_set[i][0] < open_set[current_idx][0]:
                    current_idx = i
            
            current = open_set.pop(current_idx)[1]
            
            # If we found the goal, reconstruct path
            if current == goal:
                path = []
                while current != start:
                    path.append(current)
                    current = came_from[current]
                return path
            
            # Check all 4 directions
            for move in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                new_x = current[0] + move[0]
                new_y = current[1] + move[1]
                neighbor = (new_x, new_y)
                
                # Skip if outside grid
                if new_x < 0 or new_x >= GRID_SIZE or new_y < 0 or new_y >= GRID_SIZE:
                    continue
                
                # Calculate base cost
                new_g = g_score[current] + 1
                
                # Add penalty if near snake body (not head)
                for segment in self.snake[1:]:
                    # Calculate distance to this segment
                    distance = self.manhattan_distance(neighbor, segment)
                    if distance <= 1:  # If adjacent to snake body
                        new_g += AVOIDANCE_FACTOR
                
                if neighbor not in g_score or new_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = new_g
                    f_score = new_g + self.manhattan_distance(neighbor, goal)
                    open_set.append((f_score, neighbor))
        
        # If A* fails, fall back to direct path
        return self.create_simple_path(start, goal)
    
    def find_diagonal_pattern_path(self, start, goal):
        "Find diagonal pattern path with slight self-avoidance"
        # A* algorithm with weight for self-avoidance
        open_set = [(self.manhattan_distance(start, goal), start)]
        came_from = {start: None}
        g_score = {start: 0}
        
        while open_set:
            # Find the spot with the lowest score
            current_idx = 0
            for i in range(len(open_set)):
                if open_set[i][0] < open_set[current_idx][0]:
                    current_idx = i
            
            current = open_set.pop(current_idx)[1]
            
            # If we found the goal, reconstruct path
            if current == goal:
                path = []
                while current != start:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path
            
            # Preferred directions for diagonal pattern
            x, y = current
            gx, gy = goal
            
            # Create list of preferred moves based on diagonal pattern
            preferred_moves = []
            
            if x < gx and y < gy:  # Goal is down-right
                if (x + y) % 2 == 0:
                    preferred_moves = [(1, 0), (0, 1), (-1, 0), (0, -1)]
                else:
                    preferred_moves = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            elif x < gx and y > gy:  # Goal is up-right
                if (x + y) % 2 == 0:
                    preferred_moves = [(1, 0), (0, -1), (-1, 0), (0, 1)]
                else:
                    preferred_moves = [(0, -1), (1, 0), (0, 1), (-1, 0)]
            elif x > gx and y < gy:  # Goal is down-left
                if (x + y) % 2 == 0:
                    preferred_moves = [(-1, 0), (0, 1), (1, 0), (0, -1)]
                else:
                    preferred_moves = [(0, 1), (-1, 0), (0, -1), (1, 0)]
            elif x > gx and y > gy:  # Goal is up-left
                if (x + y) % 2 == 0:
                    preferred_moves = [(-1, 0), (0, -1), (1, 0), (0, 1)]
                else:
                    preferred_moves = [(0, -1), (-1, 0), (0, 1), (1, 0)]
            else:  # Straight direction
                if x < gx:
                    preferred_moves = [(1, 0), (0, 1), (0, -1), (-1, 0)]
                elif x > gx:
                    preferred_moves = [(-1, 0), (0, 1), (0, -1), (1, 0)]
                elif y < gy:
                    preferred_moves = [(0, 1), (1, 0), (-1, 0), (0, -1)]
                else:
                    preferred_moves = [(0, -1), (1, 0), (-1, 0), (0, 1)]
            
            # Check neighbors in order of preference
            for dx, dy in preferred_moves:
                new_x = x + dx
                new_y = y + dy
                neighbor = (new_x, new_y)
                
                # Skip if outside grid
                if new_x < 0 or new_x >= GRID_SIZE or new_y < 0 or new_y >= GRID_SIZE:
                    continue
                
                # Calculate base cost
                new_g = g_score[current] + 1
                
                # Add penalty if near snake body (not head)
                for segment in self.snake[1:]:
                    distance = self.manhattan_distance(neighbor, segment)
                    if distance <= 1:  # If adjacent to snake body
                        new_g += AVOIDANCE_FACTOR
                
                if neighbor not in g_score or new_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = new_g
                    f_score = new_g + self.manhattan_distance(neighbor, goal)
                    open_set.append((f_score, neighbor))
        
        # If A* fails, fall back to simple zigzag path
        return self.create_simple_path(start, goal)
    
    def create_simple_path(self, start, goal):
        "Create a simple path ignoring obstacles"
        path = []
        x, y = start
        gx, gy = goal
        
        # Move horizontally first
        while x != gx:
            x = x + 1 if x < gx else x - 1
            path.append((x, y))
            
        # Then move vertically
        while y != gy:
            y = y + 1 if y < gy else y - 1
            path.append((x, y))
            
        return path
    
    def manhattan_distance(self, pos1, pos2):
        "Calculate Manhattan distance between two points"
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def update_game(self):
        # Don't do anything if game is over
        if self.game_over:
            return
        
        # If we have a path, move along it
        if self.path:
            next_spot = self.path.pop(0)
            
            # Check if we hit the wall
            x, y = next_spot
            if x < 0 or x >= GRID_SIZE or y < 0 or y >= GRID_SIZE:
                self.game_over = True
                return
            
            # Check if we hit ourselves
            if next_spot in self.snake:
                self.game_over = True
                return
            
            # Move snake by adding new head
            self.snake.insert(0, next_spot)
            
            # Check if we ate the fruit
            if next_spot == self.fruit:
                self.score += 1
                self.place_new_fruit()
            else:
                # Remove tail if we didn't eat
                self.snake.pop()
        else:
            # Try to find a path if we don't have one
            self.path = self.find_path()
            if not self.path:
                self.game_over = True
    
    def draw_game(self):
        # Fill background with grid pattern
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                # Create checkerboard pattern
                if (x + y) % 2 == 0:
                    color = DARK_GRAY
                else:
                    color = LIGHT_GRAY
                pygame.draw.rect(self.screen, color, 
                               (x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        
        # Draw snake
        for i, (x, y) in enumerate(self.snake):
            if i == 0:  # Head
                color = WHITE
            else:  # Body
                color = GREEN
            
            pygame.draw.rect(self.screen, color, 
                           (x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        
        # Draw fruit
        pygame.draw.rect(self.screen, RED, 
                       (self.fruit[0] * SQUARE_SIZE, self.fruit[1] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        
        # Draw score
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Show game over message
        if self.game_over:
            font = pygame.font.SysFont(None, 72)
            game_over_text = font.render('GAME OVER!', True, WHITE)
            text_rect = game_over_text.get_rect(center=(WIDTH/2, HEIGHT/2))
            self.screen.blit(game_over_text, text_rect)
            
            font = pygame.font.SysFont(None, 36)
            restart_text = font.render('Press R to restart', True, WHITE)
            restart_rect = restart_text.get_rect(center=(WIDTH/2, HEIGHT/2 + 50))
            self.screen.blit(restart_text, restart_rect)
        
        # Update the display
        pygame.display.flip()
    
    def run_game(self):
        # Main game loop
        running = True
        while running:
            # Check for quit or restart
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    # Restart game if R is pressed
                    if event.key == pygame.K_r and self.game_over:
                        self.start_new_game()
            
            # Update game state
            self.update_game()
            
            # Draw everything
            self.draw_game()
            
            # Control game speed
            self.clock.tick(GAME_SPEED)
        
        # Quit when done
        pygame.quit()

game = SnakeGame()
game.run_game()
