from pygame import Color, Rect
import pygame


def load_image(path):
    return pygame.image.load(path).convert_alpha()


class GUI:
    elements = []

    @staticmethod
    def add_element(element):
        GUI.elements.append(element)

    @staticmethod
    def del_element(name_element):
        for element in GUI.elements:
            if element.name == name_element:
                GUI.elements.remove(element)

    @staticmethod
    def update():
        for element in GUI.elements:
            element.update()

    @staticmethod
    def render(surface):
        for element in GUI.elements:
            element.render(surface)

    @staticmethod
    def apply_event(event):
        for element in GUI.elements:
            element.apply_event(event)

    @staticmethod
    def get_object(name):
        for obj in GUI.elements:
            if type(obj.name) is list:
                for _obj in obj.elements:
                    if _obj.name == name:
                        return _obj
            else:
                if obj.name == name:
                    return obj


class Element:
    def __init__(self, pos=(0, 0), size=(1, 1)):
        self.rect = Rect(pos, size)
        self.name = ''

    def move(self, x, y):
        self.rect.x += x
        self.rect.y += y

    def apply_event(self, event):
        pass

    def update(self):
        pass

    def render(self, surface):
        pass


class Button(Element):
    def __init__(self, text, pos, size, func, name, text_color=(77, 81, 83), but_color=(230, 230, 230),
                 shift_text=(0, 0), size_image=None, **kwargs):
        super().__init__()

        self.text = text
        self.pos = pos
        self.size = size
        self.function = func
        self.name = name

        self.text_color, self.color_but = text_color, but_color

        self.shift_text = shift_text

        self.rect = Rect(pos, size)
        self.rect.center = pos

        self.settings = {'but_color': but_color, 'hovered': None, 'clicked': None, 'size_font': 5}
        for name, value in kwargs.items():
            self.settings[name] = value

        self.font = pygame.font.Font(None, self.settings['size_font'])
        _x = pos[0] + pygame.font.Font(None, self.settings['size_font']).size(text)[0] // 2
        self.font_rect = Rect((pos[0] + shift_text[0], pos[1] + shift_text[1]), size)
        self.font_rect.center = (pos[0] + shift_text[0], pos[1] + shift_text[1])

        self.active = True

    def set(self, **kwargs):
        for name, value in kwargs.items():
            self.settings[name] = value

    def update(self):
        if self.active:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                if self.settings['hovered']:
                    self.color_but = self.settings['hovered']
            else:
                self.color_but = self.settings['but_color']

    def render(self, surface):
        pygame.draw.rect(surface, self.color_but, self.rect)
        self.rendered_text = self.font.render(self.text, 1, self.text_color)
        surface.blit(self.rendered_text, self.font_rect)

    def apply_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                if event.button == 1:
                    self.function()


class ButtonImage(Element):
    def __init__(self, pos, image_states, text='', size_image=None, font_path=None, text_color=(77, 81, 83),
                 text_size=20, name='test', func=lambda: None, shift_text=(0, 0)):
        super().__init__()

        self.normal_image = load_image(image_states['normal'])
        self.hover_image = load_image(image_states['hovered'])
        self.click_image = load_image(image_states['clicked'])

        self.text = text
        self.font = pygame.font.Font(font_path, text_size)
        self.text_color = text_color

        if size_image:
            # self.size_image = size_image
            self.rect.w, self.rect.h = size_image

        self.pos = pos

        self.image = self.normal_image

        self.shift_text = shift_text

        self.name = name
        self.func = func

        self.states = {
            'hovered': False,
            'clicked': False,
            'after_click': False
        }

    def update(self, *args):
        if self.states['clicked']:
            self.states['clicked'] = False
            self.image = self.click_image
            self.states['after_click'] = True
        elif self.states['after_click']:
            if self.states['hovered']:
                self.image = self.click_image
            else:
                self.states['after_click'] = False

        elif self.states['hovered']:
            self.image = self.hover_image

        else:
            self.image = self.normal_image

    def render(self, surface):
        surface.blit(self.image, self.image.get_rect(center=self.pos))
        text = self.font.render(self.text, 4, self.text_color)
        surface.blit(text, text.get_rect(center=(self.pos[0] + self.shift_text[0], self.pos[1] + self.shift_text[1])))

    def apply_event(self, event):
        self.states['hovered'] = self.image.get_rect(center=self.pos).collidepoint(*pygame.mouse.get_pos())

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.states['hovered']:
                    self.states['clicked'] = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.states['hovered']:
                    self.states['after_click'] = False
                    self.func()


