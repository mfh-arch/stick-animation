import pygame
import math
import sys

# 1. Inisialisasi Pygame
pygame.init()
WIDTH, HEIGHT = 450, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stick Figure")
clock = pygame.time.Clock()

# Warna
BG_COLOR = (12, 12, 12)        # Hitam gelap
WHITE = (235, 235, 235)        # Putih untuk teks & karakter
GRAY = (100, 100, 100)          # Garis tanah
YELLOW = (255, 220, 120)        # Cahaya lentera
GOLD = (255, 215, 0)           # Warna berkah raja

# Font
font_size = 20
try:
    font = pygame.font.SysFont("Comic Sans MS", font_size)
except:
    font = pygame.font.Font(None, font_size)

# Teks Puisi
lines = [
    "So tell me, where shall i go?",
    "To the left, where nothing's right?",
    "Or to the right, where nothing's left?"
]

def draw_text(surface):
    start_y = 180
    for i, line in enumerate(lines):
        text_surf = font.render(line, True, WHITE)
        text_rect = text_surf.get_rect(center=(WIDTH // 2, start_y + i * 32))
        surface.blit(text_surf, text_rect)

def draw_lantern_glow(surface, x, y, color=YELLOW):
    """Membuat efek pendaran cahaya lentera."""
    glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    for radius in range(60, 0, -4):
        alpha = int(120 * (1 - radius / 60)**1.5)
        pygame.draw.circle(glow_surf, (color[0], color[1], color[2], alpha), (60, 60), radius)
    surface.blit(glow_surf, (x - 60, y - 60))
    
    # Inti lentera
    pygame.draw.circle(surface, color, (int(x), int(y)), 4)
    pygame.draw.rect(surface, WHITE, (int(x)-3, int(y)-5, 6, 8), 1)

def draw_blessing_aura(surface, x, y, progress):
    """Efek pendaran emas saat menerima berkah dari Raja."""
    glow_surf = pygame.Surface((200, 200), pygame.SRCALPHA)
    max_r = int(90 * progress)
    for radius in range(max_r, 0, -5):
        alpha = int(110 * (1 - radius / max_r) * progress)
        pygame.draw.circle(glow_surf, (255, 215, 0, alpha), (100, 100), radius)
    surface.blit(glow_surf, (x - 100, y - 100))

def main():
    running = True
    start_time = pygame.time.get_ticks()

    # Koordinat dasar
    center_x = WIDTH // 2
    ground_y = 480

    # Timeline Waktu per-fase (dalam detik)
    t_walk_right_end = 2.5   # Jalan ke kanan
    t_walk_left_end  = 5.0   # Jalan kembali ke tengah
    t_pause_end      = 6.0   # Berdiri ragu sejenak
    t_kneel_end      = 8.5   # Bertekuk lutut selesai
    total_cycle_time = 11.0  # Durasi total sebelum ulang dari awal (Looping)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 1. Menghitung Waktu Real-Time
        t_raw = (pygame.time.get_ticks() - start_time) / 1000.0
        t = t_raw % total_cycle_time

        screen.fill(BG_COLOR)

        # Gambar Teks Puisi & Garis Tanah
        draw_text(screen)
        pygame.draw.line(screen, GRAY, (80, ground_y), (370, ground_y), 2)

        # === LOGIKA FASE ANIMASI ===
        facing_right = True
        char_color = WHITE
        blessing_progress = 0.0
        kneel_p = 0.0

        if t < t_walk_right_end:
            # FASE 1: Jalan ke Kanan
            progress = t / t_walk_right_end
            char_x = (center_x - 60) + progress * 120
            facing_right = True
            step_swing = math.sin(t * 8) * 12
            lantern_swing = math.sin(t * 4) * 6

        elif t < t_walk_left_end:
            # FASE 2: Jalan Kembali ke Kiri (ke tengah)
            progress = (t - t_walk_right_end) / (t_walk_left_end - t_walk_right_end)
            char_x = (center_x + 60) - progress * 60
            facing_right = False
            step_swing = math.sin(t * 8) * 12
            lantern_swing = math.sin(t * 4) * 6

        elif t < t_pause_end:
            # FASE 3: Berhenti di Tengah (Berdiri Tegak)
            char_x = center_x
            facing_right = True
            step_swing = 0
            lantern_swing = 0

        elif t < t_kneel_end:
            # FASE 4: Transisi Bertekuk Lutut (Sembah)
            char_x = center_x
            facing_right = True
            step_swing = 0
            lantern_swing = 0
            kneel_p = (t - t_pause_end) / (t_kneel_end - t_pause_end)

        else:
            # FASE 5: Bertekuk Lutut Total & Berkah Emas
            char_x = center_x
            facing_right = True
            step_swing = 0
            lantern_swing = 0
            kneel_p = 1.0
            
            blessing_progress = min(1.0, (t - t_kneel_end) / 1.5)
            # Transisi Warna ke Emas
            char_color = (
                int(WHITE[0] + (GOLD[0] - WHITE[0]) * blessing_progress),
                int(WHITE[1] + (GOLD[1] - WHITE[1]) * blessing_progress),
                int(WHITE[2] + (GOLD[2] - WHITE[2]) * blessing_progress)
            )

        # === HITUNG POSISI SENDI KARAKTER (DIPERBAIKI AGAR BERLUTUT TEGAK) ===
        # Pinggul ditarik sedikit ke belakang agar paha depan pas
        hip_x = char_x - (5 * kneel_p)
        hip_y = (ground_y - 30) + (10 * kneel_p)

        # Leher & Kepala diatur TEGAK LURUS di atas pinggul
        neck_x = hip_x  
        neck_y = hip_y - 35

        head_x = neck_x
        head_y = neck_y - 15

        # === MENGGAMBAR STICK FIGURE ===

        # 1. Kepala
        pygame.draw.circle(screen, char_color, (int(head_x), int(head_y)), 12, 2)

        # 2. Badan (Punggung Tegak Lurus)
        pygame.draw.line(screen, char_color, (neck_x, neck_y), (hip_x, hip_y), 2)

        # 3. Kaki (Anatomi Berlutut Tegak)
        if kneel_p == 0.0:
            dir_mult = 1 if facing_right else -1
            pygame.draw.line(screen, char_color, (hip_x, hip_y), (hip_x + step_swing * dir_mult, ground_y), 2)
            pygame.draw.line(screen, char_color, (hip_x, hip_y), (hip_x - step_swing * dir_mult, ground_y), 2)
        else:
            # Kaki Depan (Paha Horisontal 90 Derajat, Betis Tegak)
            front_knee_x = hip_x + (22 * kneel_p)
            front_knee_y = hip_y
            front_foot_x = front_knee_x
            pygame.draw.line(screen, char_color, (hip_x, hip_y), (front_knee_x, front_knee_y), 2)
            pygame.draw.line(screen, char_color, (front_knee_x, front_knee_y), (front_foot_x, ground_y), 2)

            # Kaki Belakang (Lutut Menempel Tanah)
            back_knee_x = hip_x - (5 * kneel_p)
            back_foot_x = back_knee_x - (20 * kneel_p)
            pygame.draw.line(screen, char_color, (hip_x, hip_y), (back_knee_x, ground_y), 2)
            pygame.draw.line(screen, char_color, (back_knee_x, ground_y), (back_foot_x, ground_y), 2)

        # 4. Tangan & Lentera (MEMEGANG LENTERA DI DEPAN DADA TEGAK)
        if kneel_p == 0.0:
            arm_dir = 18 if facing_right else -18
            hand_x = neck_x + arm_dir
            hand_y = neck_y + 15 + lantern_swing
            
            pygame.draw.line(screen, char_color, (neck_x, neck_y), (hand_x, hand_y), 2)
            pygame.draw.line(screen, char_color, (neck_x, neck_y), (neck_x - arm_dir * 0.6, neck_y + 20), 2)
            
            lantern_x = hand_x + (5 if facing_right else -5)
            lantern_y = hand_y + 15
        else:
            # Tangan terangkat khidmat memegang lentera di depan dada
            hand_x = neck_x + (15 * kneel_p)
            hand_y = neck_y + (15 * kneel_p)
            
            pygame.draw.line(screen, char_color, (neck_x, neck_y), (hand_x, hand_y), 2)
            pygame.draw.line(screen, char_color, (neck_x, neck_y), (hand_x - 3, hand_y + 3), 2)

            lantern_x = hand_x + 2
            lantern_y = hand_y + 18

        # Gambar Tali Lentera & Cahaya
        pygame.draw.line(screen, char_color, (hand_x, hand_y), (lantern_x, lantern_y - 5), 1)
        draw_lantern_glow(screen, lantern_x, lantern_y)

        # 5. Aura Berkah Emas dari Atas
        if blessing_progress > 0:
            draw_blessing_aura(screen, head_x, head_y - 15, blessing_progress)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()