"""
台球模拟器

作者：KirkLee123 & ktbtn
创建日期：2026-01-17

版本：V0.1
最近更新：2026-01-17
"""
import copy
import pygame, random, math
import os
import sys


# 资源文件目录访问
def source_path(relative_path):
    # 是否Bundle Resource
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# 修改当前工作目录，使得资源文件可以被正确访问
cd = source_path('')
os.chdir(cd)


class Ball:
    def __init__(self, x=None, y=None, vx=None, vy=None, mass=None, color=None, is_half=False, number=None):
        self.x = x if x is not None else random.randint(100, WIDTH - 100)
        self.y = y if y is not None else random.randint(100, HEIGHT - 100)
        self.vx = vx if vx is not None else 0
        self.vy = vy if vy is not None else 0
        self.mass = mass if mass is not None else 50
        self.color = color if color is not None else (
        random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.radius = math.sqrt(self.mass * 20 / math.pi)
        self.is_half = is_half
        self.is_in_dong = False
        self.number = number
        self.flags = []
        self.flag_interval = 0

    def move(self):
        self.x += self.vx * setting["logical_fps"] / setting["fps"]
        self.y += self.vy * setting["logical_fps"] / setting["fps"]
        # 阻力
        if setting["is_resistance"]:
            self.vx *= (1 - setting["resistance"]) * setting["logical_fps"] / setting["fps"]
            self.vy *= (1 - setting["resistance"]) * setting["logical_fps"] / setting["fps"]
        # 边界反弹
        if setting["bound_bounce"]:
            if self.x - self.radius < 0:
                self.vx = abs(self.vx)
            if self.x + self.radius > WIDTH:
                self.vx = -abs(self.vx)
            if self.y - self.radius < 0:
                self.vy = abs(self.vy)
            if self.y + self.radius > HEIGHT:
                self.vy = -abs(self.vy)

        if abs(math.sqrt(self.vx ** 2 + self.vy ** 2)) < 0.1:
            self.vx = 0
            self.vy = 0

        # 判断球是否进洞
        for d in dong:
            if math.sqrt((self.x - d[0]) ** 2 + (self.y - d[1]) ** 2) < dong_radius:
                self.is_in_dong = True
                break

    def draw(self, x=None, y=None):
        if x: self.x = x
        if y: self.y = y
        if not self.is_half:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        else:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.radius - 2)
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius - 5)
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.radius - 9)
        if self.number:
            text = FONT.render(str(self.number), True, (0, 0, 0))
            text_rect = text.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(text, text_rect)


def handle_collision(ball1, ball2):
    dx = ball2.x - ball1.x
    dy = ball2.y - ball1.y
    dist = math.hypot(dx, dy)
    # 碰撞
    if setting["is_collision"]:
        if dist < ball1.radius + ball2.radius:
            nx, ny = dx / dist, dy / dist  # 碰撞方向
            # 投影到法向
            p1 = ball1.vx * nx + ball1.vy * ny
            p2 = ball2.vx * nx + ball2.vy * ny
            # 速度分量 (考虑质量)
            m1, m2 = ball1.mass, ball2.mass
            new_p1 = (p1 * (m1 - m2) + 2 * m2 * p2) / (m1 + m2)
            new_p2 = (p2 * (m2 - m1) + 2 * m1 * p1) / (m1 + m2)
            ball1.vx += (new_p1 - p1) * nx
            ball1.vy += (new_p1 - p1) * ny
            ball2.vx += (new_p2 - p2) * nx
            ball2.vy += (new_p2 - p2) * ny
            # 分离，避免重叠
            overlap = (ball1.radius + ball2.radius - dist) / 10
            ball1.x -= overlap * nx
            ball1.y -= overlap * ny
            ball2.x += overlap * nx
            ball2.y += overlap * ny


def calculate_predicted_path(ball, vx, vy, steps):
    """计算球的预测轨迹路径"""
    path = []
    temp_ball = copy.deepcopy(ball)
    temp_ball.vx, temp_ball.vy = -vx, -vy

    for _ in range(steps):
        temp_ball.move()
        path.append((int(temp_ball.x), int(temp_ball.y)))

    return path


