import pygame
import math
import random
import os


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)
DARK_BLUE = (0, 0, 100)
LIGHT_GRAY = (200, 200, 200)


# Initialize Pygame
pygame.init()
pygame.mixer.init() # INITIALISER PYGAME MIXER FOR LYD


# Constants
SCREEN_WIDTH = 736
SCREEN_HEIGHT = 1024
FPS = 60
GRAVITY = 0.3
BALL_RADIUS = 12
FLIPPER_LENGTH = 80
FLIPPER_WIDTH = 8
WALL_THICKNESS = 8
STUCK_THRESHOLD = 0.5 # Hastighedstærskel for at bolden anses for at sidde fast

COLLECTIBLE_RADIUS = 8
COLLECTIBLE_POINTS = 50
COLLECTIBLE_COLOR = GREEN
COLLECTIBLE_MAX_COUNT = 10 # Maksimum antal samleobjekter


class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = 0
        self.radius = BALL_RADIUS

    def update(self):
        self.vy += GRAVITY
        self.x += self.vx
        self.y += self.vy

        if self.x - self.radius <= 0:
            self.x = self.radius
            self.vx = abs(self.vx) * 0.8
        elif self.x + self.radius >= SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.radius
            self.vx = -abs(self.vx) * 0.8

        if self.y - self.radius <= 0:
            self.y = self.radius
            self.vy = abs(self.vy) * 0.8

        self.vx *= 0.999
        self.vy *= 0.999

    def get_speed(self):
        return math.sqrt(self.vx**2 + self.vy**2)

    def draw(self, screen):
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x - 3), int(self.y - 3)), 3)

