import pygame


def run_editor_shell(screen, clock):
    running = True
    font = pygame.font.SysFont("arial", 26, bold=True)
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                running = False
        screen.fill((28, 33, 42))
        screen.blit(font.render("Editor Hub (ESC to return)", True, (240, 240, 240)), (40, 40))
        pygame.display.flip()
        clock.tick(60)
    return "menu"
