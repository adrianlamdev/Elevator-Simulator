import pygame, os, json, time
from states.state import state_format
from states.pause_menu import paused

with open("button_coords.json", "r") as input:
    data = json.load(input)
input.close()


class main_game(state_format):
    def __init__(self, game):
        super().__init__(game)
        service = True

        self.surface = pygame.Surface((672, 378))
        self.surface.fill((40, 42, 54))
        self.music = pygame.mixer.Sound(
            os.path.join(self.game.asset_dir, "sounds", "elevator_main.wav")
        )
        if self.game.sound_enabled:
            self.music.play(1, 0, 500)
        self.elevator_group = []

        self.elevator1 = elevator(self.game, True, 10, 200)
        self.elevator2 = elevator(self.game, False, 10, 300)
        self.elevator_group.append(self.elevator1)
        self.elevator_group.append(self.elevator2)
        self.elevator1.button_init(300, 340)
        self.elevator2.button_init(364, 340)

    def update(self, actions):
        if actions["Pause"]:
            next_state = paused(self.game)
            next_state.enter_state()
        self.elevator1.update(actions)
        self.elevator2.update(actions)
        """self.game.reset_keys()"""

        # elevator velocity changes go here

    def render(self, surface):
        surface.blit(self.surface, (0, 0))
        self.elevator1.render(self.surface)
        self.elevator2.render(self.surface)


class button(pygame.sprite.Sprite):
    def __init__(self, elevator, game, x, y, image, val):
        super().__init__()
        self.game = game
        self.x, self.y = x, y
        self.val = val
        self.dir = os.path.join("assets", "graphics", "Keys")
        self.butt = image
        self.image = pygame.image.load(os.path.join(self.dir, self.butt))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.pushed = False
        self.sound = pygame.mixer.Sound(
            os.path.join(self.game.asset_dir, "sounds", "button_sound.wav")
        )

    def update(self, pushed):
        if pushed:
            self.image = pygame.image.load(
                os.path.join(self.dir, self.val + ".5-Key.png")
            )
        else:
            self.image = pygame.image.load(os.path.join(self.dir, self.butt))

    def render(self, surface):
        pass


class elevator:
    def __init__(self, game, service, x, y):
        self.game = game
        self.x, self.y = x, y
        self.images = []
        self.service = service
        self.direction = {"Up": False, "Down": False}
        self.door_state = {"Open": False}
        self.user_choice = {"Open": True}
        self.curr_floor = {
            "1": True,
            "2": False,
            "3": False,
            "4": False,
            "5": False,
            "6": False,
        }
        self.button_group = []
        self.floor_queue = []
        self.curr_frame = 0
        for image_name in data["frames"]["Elevator Pictures"]:
            img_load = pygame.image.load(
                os.path.join(self.game.asset_dir, "graphics", "elevator", image_name)
            )
            img_load = pygame.transform.scale(
                img_load, (img_load.get_width() * 2, img_load.get_height() * 2)
            )
            self.images.append(img_load)
        self.image = self.images[self.curr_frame]
        self.surface = pygame.Surface((img_load.get_width(), img_load.get_height()))
        self.rect = self.surface.get_rect(topleft=(x, y))

    def button_collision_detection(self, actions):
        for self.button in self.button_group:
            if self.button.rect.collidepoint(self.game.mouse_pos) and actions["Click"]:
                self.button.pushed = True
                self.button.update(self.button.pushed)
                self.button.sound.play()
            if not actions["Click"]:
                self.button.pushed = False
                self.button.update(self.button.pushed)

    def update(self, actions):
        if actions["Click"]:
            self.button_collision_detection(actions)
        elif actions["Click"] == False:
            self.button_collision_detection(actions)
        if self.user_choice["Open"] == True:
            if self.door_state["Open"] == False:
                if self.curr_frame < 4:
                    self.image = self.images[self.curr_frame]
                    self.curr_frame += 1

                else:
                    self.curr_frame = 4
                    self.door_state["Open"] = True
        else:
            if self.curr_frame != 0:
                if self.curr_frame > 0:
                    self.image = self.images[self.curr_frame]
                    self.curr_frame -= 1
                else:
                    self.curr_frame = 0
                    self.door_state["Open"] = False
        print(self.user_choice)
        print(self.door_state)

        """if self.direction["Up"] is True:
            self.direction["Down"] = False
        elif self.direction["Down"] is True:
            self.direction["Up"] = False
        if self.door_state["Open"] is True:
            self.door_state["Closed"] = False
        elif self.door_state["Open"] is False:
            self.door_state["Closed"] = True
        if self.door_state["Open"] is True:
            for keys in self.direction.keys():
                self.direction[keys] = False"""

    def button_init(self, x=300, y=340):
        for elem in data["frames"]["elevator buttons"]:
            if not self.service:
                print(self.service)
                if elem == "S-Key.png":
                    break
            val = elem[0]
            self.buttons = button(self, self.game, x, y, elem, val)
            self.buttons.w, self.buttons.h = (
                data["frames"]["elevator buttons"][elem]["size"]["w"],
                data["frames"]["elevator buttons"][elem]["size"]["h"],
            )
            y -= 30
            self.button_group.append(self.buttons)
        self.button_group = pygame.sprite.Group(self.button_group)

    def render(self, surface):
        self.button_group.draw(surface)
        surface.blit(self.image, self.rect)
