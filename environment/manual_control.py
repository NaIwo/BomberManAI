import pygame

from game.config import GameProperties, MOVE_TO_NUMBER, Move


def manual_control(**kwargs) -> None:
    from game.bomberman_game import BomberManGame

    human_idx: int = 0

    bm = BomberManGame(**kwargs, human_player_idx=human_idx)
    bm.reset()

    clock = pygame.time.Clock()
    quit_game: int = 0
    cur_agent: int = human_idx

    while not bm.is_end_game():
        clock.tick(GameProperties.FPS.value)
        actions = [MOVE_TO_NUMBER[Move.NOT_MOVING] for _ in range(len(bm.players))]

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit_game = 1
                    break
                if event.key == pygame.K_BACKSPACE:
                    bm.reset()
                if event.key == pygame.K_c:
                    cur_agent += 1
                    if cur_agent == len(bm.players):
                        cur_agent = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            actions[cur_agent] = MOVE_TO_NUMBER[Move.UP]
        if keys[pygame.K_s]:
            actions[cur_agent] = MOVE_TO_NUMBER[Move.DOWN]
        if keys[pygame.K_a]:
            actions[cur_agent] = MOVE_TO_NUMBER[Move.LEFT]
        if keys[pygame.K_d]:
            actions[cur_agent] = MOVE_TO_NUMBER[Move.RIGHT]

        if quit_game:
            break
        for agent_idx, action in enumerate(actions):
            bm.perform_action_and_get_reward(agent_idx, action)
        bm.update()
        bm.render()

    bm.close()
