import pygame
from .paddle import Paddle
from .ball import Ball

# Game Engine

WHITE = (255, 255, 255)

class GameEngine:
    def __init__(self, width, height):
        self.WINNING_SCORE = 5
        self.width = width
        self.height = height
        self.paddle_width = 10
        self.paddle_height = 100

        self.player = Paddle(10, height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ai = Paddle(width - 20, height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ball = Ball(width // 2, height // 2, 7, 7, width, height)

        self.player_score = 0
        self.ai_score = 0
        self.font = pygame.font.SysFont("Arial", 30)

        # ADDED: Sound Loading
        try:
            # Assuming sound files are in a 'sound' directory
            self.PADDLE_SOUND = pygame.mixer.Sound('sound/paddle_hit.wav') 
            self.WALL_SOUND = pygame.mixer.Sound('sound/wall_bounce.wav')
            self.SCORE_SOUND = pygame.mixer.Sound('sound/score.wav')
        except pygame.error as e:
            print(f"Warning: Could not load sound files. Make sure they are in 'sound/' directory. Error: {e}")
            self.PADDLE_SOUND = None
            self.WALL_SOUND = None
            self.SCORE_SOUND = None

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.player.move(-10, self.height)
        if keys[pygame.K_s]:
            self.player.move(10, self.height)

    def update(self):
        # MODIFIED: Get event from ball movement
        wall_hit = self.ball.move()
        # MODIFIED: Get event from ball-paddle collision
        paddle_hit = self.ball.check_collision(self.player, self.ai)
        
        # ADDED: Play wall sound
        if wall_hit == "wall_hit" and self.WALL_SOUND:
            self.WALL_SOUND.play()
            
        # ADDED: Play paddle sound
        if paddle_hit == "paddle_hit" and self.PADDLE_SOUND:
            self.PADDLE_SOUND.play()

        # Scoring logic
        if self.ball.x <= 0:
            self.ai_score += 1
            if self.SCORE_SOUND: self.SCORE_SOUND.play() # <-- ADDED: Play score sound
            self.ball.reset()
        elif self.ball.x >= self.width:
            self.player_score += 1
            if self.SCORE_SOUND: self.SCORE_SOUND.play() # <-- ADDED: Play score sound
            self.ball.reset()

        # AI follows ball
        self.ai.auto_track(self.ball, self.height)

    def is_game_over(self):
        """Check if the game is over and return winner info"""
        if self.player_score >= self.WINNING_SCORE:
            return True, "Player Wins!"
        elif self.ai_score >= self.WINNING_SCORE:
            return True, "AI Wins!"
        return False, None



    def render(self, screen):
        # Draw paddles and ball
        pygame.draw.rect(screen, WHITE, self.player.rect())
        pygame.draw.rect(screen, WHITE, self.ai.rect())
        pygame.draw.ellipse(screen, WHITE, self.ball.rect())
        pygame.draw.aaline(screen, WHITE, (self.width//2, 0), (self.width//2, self.height))

        # Draw score
        player_text = self.font.render(str(self.player_score), True, WHITE)
        ai_text = self.font.render(str(self.ai_score), True, WHITE)
        screen.blit(player_text, (self.width//4, 20))
        screen.blit(ai_text, (self.width * 3//4, 20))

    def show_winner(self, screen, text):
        font_big = pygame.font.SysFont("Arial", 50)
        winner_text = font_big.render(text, True, (255, 255, 255))
        score_text = self.font.render(
            f"Player: {self.player_score}   AI: {self.ai_score}", True, (255, 255, 255)
        )

        screen.fill((0, 0, 0)) # Fills the screen with black
        screen.blit(winner_text, (self.width // 2 - winner_text.get_width() // 2, self.height // 2 - 50))
        screen.blit(score_text, (self.width // 2 - score_text.get_width() // 2, self.height // 2 + 20))
        # main.py handles the pygame.display.flip()

    def show_replay_menu(self, screen):
        font = pygame.font.SysFont("Arial", 40)
        screen.fill((0, 0, 0))
        text = font.render("Replay? Press 3, 5, 7 or ESC to exit", True, (255, 255, 255))
        rect = text.get_rect(center=(self.width // 2, self.height // 2))
        screen.blit(text, rect)
        pygame.display.flip()

    def handle_replay_input(self):
        """Handle replay menu input and return new winning score or None to exit"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_3:
                    return 3
                elif event.key == pygame.K_5:
                    return 5
                elif event.key == pygame.K_7:
                    return 7
                elif event.key == pygame.K_ESCAPE:
                    return "quit"
        return None

    def reset_game(self):
        self.player_score = 0
        self.ai_score = 0
        self.ball.reset()
        self.player.reset_position()
        self.ai.reset_position()
