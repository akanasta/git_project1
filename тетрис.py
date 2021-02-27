from проект.board import Board
import pygame
import sys, os
from random import randrange, choice


all_sprites = pygame.sprite.Group()  # группа для всех спрайтов
stand_shapes = pygame.sprite.Group()  # группа для спрайтов движущейся фигуры
move_shape = pygame.sprite.Group()  # группа для спрайтов всех остановившихся фигур
stars = pygame.sprite.Group()

clock = pygame.time.Clock()

center = [0, 0]  # координаты условного центра движущейся фигуры.
# Относительно center чертим фигуры вначале, а после вращаем их
board = Board(10, 15)  # создаем поле
# занесём в список shapes координаты относительно значения center[0], для начальной отрисовки фигур
shapes = [[(-2, 0), (-1, 0), (0, 0), (1, 0)], [(-2, -1), (-1, -1), (0, -1), (0, 0)],
          [(-1, -1), (0, -1), (-1, 0), (1, -1)], [(-1, -1), (0, -1), (0, 0), (1, 0)],
          [(-1, -1), (0, -1), (-1, 0), (0, 0)], [(-1, -0), (0, -1), (0, 0), (1, -1)],
          [(-1, 0), (0, -1), (0, 0), (1, 0)]]
screen_rect = (0, 0, 400, 685)

pygame.init()
pygame.display.set_caption("Тетрис")
screen = pygame.display.set_mode([400, 685])


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Particle(pygame.sprite.Sprite):  # ылетающие звёздочки
    # сгенерируем частицы разного размера
    fire = [load_image("star.png")]
    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites)
        self.add(stars)
        self.image = choice(self.fire)
        self.rect = self.image.get_rect()

        # у каждой частицы своя скорость — это вектор
        self.velocity = [dx, dy]
        # и свои координаты
        self.rect.x, self.rect.y = pos

        # гравитация будет одинаковой (значение константы)
        self.gravity = 5

    def update(self):
        # применяем гравитационный эффект:
        # движение с ускорением под действием гравитации
        self.velocity[1] += self.gravity
        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # убиваем, если частица ушла за экран
        if not self.rect.colliderect(screen_rect):
            self.kill()


def create_particles(position):
    # количество создаваемых частиц
    particle_count = 20
    # возможные скорости
    numbers = range(-20, 20)
    for _ in range(particle_count):
        Particle(position, choice(numbers), choice(numbers))


def make_shape():  # создаем фигуру
    a = randrange(0, 7)  # выбираем формат вид фигуры(отличаютя отклонениями от условного центра)
    while True:  # рандомно выбираем начальное положенеие падения
        a_cell = randrange(1, 11)
        # проверяем не выходит ли фигура за границы поля
        if shapes[a][0][0] + a_cell >= 1 and shapes[a][3][0] + a_cell <= 10:
            break
    # выбрав начальное положение фигуры, задаем значние center
    center[0], center[1] = (a_cell - 1) * 40, 45
    for i in range(4):  # одна фигура состоит из 4 спрайтов
        pos_x = shapes[a][i][0] * 40 + (a_cell - 1) * 40
        pos_y = shapes[a][i][1] * 40 + 60
        Shapes(pos_x, pos_y)


class Shapes(pygame.sprite.Sprite):  # в классе Shapes создается спрайт, занимающий одну клетку доски
    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites)
        self.add(move_shape)  # при срздании, спрайт оказывается в группе движущейся фигуры

        self.image = load_image("пицца.jpg")
        self.rect = self.image.get_rect()
        self.rect.left = pos_x
        self.rect.top = pos_y

    def update(self, move, speed=5):
        if move:
            self.rect.top += speed  # каждый спрайт фигуры опускается вниз со скоростью speed


def check_borders(x):  # функция для прверки столкновения фигуры с боковыми границами поля при сдвиги впрво или влево
    for s in move_shape:
        if 0 > s.rect.left + x or s.rect.left + 40 + x > 400:
            return False
    center[0] += x
    return True