class Flipper:
    def __init__(self, x, y, left_flipper=True):
        self.pivot_x = x
        self.pivot_y = y
        self.length = FLIPPER_LENGTH
        self.width = FLIPPER_WIDTH
        self.left_flipper = left_flipper
        self.rest_angle = 45 if left_flipper else 135
        self.active_angle = -15 if left_flipper else 195
        self.angle = self.rest_angle
        self.target_angle = self.angle
        self.is_active = False

    def activate(self):
        self.is_active = True
        self.target_angle = self.active_angle

    def deactivate(self):
        self.is_active = False
        self.target_angle = self.rest_angle

    def update(self):
        angle_diff = self.target_angle - self.angle
        if abs(angle_diff) > 0.5:
            self.angle += angle_diff * 0.2
        else:
            self.angle = self.target_angle

    def get_end_point(self):
        angle_rad = math.radians(self.angle)
        end_x = self.pivot_x + self.length * math.cos(angle_rad)
        end_y = self.pivot_y + self.length * math.sin(angle_rad)
        return end_x, end_y

    def get_flipper_polygon_points(self):
        angle_rad = math.radians(self.angle)

        fx = self.length * math.cos(angle_rad)
        fy = self.length * math.sin(angle_rad)

        px = -self.width / 2 * math.sin(angle_rad)
        py = self.width / 2 * math.cos(angle_rad)

        p1 = (self.pivot_x + px, self.pivot_y + py)
        p2 = (self.pivot_x - px, self.pivot_y - py)
        p3 = (self.pivot_x - px + fx, self.pivot_y - py + fy)
        p4 = (self.pivot_x + px + fx, self.pivot_y + py + fy)

        return [p1, p2, p3, p4]

    def draw(self, screen):
        flipper_points = self.get_flipper_polygon_points()
        pygame.draw.polygon(screen, YELLOW, flipper_points)

        end_x, end_y = self.get_end_point()
        pygame.draw.circle(screen, YELLOW, (int(end_x), int(end_y)), self.width // 2)

        pygame.draw.circle(screen, GRAY, (int(self.pivot_x), int(self.pivot_y)), 5)

    def check_collision(self, ball, sound_manager=None): # Tilføj sound_manager
        flipper_start_x, flipper_start_y = self.pivot_x, self.pivot_y
        flipper_end_x, flipper_end_y = self.get_end_point()

        v_start_ball_x = ball.x - flipper_start_x
        v_start_ball_y = ball.y - flipper_start_y

        v_flipper_x = flipper_end_x - flipper_start_x
        v_flipper_y = flipper_end_y - flipper_start_y

        flipper_length_sq = v_flipper_x * v_flipper_x + v_flipper_y * v_flipper_y
        if flipper_length_sq == 0:
            return False

        t = max(0, min(1, (v_start_ball_x * v_flipper_x + v_start_ball_y * v_flipper_y) / flipper_length_sq))

        closest_x = flipper_start_x + t * v_flipper_x
        closest_y = flipper_start_y + t * v_flipper_y

        dx = ball.x - closest_x
        dy = ball.y - closest_y
        distance = math.sqrt(dx * dx + dy * dy)

        collision_threshold = ball.radius + self.width / 2
        if distance <= collision_threshold:
            if distance == 0:
                ball.vx = random.uniform(-1, 1) * 5
                ball.vy = random.uniform(-1, 1) * 5
                if sound_manager:
                    sound_manager.play_flipper_hit() # Afspil flipper lyd
                return True

            nx = dx / distance
            ny = dy / distance

            dot_product = ball.vx * nx + ball.vy * ny

            if dot_product < 0:
                ball.vx -= 2 * dot_product * nx
                ball.vy -= 2 * dot_product * ny

                if self.is_active:
                    force_multiplier = 2.0
                    ball.vx *= force_multiplier
                    ball.vy *= force_multiplier
                    ball.vy -= 6
                
                if sound_manager:
                    sound_manager.play_flipper_hit() # Afspil flipper lyd

                overlap = collision_threshold - distance
                ball.x += nx * (overlap + 0.5)
                ball.y += ny * (overlap + 0.5)

                return True
        return False

class Wall:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.wall_vec_x = self.x2 - self.x1
        self.wall_vec_y = self.y2 - self.y1
        self.normal_x = -self.wall_vec_y
        self.normal_y = self.wall_vec_x
        norm_mag = math.sqrt(self.normal_x**2 + self.normal_y**2)
        if norm_mag != 0:
            self.normal_x /= norm_mag
            self.normal_y /= norm_mag
        else:
            self.normal_x = 0
            self.normal_y = 0

    def draw(self, screen):
        pygame.draw.line(screen, LIGHT_GRAY, (self.x1, self.y1), (self.x2, self.y2), WALL_THICKNESS)

    def check_collision(self, ball, sound_manager=None): # Tilføj sound_manager
        wx = self.x2 - self.x1
        wy = self.y2 - self.y1

        bx_to_wall_start = ball.x - self.x1
        by_to_wall_start = ball.y - self.y1

        wall_length_sq = wx * wx + wy * wy

        if wall_length_sq == 0:
            return False

        t = max(0, min(1, (bx_to_wall_start * wx + by_to_wall_start * wy) / wall_length_sq))

        closest_x = self.x1 + t * wx
        closest_y = self.y1 + t * wy

        dx_to_ball_center = ball.x - closest_x
        dy_to_ball_center = ball.y - closest_y

        distance = math.sqrt(dx_to_ball_center * dx_to_ball_center + dy_to_ball_center * dy_to_ball_center)

        collision_threshold = ball.radius + WALL_THICKNESS / 2

        if distance < collision_threshold:
            if distance == 0:
                nx = self.normal_x
                ny = self.normal_y
            else:
                nx = dx_to_ball_center / distance
                ny = dy_to_ball_center / distance

            dot_product = ball.vx * nx + ball.vy * ny

            ball.vx -= 2 * dot_product * nx
            ball.vy -= 2 * dot_product * ny

            ball.vx *= 0.8
            ball.vy *= 0.8

            overlap = collision_threshold - distance
            ball.x += nx * (overlap + 0.2)
            ball.y += ny * (overlap + 0.2)

            if sound_manager:
                sound_manager.play_wall_hit() # Afspil væg lyd

            return True

        return False

class Collectible:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = COLLECTIBLE_RADIUS
        self.collected = False

    def draw(self, screen):
        if not self.collected:
            pygame.draw.circle(screen, COLLECTIBLE_COLOR, (int(self.x), int(self.y)), self.radius)
            # Add a small sparkle for visual appeal
            pygame.draw.circle(screen, WHITE, (int(self.x + self.radius/2), int(self.y - self.radius/2)), self.radius // 3)


    def check_collision(self, ball, sound_manager=None): # Tilføj sound_manager
        if self.collected:
            return False

        distance = math.sqrt((self.x - ball.x)**2 + (self.y - ball.y)**2)
        if distance < self.radius + ball.radius:
            self.collected = True
            if sound_manager:
                sound_manager.play_collectible_pickup() # Afspil collectible lyd
            return True
        return False

class SoundManager: # NY KLASSE TIL LYDHÅNDTERING
    def __init__(self):
        self.flipper_hit_sound = None
        self.wall_hit_sound = None
        self.ball_lost_sound = None
        self.collectible_pickup_sound = None
        self.background_music = None

        self._load_sounds()
        self._play_music()

    def _load_sounds(self):
        try:
            # Sørg for at disse filer findes i samme mappe som scriptet
            # Du skal erstatte 'path_to_sound.wav' med de faktiske filnavne
            self.flipper_hit_sound = pygame.mixer.Sound("flipper_hit.mp3") # Eks: Kort "pop" eller "thwack"
            self.wall_hit_sound = pygame.mixer.Sound("wall_hit.mp3")     # Eks: Blødere "thud"
            self.ball_lost_sound = pygame.mixer.Sound("lost_ball_hit.mp3")   # Eks: Dyb "boing" eller "splat"
            self.collectible_pickup_sound = pygame.mixer.Sound("punch_hit.mp3") # Eks: "Ding" eller "chime"

            # Juster lydstyrken efter behov
            self.flipper_hit_sound.set_volume(0.5)
            self.wall_hit_sound.set_volume(0.3)
            self.ball_lost_sound.set_volume(0.7)
            self.collectible_pickup_sound.set_volume(0.4)

        except pygame.error as e:
            print(f"Kunne ikke indlæse lyde: {e}")
            # Fortsæt uden lyde, hvis de ikke kan indlæses

        try:
            self.background_music = "background_music.mp3" # Eks: .mp3 eller .ogg fil
            pygame.mixer.music.load(self.background_music)
            pygame.mixer.music.set_volume(0.2) # Baggrundsmusik skal være lavere
        except pygame.error as e:
            print(f"Kunne ikke indlæse baggrundsmusik: {e}")
            self.background_music = None

    def _play_music(self):
        if self.background_music:
            pygame.mixer.music.play(-1) # -1 gør at musikken looper uendeligt

    def play_flipper_hit(self):
        if self.flipper_hit_sound:
            self.flipper_hit_sound.play()

    def play_wall_hit(self):
        if self.wall_hit_sound:
            self.wall_hit_sound.play()

    def play_ball_lost(self):
        if self.ball_lost_sound:
            self.ball_lost_sound.play()

    def play_collectible_pickup(self):
        if self.collectible_pickup_sound:
            self.collectible_pickup_sound.play()


class PinballGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pinball Simulator")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72) # Til Game Over skærm

        try:
            self.background_image = pygame.image.load("pinball.png").convert()
            self.background_image = pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except pygame.error as e:
            print(f"Kunne ikke indlæse baggrundsbillede: {e}")
            self.background_image = None
        
        self.sound_manager = SoundManager() # Opret SoundManager instansen


        self.highscore = self.load_highscore()
        self.game_over = False
        self.reset_game()
        self.create_walls()
        # self.create_collectibles() # Kaldes i reset_game nu

    def load_highscore(self):
        if os.path.exists("highscore.txt"):
            with open("highscore.txt", "r") as f:
                try:
                    return int(f.read())
                except ValueError:
                    return 0 # Filen er tom eller indeholder ugyldig data
        return 0

    def save_highscore(self):
        with open("highscore.txt", "w") as f:
            f.write(str(self.highscore))

    def reset_game(self):
        self.score = 0
        self.balls_left = 5 # Antal kugler pr. spil
        self.last_extra_ball_score_threshold = 0 # Nulstil tærskel for ekstrabold
        self.game_over = False
        self._spawn_new_ball()

        self.left_flipper = Flipper(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 120, True)
        self.right_flipper = Flipper(SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT - 120, False)
        
        # Sørg for at samleobjekter også nulstilles/genoprettes
        self.create_collectibles()


    def _spawn_new_ball(self):
        # Spawns ball higher up to allow it to fall into place
        start_x = random.randint(SCREEN_WIDTH // 2 - 50, SCREEN_WIDTH // 2 + 50)
        self.ball = Ball(start_x, 175)

    def create_walls(self):
        self.walls = []

        # Outer Left Wall
        self.walls.append(Wall(170, 230, 170, SCREEN_HEIGHT - 280))

        # Outer Right Wall
        self.walls.append(Wall(SCREEN_WIDTH - 170, 230, SCREEN_WIDTH - 170, SCREEN_HEIGHT - 280))

        # Top Wall (extended)
        self.walls.append(Wall(170, 100, SCREEN_WIDTH - 170, 100)) # Extended

        # Left Angled Wall (leading to flipper area)
        self.walls.append(Wall(170, SCREEN_HEIGHT - 280, SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT - 130))

        # Right Angled Wall (leading to flipper area)
        self.walls.append(Wall(SCREEN_WIDTH // 2 + 130, SCREEN_HEIGHT - 130, SCREEN_WIDTH - 170, SCREEN_HEIGHT - 280))

        # Left Flipper Gutter Wall (short inner wall near flipper)
        self.walls.append(Wall(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT - 130, SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT - 50))

        # Right Flipper Gutter Wall (short inner wall near flipper)
        self.walls.append(Wall(SCREEN_WIDTH // 2 + 90, SCREEN_HEIGHT - 50, SCREEN_WIDTH // 2 + 130, SCREEN_HEIGHT - 130))

        # --- New Walls and Obstacles ---

        # Central "V" Obstacle (two walls)
        self.walls.append(Wall(SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 - 100, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.walls.append(Wall(SCREEN_WIDTH // 2 + 60, SCREEN_HEIGHT // 2 - 100, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))

        # Left Bumper Wall
        self.walls.append(Wall(220, SCREEN_HEIGHT // 2 - 20, 220, SCREEN_HEIGHT // 2 + 60))

        # Right Bumper Wall
        self.walls.append(Wall(SCREEN_WIDTH - 220, SCREEN_HEIGHT // 2 - 20, SCREEN_WIDTH - 220, SCREEN_HEIGHT // 2 + 60))

        # Angled walls above the flippers
        self.walls.append(Wall(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT - 200, SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT - 250))
        self.walls.append(Wall(SCREEN_WIDTH // 2 + 130, SCREEN_HEIGHT - 200, SCREEN_WIDTH // 2 + 200, SCREEN_HEIGHT - 250))

    def create_collectibles(self):
        self.collectibles = []
        
        # Definer et område hvor collectibles kan spawne
        # Juster disse for at styre hvor på banen de kan dukke op
        min_x = 200
        max_x = SCREEN_WIDTH - 200
        min_y = 150
        max_y = SCREEN_HEIGHT - 350 # Undgå flipperområdet

        # Tilføj et tilfældigt antal samleobjekter op til COLLECTIBLE_MAX_COUNT
        num_collectibles_to_add = random.randint(5, COLLECTIBLE_MAX_COUNT)

        for _ in range(num_collectibles_to_add):
            # Generer tilfældige koordinater inden for det definerede område
            x = random.randint(min_x, max_x)
            y = random.randint(min_y, max_y)
            self.collectibles.append(Collectible(x, y))


    def handle_input(self):
        keys = pygame.key.get_pressed()

        if not self.game_over:
            if keys[pygame.K_LSHIFT] or keys[pygame.K_LCTRL]:
                self.left_flipper.activate()
            else:
                self.left_flipper.deactivate()

            if keys[pygame.K_RSHIFT] or keys[pygame.K_RCTRL]:
                self.right_flipper.activate()
            else:
                self.right_flipper.deactivate()
            
            # Ny logik for at resette bolden, hvis den sidder fast
            if keys[pygame.K_r] and self.ball.get_speed() < STUCK_THRESHOLD:
                print("Bolden sidder fast, resetter...")
                self._spawn_new_ball()


    def update(self):
        if self.game_over:
            return

        self.ball.update()
        self.left_flipper.update()
        self.right_flipper.update()

        for wall in self.walls:
            wall.check_collision(self.ball, self.sound_manager) # Send sound_manager med

        if self.left_flipper.check_collision(self.ball, self.sound_manager): # Send sound_manager med
            self.score += 10
        if self.right_flipper.check_collision(self.ball, self.sound_manager): # Send sound_manager med
            self.score += 10

        # Tjek kollision med samleobjekter
        collectibles_to_remove = []
        for collectible in self.collectibles:
            if collectible.check_collision(self.ball, self.sound_manager): # Send sound_manager med
                self.score += COLLECTIBLE_POINTS
                collectibles_to_remove.append(collectible)
        
        # Fjern samlede objekter
        for collectible in collectibles_to_remove:
            self.collectibles.remove(collectible)

        # Tjek om alle collectibles er samlet og genopret dem
        if not self.collectibles: # Hvis listen er tom
            print("Alle samleobjekter er samlet! Genopretter nye.")
            self.create_collectibles() # Kalder for at oprette nye

        # --- Ny logik for ekstrabold baseret på score ---
        if self.score >= self.last_extra_ball_score_threshold + 500:
            self.balls_left += 1
            self.last_extra_ball_score_threshold += 500
            print(f"Ekstra bold! Antal bolde tilbage: {self.balls_left}")
            # Tilføj evt. en lyd for ekstrabold her

        # Check if ball went out of bounds
        if self.ball.y > SCREEN_HEIGHT + 50:
            self.balls_left -= 1
            self.sound_manager.play_ball_lost() # AFSPIL LYD NÅR BOLDEN TABES
            if self.balls_left > 0:
                self._spawn_new_ball()
            else:
                self.game_over = True
                if self.score > self.highscore:
                    self.highscore = self.score
                    self.save_highscore()

    def draw(self):
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
            self.screen.fill(DARK_BLUE)

        for wall in self.walls:
            wall.draw(self.screen)

        for collectible in self.collectibles: # Tegn samleobjekter
            collectible.draw(self.screen)

        self.left_flipper.draw(self.screen)
        self.right_flipper.draw(self.screen)
        self.ball.draw(self.screen)

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        balls_text = self.font.render(f"Kugler: {self.balls_left}", True, WHITE)
        self.screen.blit(balls_text, (SCREEN_WIDTH - balls_text.get_width() - 10, 10))

        highscore_text = self.font.render(f"Highscore: {self.highscore}", True, WHITE)
        self.screen.blit(highscore_text, (10, 50))

        # Vis instruktion for reset
        if self.ball.get_speed() < STUCK_THRESHOLD and not self.game_over:
            reset_instruction_text = self.font.render("Bold sidder fast? Tryk 'R' for reset", True, YELLOW)
            self.screen.blit(reset_instruction_text, (SCREEN_WIDTH // 2 - reset_instruction_text.get_width() // 2, SCREEN_HEIGHT - 20))


        if self.game_over:
            self.draw_game_over()

        pygame.display.flip()

    def draw_game_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180)) # Sort med 180 alpha
        self.screen.blit(overlay, (0, 0))

        game_over_label = self.large_font.render("GAME OVER", True, RED)
        go_rect = game_over_label.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(game_over_label, go_rect)

        final_score_label = self.font.render(f"Din Score: {self.score}", True, WHITE)
        fs_rect = final_score_label.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(final_score_label, fs_rect)

        current_highscore_label = self.font.render(f"Highscore: {self.highscore}", True, WHITE)
        ch_rect = current_highscore_label.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        self.screen.blit(current_highscore_label, ch_rect)

        if self.score == self.highscore and self.highscore > 0: # Kun vis "New Highscore!" hvis det er en ny highscore
            new_highscore_label = self.font.render("NY HIGH SCORE!", True, YELLOW)
            nh_rect = new_highscore_label.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(new_highscore_label, nh_rect)

        try_again_label = self.font.render("Tryk SPACE for at spille igen", True, WHITE)
        ta_rect = try_again_label.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120))
        self.screen.blit(try_again_label, ta_rect)

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.game_over:
                            self.reset_game()
                        # Removed the reset_game() call here for in-game reset
                        # as it's now handled by losing balls.

            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()

if __name__ == "__main__":
    game = PinballGame()
    game.run()