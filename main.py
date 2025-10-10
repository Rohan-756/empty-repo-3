# main.py
import pygame
from game.game_engine import GameEngine

pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

game = GameEngine(WIDTH, HEIGHT)
game_state = "playing"  # "playing", "game_over", "replay_menu"
replay_timer = 0
winner_text = "" # <-- ADDED: To store the winner text across states

running = True
while running:
    # IMPORTANT: screen.fill((0, 0, 0)) must be outside the state checks 
    # if you want a black background for all states.
    screen.fill((0, 0, 0)) 

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # The replay menu input handler is now responsible for processing events 
        # when in the 'replay_menu' state.

    if game_state == "playing":
        game.handle_input()
        game.update()
        game.render(screen)
        
        # Check for game over (Task 2 logic)
        is_over, winner = game.is_game_over()
        if is_over:
            game_state = "game_over"
            winner_text = winner # Store the winner text
            # Draw winner screen instantly on the transition frame
            game.show_winner(screen, winner_text) 
            replay_timer = pygame.time.get_ticks() + 2000  # 2 second delay (Task 2 delay)

    elif game_state == "game_over":
        # Task 2: Continuously draw the winner screen until timer expires
        game.show_winner(screen, winner_text)
        
        if pygame.time.get_ticks() >= replay_timer:
            game_state = "replay_menu"
            # The replay menu will be drawn on the next frame (Task 3 transition)

    elif game_state == "replay_menu":
        # Task 3: Continuously show the menu and handle input
        game.show_replay_menu(screen)
        
        choice = game.handle_replay_input()
        if choice == "quit":
            running = False
        elif choice in [3, 5, 7]:
            game.WINNING_SCORE = choice
            game.reset_game()
            game_state = "playing"

    pygame.display.flip()
    clock.tick(60)

pygame.quit()