def del_row():  # функция проверяет есть ли полностью заполненные ряды
    y = []
    for i in range(15):
        row = board.board[i]
        if len(set(row)) == 1 and 1 in row:
            y.append(i * 40 + 85)
    return y


def correct(s):  # функция коррректирует положение переданнго спрайта, после остановки его фигуры, по сетке поля
    x, y = s.rect.left, s.rect.top
    s.rect.left = x // 40 * 40
    s.rect.top = y // 40 * 40 + 5


def turn_around():  # функция высчитывает новые координаты для фигуры, поле её поворота
    yes = True
    for s in move_shape:
        x = s.rect.top - center[1]
        y = s.rect.left - center[0]
        if center[0] - x < 0 or center[0] - x > 360 or center[1] - y < 0 or center[1] - y > 685:
            yes = False
    if yes:
        for s in move_shape:
            x = s.rect.top - center[1]
            y = s.rect.left - center[0]
            s.rect.left = center[0] - x
            s.rect.top = center[1] - y


def terminate():
    pygame.quit()
    sys.exit()


def start_screen(screen):
    text = [
        "Правила:", "", "используйте клавиши со стрелками для", "передвижения фигурки вправо/влево,",
                        "чтобы придать фигурке ускорение", "стрелка вниз,", "клавиша Ctrl для поворота фигуры"
    ]
    start_screen = pygame.Surface([400, 685])
    start_screen.fill((210, 70, 70))
    start_screen.blit(load_image("доставщик2.png"), (0, 400))
    font = pygame.font.Font(None, 25)
    text_coord = 70
    for line in text:
        string_rendered = font.render(line, 1, pygame.Color(255, 184, 65))
        intro_rect = string_rendered.get_rect()
        text_coord += 5
        intro_rect.top = text_coord
        intro_rect.x = 30
        text_coord += intro_rect.height
        start_screen.blit(string_rendered, intro_rect)
    start_string = pygame.font.Font(None, 50).render("Чтобы НАЧАТЬ", 1, pygame.Color(255, 184, 65))
    start_screen.blit(start_string, (20, 275))
    start_string = pygame.font.Font(None, 50).render("нажмите ПРОБЕЛ", 1, pygame.Color(255, 184, 65))
    start_screen.blit(start_string, (60, 325))
    screen.blit(start_screen, (0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                return
        pygame.display.flip()
        clock.tick(50)


def pause_screen(screen, score):
    pause_screen = pygame.Surface([400, 400])
    pause_screen.fill((210, 70, 70))
    pause_string = pygame.font.Font(None, 50).render("ПАУЗА", 1, pygame.Color(255, 184, 65))
    pause_screen.blit(pause_string, (130, 130))
    score_string = pygame.font.Font(None, 50).render(f"Текущий счёт: {score}", 1, pygame.Color(255, 184, 65))
    pause_screen.blit(score_string, (20, 180))
    screen.blit(pause_screen, (0, 140))

    waiting = True
    while waiting:
        clock.tick(50)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False
        pygame.display.flip()
        clock.tick(50)


def end_screen(screen, score, record):
    text = [
        "Ваш счёт:", "", "Рекордный счёт заказа:", "", "хотите сделаать ещё один заказ?", "нажмите ПРОБЕЛ"
    ]
    end_screen = pygame.Surface([400, 685])
    end_screen.fill((210, 70, 70))
    end_screen.blit(load_image("упала.png"), (25, 350))
    font = pygame.font.Font(None, 30)
    text_coord = 100
    for line in text:
        string_rendered = font.render(line, 1, pygame.Color(255, 184, 65))
        intro_rect = string_rendered.get_rect()
        text_coord += 5
        intro_rect.top = text_coord
        intro_rect.x = 30
        text_coord += intro_rect.height
        end_screen.blit(string_rendered, intro_rect)
    record_string = pygame.font.Font(None, 50).render(str(record), 1, pygame.Color(255, 184, 65))
    end_screen.blit(record_string, (300, 150))
    score_string = pygame.font.Font(None, 50).render(str(score), 1, pygame.Color(255, 184, 65))
    end_screen.blit(score_string, (170, 100))
    screen.blit(end_screen, (0, 0))

    waiting = True
    while waiting:
        clock.tick(50)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False
        pygame.display.flip()
        clock.tick(50)


def main():

    start_screen(screen)

    running = True
    move = False  # показывает есть ли на поле движущиеся фигуры
    speed = 10  # показатель скорости движения фигур
    start = True  # начало нвого цикла(созание новой фигуры т т.д.)
    end = False  # конец игры
    score = 0
    record = 0
    while running:
        sdv = 0  # обозначает направление сдвига фигуры(вправо\влево)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                pause_screen(screen, score)
            if event.type == pygame.KEYDOWN and move:
                if event.key == pygame.K_LEFT:
                    sdv = - 40
                if event.key == pygame.K_RIGHT:
                    sdv = 40
                # при нажатии на стрлочку-вниз скорость падения фигуры увеличивается
                if event.key == pygame.K_DOWN:
                    speed += 70
                # при нажатии на пробел, падающая фигура поворачивается на 90 градусов по часовой стрелке
                if event.key == pygame.K_LCTRL:
                    center[1] = max(s.rect.top for s in move_shape)
                    turn_around()
        stars.update()
        all_sprites.draw(screen)
        collision = check_borders(sdv)  # проверяем возможен ли сдвиг фигуры по нажатой клавише-стрелке
        screen.fill((41, 7, 15))
        stars.draw(screen)
        score_string = pygame.font.Font(None, 50).render(str(score), 1, pygame.Color(255, 184, 65))
        screen.blit(score_string, (310, 12))
        if start:
            make_shape()
            move = True
            start = False
        board.render(screen)  # отрисовываем поле
        all_sprites.draw(screen)  # отрисовываем все спрайты
        move_shape.update(move)
        if move:
            center[1] += speed  # перемещаем центр фигуры при ее движении
            for s in move_shape:
                # проверяем падающую фигуру на столкновение с нижней границей поля или с уже остановившимися фигурами
                # если столкновение произошло, останавливаем падающую фигуру(меняем показатель движения - move)
                if pygame.sprite.spritecollideany(s, stand_shapes) is not None or s.rect.top + 40 >= 685:
                    move = False
                    # возвращаем скорость для следующей фигуры в норму(на случай, если было ускорение фигуры)
                    speed = 10
                # если сдвиг возможен, сдвигаем каждый спрат в падающей фигуре(в группе move_shape) на sdv
                if collision and sdv:
                    s.rect.left += sdv
        if not move:  # когда фигура остановилась:
            for s in move_shape:
                correct(s)  # корректируем ее пложение, чтобы оно совпадало с границами клеток поля
                s.add(stand_shapes)  # все спрайты фигуры переходят из группы спрайтов движущейся фигуры,
                # в группу спрайтов остановившихся фигур
                move_shape.remove(s)
                # в списке класса Board отмечаем клетки, заполненные спрайтами остновившихся фигур
                board.get_stop((s.rect.left, s.rect.top))
                if s.rect.top <= 85:
                    end = True
            y = del_row()  # получаем заполненные ряды
            if y:
                create_particles((200, y[0]))
                for sprite in stand_shapes:
                    if sprite.rect.top == y[0]:  # если спрай входит в заполенный ряд, то он удаляется
                        board.get_stop((sprite.rect.left, sprite.rect.top), False)  # значение в списке на 0
                        sprite.kill()
                    if sprite.rect.top < y[0]:  # если спрайт находится выше заполненного ряда
                        stand_shapes.remove(sprite)
                        board.get_stop((sprite.rect.left, sprite.rect.top), False)
                        sprite.add(move_shape)
                        move = True
                score += 10
                del y[0]
            if not y and not move_shape:
                start = True
                clock.tick(3)
            if end:
                if score > record:
                    record = score
                end_screen(screen, score, record)
                board.board = [[0] * 10 for _ in range(15)]
                for sprite in all_sprites:
                    sprite.kill()
                center[0], center[1] = 0, 0
                score = 0
                end = False
        clock.tick(speed)
        pygame.display.flip()


if __name__ == "__main__":
    main()