class ButtonFlag(ButtonImage):
    def update(self, *args):
        if self.states['clicked']:
            self.image = self.click_image
            self.states['after_click'] = True
        elif self.states['after_click']:
            if self.states['hovered']:
                self.image = self.click_image
            else:
                self.states['after_click'] = False

        elif self.states['hovered']:
            self.image = self.hover_image

        else:
            self.image = self.normal_image

    def apply_event(self, event):
        self.states['hovered'] = self.image.get_rect(center=self.pos).collidepoint(*pygame.mouse.get_pos())

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.states['hovered']:
                    self.states['clicked'] = True
                    self.func()
                    if self.states['clicked']:
                        return self.name


                        # elif event.type == pygame.MOUSEBUTTONUP:
                        #    if event.button == 1:
                        #        if self.states['hovered']:
                        #            self.states['after_click'] = False
                        #            self.func()


class Label(Element):
    def __init__(self, rect, text):
        super().__init__()

        self.rect = pygame.Rect(rect)
        self.text = text
        self.bgcolor = pygame.Color("white")
        self.font_color = (77, 81, 83)
        self.font = pygame.font.Font(None, self.rect.height - 4)
        self.rendered_text = None
        self.rendered_rect = None

    def render(self, surface):
        surface.fill(self.bgcolor, self.rect)
        self.rendered_text = self.font.render(self.text, 1, self.font_color)
        self.rendered_rect = self.rendered_text.get_rect(x=self.rect.x + 2, centery=self.rect.centery)
        surface.blit(self.rendered_text, self.rendered_rect)


class Div:
    def __init__(self, *buttons):
        self.elements = [but for but in buttons]
        self.name = [but.name for but in buttons]

    def update(self):
        for element in self.elements:
            element.update()

    def render(self, surface):
        for element in self.elements:
            element.render(surface)

    def apply_event(self, event):
        for element in self.elements:
            element.apply_event(event)

    def move(self, x, y):
        for element in self.elements:
            element.move(x, y)


class DivButtons(Div):
    def apply_event(self, event):
        for but in self.elements:
            ans = but.apply_event(event)
            if ans:
                for but_ in self.elements:
                    if but_.name != ans:
                        but_.states['clicked'] = False


class TextBox(Label):
    def __init__(self, rect, text, max_len=None, default_text='', name=''):
        super().__init__(rect, text)
        self.active = False
        self.blink = True
        self.blink_timer = 0
        self.caret = 0

        self.flag_first_active = True
        self.default_text = default_text

        self.max_len = max_len

        self.text = self.default_text

        self.name = name

    def apply_event(self, event):
        if event.type == pygame.KEYDOWN and self.active:

            if event.key == pygame.K_BACKSPACE:
                if len(self.text) > 0 and self.caret != 0:
                    self.text = self.text[:self.caret - 1] + self.text[self.caret:]
                    if self.caret > 0:
                        self.caret -= 1

            else:
                if self.font.render(self.text + event.unicode, 1, self.font_color).get_rect().w < self.rect.w:
                    self.text = self.text[:self.caret] + event.unicode + self.text[self.caret:]
                    self.caret += 1
        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:
                self.active = self.rect.collidepoint(event.pos)
                if self.active:
                    if len(self.text) > 0 and self.text != self.default_text:
                        self.caret = (event.pos[0] - self.rect.x) // (self.rendered_rect.width // len(self.text))
                        if self.caret >= len(self.text):
                            self.caret = len(self.text)
                    else:
                        self.caret = 0


    def update(self):
        if self.active and self.flag_first_active:
            self.flag_first_active = False
            self.text = ''
            self.caret = 0

        elif not self.active and not self.flag_first_active and self.text == '':
            self.flag_first_active = True
            self.text = self.default_text
            self.caret = 0

        if pygame.time.get_ticks() - self.blink_timer > 200:
            self.blink = not self.blink
            self.blink_timer = pygame.time.get_ticks()

    def render(self, surface):
        super(TextBox, self).render(surface)
        w = self.rect.x + self.font.render(self.text[:self.caret], 1, self.font_color).get_rect().width

        pygame.draw.line(surface, Color('gray'), (self.rect.x, self.rect.y), (self.rect.x, self.rect.y + self.rect.h),
                         2)
        pygame.draw.line(surface, Color('gray'), (self.rect.x, self.rect.y + self.rect.h),
                         (self.rect.x + self.rect.w, self.rect.y + self.rect.h), 2)
        pygame.draw.line(surface, Color('gray'), (self.rect.x + self.rect.w, self.rect.y),
                         (self.rect.x + self.rect.w, self.rect.y + self.rect.h), 2)
        pygame.draw.line(surface, Color('gray'), (self.rect.x, self.rect.y), (self.rect.x + self.rect.w, self.rect.y),
                         2)

        if self.blink and self.active:
            pygame.draw.line(
                surface, pygame.Color("black"), (w + 2, self.rendered_rect.top + 2),
                (w + 2, self.rendered_rect.bottom - 2))