if __name__ == "__main__":
    pygame.init()
    WIDTH, HEIGHT = 1400, 700
    bar_HEIGHT = 100
    dong_radius = 30
    screen = pygame.display.set_mode((WIDTH, HEIGHT + bar_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.Font("res/STSONG.TTF", 30)
    FONT = pygame.font.Font(None, 24)  # 字体
    setting = {
        "fps": 60,
        "logical_fps": 60,

        "is_resistance": True,
        "resistance": 0.01,

        "bound_bounce" : True,
        "is_collision": True,
    }
    is_quit = False


    balls = []
    in_dong_balls = []


    baix = 1150
    baiy = 350
    ball1x = 350
    ball1y = 350

    ball_pos = []
    ball_pos.append((ball1x, ball1y))

    ball_pos.append((ball1x-30, ball1y-18))
    ball_pos.append((ball1x-30, ball1y+18))

    ball_pos.append((ball1x-60, ball1y-36))
    ball_pos.append((ball1x-60, ball1y))
    ball_pos.append((ball1x-60, ball1y+36))

    ball_pos.append((ball1x-90, ball1y-54))
    ball_pos.append((ball1x-90, ball1y-18))
    ball_pos.append((ball1x-90, ball1y+18))
    ball_pos.append((ball1x-90, ball1y+54))

    ball_pos.append((ball1x-120, ball1y-72))
    ball_pos.append((ball1x-120, ball1y-36))
    ball_pos.append((ball1x-120, ball1y))
    ball_pos.append((ball1x-120, ball1y+36))
    ball_pos.append((ball1x-120, ball1y+72))

    random.shuffle(ball_pos)

    balls.append(Ball(color=(255, 255, 255), x=baix, y=baiy, number=0))  # 白球，必须放在第一个

    x, y = ball_pos.pop()
    balls.append(Ball(color=(210, 233, 3), x=x, y=y, number=1))

    x, y = ball_pos.pop()
    balls.append(Ball(color=(255, 0, 0), x=x, y=y, number=3))
    x, y = ball_pos.pop()
    balls.append(Ball(color=(255, 0, 0), x=x, y=y, number=11, is_half=True))

    x, y = ball_pos.pop()
    balls.append(Ball(color=(0, 255, 0), x=x, y=y, number=14, is_half=True))
    x, y = ball_pos.pop()
    balls.append(Ball(color=(0, 0, 0), x=x, y=y, number=8))
    x, y = ball_pos.pop()
    balls.append(Ball(color=(0, 255, 0), x=x, y=y, number=6))

    x, y = ball_pos.pop()
    balls.append(Ball(color=(210, 233, 3), x=x, y=y, number=2, is_half=True))
    x, y = ball_pos.pop()
    balls.append(Ball(color=(255, 0, 255), x=x, y=y, number=4))
    x, y = ball_pos.pop()
    balls.append(Ball(color=(255, 0, 0), x=x, y=y, number=15, is_half=True))
    x, y = ball_pos.pop()
    balls.append(Ball(color=(232, 125, 3), x=x, y=y, number=13, is_half=True))

    x, y = ball_pos.pop()
    balls.append(Ball(color=(255, 0, 255), x=x, y=y, number=12, is_half=True))
    x, y = ball_pos.pop()
    balls.append(Ball(color=(232, 125, 3), x=x, y=y, number=5))
    x, y = ball_pos.pop()
    balls.append(Ball(color=(0, 0, 255), x=x, y=y, number=10, is_half=True))
    x, y = ball_pos.pop()
    balls.append(Ball(color=(0, 0, 255), x=x, y=y, number=9))
    x, y = ball_pos.pop()
    balls.append(Ball(color=(255, 0, 0), x=x, y=y, number=7))


    dong = [(0, 0), (0, HEIGHT), (WIDTH, 0), (WIDTH, HEIGHT), (WIDTH / 2, 0), (WIDTH / 2, HEIGHT)]

    # 添加全局变量
    dragging_ball = None
    drag_start_pos = None
    drag_current_pos = None

    is_white_ball_in_dong = False
    is_ball_in_hand = False
    in_hand_ball = None

    running = True
    paused = False
    beisu = 1
    tps_interval = 0
    ticks = 0
    fps = clock.get_fps()
    actionable = True
    while running:

        actionable = True
        for i in balls:
            if i.vx != 0 or i.vy != 0:
                actionable = False
                break
        if actionable:
            if is_white_ball_in_dong:
                is_white_ball_in_dong = False
                wb = None
                for b in in_dong_balls:
                    if b.number == 0:
                        wb = b
                        break
                in_dong_balls.remove(wb)
                balls.insert(0, wb)
                balls[0].x = baix
                balls[0].y = baiy
                balls[0].vx = 0
                balls[0].vy = 0
                balls[0].is_in_dong = False
                paused = True


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and paused:
                paused = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and actionable:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # 检查是否点击了白球（假设白球是第一个球）
                white_ball = balls[0]
                distance = math.hypot(mouse_x - white_ball.x, mouse_y - white_ball.y)
                if distance <= white_ball.radius:
                    dragging_ball = white_ball
                    drag_start_pos = (white_ball.x, white_ball.y)
                    drag_current_pos = (mouse_x, mouse_y)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if dragging_ball and actionable:
                    # 计算击球力度和方向
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    dx = drag_start_pos[0] - mouse_x
                    dy = drag_start_pos[1] - mouse_y

                    # 设置白球的速度（击球效果）
                    dis = math.hypot(dx, dy)  # 控制最大力度
                    if dis > 1:  # 只有当力度大于阈值时才击球
                        power = min(dis/10, 50)  # 力度最大值为50
                        dragging_ball.vx = power * dx / dis
                        dragging_ball.vy = power * dy / dis


                dragging_ball = None
                drag_start_pos = None
                drag_current_pos = None
            elif event.type == pygame.MOUSEMOTION:
                if dragging_ball:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    drag_current_pos = (mouse_x, mouse_y)

        if actionable:
            left, middle, right = pygame.mouse.get_pressed()
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if right and not is_ball_in_hand:
                for b in balls:
                    if math.hypot(b.x - mouse_x, b.y - mouse_y) < b.radius:
                        in_hand_ball = b
                        is_ball_in_hand = True
                        break
            if right and is_ball_in_hand:
                in_hand_ball.x = mouse_x
                in_hand_ball.y = mouse_y
            if not right and is_ball_in_hand:
                is_ball_in_hand = False



        if paused:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            white_ball = balls[0]
            white_ball.x = mouse_x
            white_ball.y = mouse_y

        else:
            ticks += 1
            for b in balls:
                b.move()
            for b in balls:
                if b.is_in_dong:
                    in_dong_balls.append(b)
                    balls.remove(b)
                    if b.number == 0:
                        is_white_ball_in_dong = True


            for i in range(len(balls)):
                for j in range(i + 1, len(balls)):
                    handle_collision(balls[i], balls[j])


        # 绘制背景
        screen.fill((52, 125, 0))
        for i in dong:
            pygame.draw.circle(screen, (0, 0, 0), i, dong_radius)
        pygame.draw.line(screen, (104, 104, 104), (0, HEIGHT+(bar_HEIGHT/2)), (WIDTH, HEIGHT+(bar_HEIGHT/2)), bar_HEIGHT)


        # 绘制方向线（如果正在拖拽球）
        if dragging_ball and drag_start_pos and drag_current_pos:
            start_pos = (int(drag_start_pos[0]), int(drag_start_pos[1]))
            end_pos = drag_current_pos

            # 绘制方向线
            pygame.draw.line(screen, (255, 255, 255), start_pos, end_pos, 2)

            # 计算距离和方向
            distance = math.hypot(end_pos[0] - start_pos[0], end_pos[1] - start_pos[1])
            if distance > 1:
                # 显示力度指示器
                max_power = 500  # 最大力度对应的距离
                thickness = int(min(distance / max_power * 10, 10))
                pygame.draw.line(screen, (255, 100, 100), start_pos, end_pos, thickness)

                # 显示距离数值（可选）
                distance_text = FONT.render(f"{min(distance, 500):.1f}", True, (255, 255, 255))
                mid_x = (start_pos[0] + end_pos[0]) / 2
                mid_y = (start_pos[1] + end_pos[1]) / 2
                screen.blit(distance_text, (mid_x, mid_y))

                # 显示预测轨迹线
                white_ball = balls[0]  # （假设白球是第一个球）
                power = min(distance / 10, 50)  # 力度最大值为50
                vx = power * (end_pos[0] - start_pos[0]) / distance
                vy = power * (end_pos[1] - start_pos[1]) / distance
                paths = calculate_predicted_path(white_ball, vx, vy, setting["logical_fps"]*2)
                for p in paths:
                    pygame.draw.circle(screen, (255, 255, 255), (int(p[0]), int(p[1])), 2)


        for b in balls:
            b.draw()
        for i in range(len(in_dong_balls)):
            in_dong_balls[i].draw(i*(bar_HEIGHT/2) + (bar_HEIGHT/4), HEIGHT+(bar_HEIGHT/4))

        if paused:
            pause_text = font.render("自由球：请点击任意位置放下白球", True, (255, 100, 100))
            screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, 20))

        if actionable and not paused:
            action_text = font.render("拖动白球来击球", True, (255, 100, 100))
            screen.blit(action_text, (WIDTH // 2 - action_text.get_width() // 2, 20))

        fps = clock.get_fps()
        tps_interval += 1
        if tps_interval >= setting["logical_fps"] / 4:
            tps_interval = 0
            fps = clock.get_fps()
        pygame.display.set_caption("台球模拟器 TPS: {:.2f}".format(fps))




        pygame.display.flip()
        clock.tick(setting["fps"])

    pygame.quit()