class TextBlock(Element):
    def __init__(self, rect, text, size, text_color=Color('black'), bg_color=-1, name=''):
        super().__init__()

        self.rect = pygame.Rect(rect)

        self.text = text

        self.text_color = text_color
        self.bg_color = bg_color

        self.font = pygame.font.Font(None, size)

        self.name = name

        self.active_text = True

    def render(self, surface):
        self.change_text()
        if self.bg_color != -1:
            surface.fill(self.bg_color, self.rect)
        if self.active_text:
            if self.text != []:
                height = self.font.size(self.text[0])[1]

                for num, string in enumerate(self.text):
                    self.rendered_text = self.font.render(string, 1, self.text_color)
                    self.rendered_rect = self.rendered_text.get_rect()
                    self.rendered_rect.x, self.rendered_rect.y = self.rect.x + 3, height * (num + 1) + self.rect.y - 12
                    surface.blit(self.rendered_text, self.rendered_rect)

    def change_text(self):
        for num, string in enumerate(self.text):
            c = 0
            flag = False
            _ = self.font.render(string, 1, self.text_color).get_size()[0]
            while _ >= self.rect.w:
                c -= 1
                flag = True
                _string = string.split(', ')[:c]
                string_ = string.split(', ')[c:]

                _ = self.font.render(', '.join(_string), 1, self.text_color).get_size()[0]

            if flag:
                self.text = [', '.join(self.text[:num]), ', '.join(_string), ', '.join(string_),
                             ', '.join(self.text[num + 1:])]
                if self.text[0] == '':
                    self.text = self.text[1:]


class Switch():
    def __init__(self, rect, text, color_switch, color_background, color_background_on, func):  # func=None, name=None
        self.rect = Rect(rect)
        self.text = text
        self.bgcolor = pygame.Color("white")
        self.font_color = (77, 81, 83)
        self.font = pygame.font.Font(None, self.rect.height - 4)
        self.rendered_text = None
        self.rendered_rect = None

        self.rect_background = Rect(rect)
        self.rect_background.w = self.rect.w * 2
        self.function = func
        self.color_switch = color_switch
        self.color_background = color_background
        self.color_background_on = color_background_on
        self.address = None
        self.active = False
        self.on = False
        self.flag_first_active = False

    def set(self, **kwargs):
        for name, value in kwargs.items():
            self.settings[name] = value

    def apply_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.active = self.rect.collidepoint(event.pos)
                if self.active:
                    self.flag_first_active = True
                    self.on = not self.on
                    self.function()

    def update(self):
        if (self.rect.topright[0] == self.rect_background.x + self.rect_background.w and self.on) or (
                        self.rect.topleft[0] == self.rect_background.x and not self.on):
            self.flag_first_active = False
        if self.flag_first_active and self.on:
            self.rect.x += 1
        elif self.flag_first_active and not self.on:
            self.rect.x -= 1

    def render(self, screen):
        pygame.draw.rect(screen, self.color_background, (
            self.rect_background.x, self.rect_background.y, self.rect_background.w, self.rect_background.h))  # фон
        pygame.draw.rect(screen, self.color_switch,
                         (self.rect.x, self.rect.y, self.rect.w, self.rect.h))  # сам ползунок

        pygame.draw.line(screen, Color('gray'), (self.rect_background.x, self.rect_background.y),
                         (self.rect_background.x, self.rect_background.y + self.rect_background.h),
                         1)
        pygame.draw.line(screen, Color('gray'),
                         (self.rect_background.x, self.rect_background.y + self.rect_background.h),
                         (self.rect_background.x + self.rect_background.w,
                          self.rect_background.y + self.rect_background.h), 1)
        pygame.draw.line(screen, Color('gray'),
                         (self.rect_background.x + self.rect_background.w, self.rect_background.y),
                         (self.rect_background.x + self.rect_background.w,
                          self.rect_background.y + self.rect_background.h), 1)
        pygame.draw.line(screen, Color('gray'), (self.rect_background.x, self.rect_background.y),
                         (self.rect_background.x + self.rect_background.w, self.rect_background.y),
                         1)

        self.rendered_text = self.font.render(self.text, 1, self.font_color)
        self.rendered_rect = self.rendered_text.get_rect(y=self.rect_background.y - 25,
                                                         centerx=self.rect_background.x + self.rect_background.w // 2)  # y=495, centerx=self.rect_background.x + self.rect_background.w//2
        screen.blit(self.rendered_text, self.rendered_rect)
