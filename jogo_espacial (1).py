import tkinter as tk
import random
import math
import json
import os

# Configurações da Janela e Jogo
WIDTH = 600
HEIGHT = 700
FPS = 16  # ~60 quadros por segundo
HIGHSCORE_FILE = os.path.join(os.path.dirname(__file__), "highscore.json")


class SpaceArcadeGame:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🚀 Defensor Estelar - Arcade em Python")
        self.root.resizable(False, False)
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after(600, lambda: self.root.attributes("-topmost", False))
        self.root.focus_force()

        self.canvas = tk.Canvas(
            root, width=WIDTH, height=HEIGHT, bg="#0b0c10", highlightthickness=0
        )
        self.canvas.pack()

        # Controles (Teclado + Toque/Mouse estilo Mobile)
        self.keys = set()
        self.touch_active = False
        self.touch_x = WIDTH // 2
        self.touch_y = HEIGHT - 70
        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)
        self.root.bind("<FocusOut>", self.on_focus_out)
        self.canvas.bind("<ButtonPress-1>", self.on_touch_start)
        self.canvas.bind("<B1-Motion>", self.on_touch_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_touch_end)

        # Fundo estelar em camadas (parallax)
        self.stars = [
            {
                "x": random.randint(0, WIDTH),
                "y": random.randint(0, HEIGHT),
                "size": random.choice([1, 2, 3]),
                "speed": random.uniform(0.5, 3.0),
                "color": random.choice(["#ffffff", "#66fcf1", "#c5c6c7", "#45a29e"]),
            }
            for _ in range(80)
        ]

        self.high_score = self.load_high_score()
        self.state = "MENU"  # MENU, PLAYING, PAUSED, GAMEOVER
        self.reset_game()
        self.update()

    def load_high_score(self) -> int:
        try:
            if os.path.exists(HIGHSCORE_FILE):
                with open(HIGHSCORE_FILE, "r", encoding="utf-8") as f:
                    return int(json.load(f).get("high_score", 0))
        except Exception:
            pass
        return 0

    def save_high_score(self):
        try:
            with open(HIGHSCORE_FILE, "w", encoding="utf-8") as f:
                json.dump({"high_score": self.high_score}, f)
        except Exception:
            pass

    def reset_game(self):
        self.player_x = WIDTH // 2
        self.player_y = HEIGHT - 70
        self.player_speed = 7
        self.lives = 3
        self.score = 0
        self.combo = 1
        self.combo_timer = 0
        self.level = 1
        self.shoot_cooldown = 0
        self.invulnerable = 0
        self.shield_active = False
        self.screen_shake = 0

        self.bullets = []
        self.enemy_bullets = []
        self.asteroids = []
        self.particles = []
        self.floating_texts = []
        self.powerups = []
        self.boss = None
        self.boss_count = 0
        self.next_boss_score = 300
        self.rapid_fire_timer = 0
        self.spawn_timer = 0

    def on_key_press(self, event):
        key = event.keysym.lower()
        self.keys.add(key)

        if self.state == "MENU" and key in ("space", "return"):
            self.reset_game()
            self.state = "PLAYING"
        elif self.state == "PLAYING" and key == "p":
            self.state = "PAUSED"
        elif self.state == "PAUSED" and key in ("p", "space", "return"):
            self.state = "PLAYING"
        elif self.state == "GAMEOVER" and key in ("r", "return", "space"):
            self.reset_game()
            self.state = "PLAYING"

    def on_key_release(self, event):
        key = event.keysym.lower()
        if key in self.keys:
            self.keys.remove(key)

    def on_focus_out(self, _event):
        self.keys.clear()
        self.touch_active = False

    def on_touch_start(self, event):
        if self.state in ("MENU", "GAMEOVER"):
            self.reset_game()
            self.state = "PLAYING"
            return
        if self.state == "PAUSED":
            self.state = "PLAYING"
            return
        self.touch_active = True
        self.touch_x = event.x
        self.touch_y = event.y

    def on_touch_move(self, event):
        self.touch_x = event.x
        self.touch_y = event.y

    def on_touch_end(self, _event):
        self.touch_active = False

    def spawn_explosion(self, x, y, color="#ff6b6b", count=15):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1.5, 6.5)
            self.particles.append(
                {
                    "x": x,
                    "y": y,
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "life": random.randint(15, 32),
                    "color": color,
                    "size": random.randint(2, 5),
                }
            )

    def add_floating_text(self, x, y, text, color="#ffffff"):
        self.floating_texts.append(
            {"x": x, "y": y, "text": text, "color": color, "life": 35}
        )

    def update(self):
        self.canvas.delete("all")

        # Efeito de tremor de tela (Screen Shake)
        ox, oy = 0, 0
        if self.screen_shake > 0:
            self.screen_shake -= 1
            ox = random.randint(-5, 5)
            oy = random.randint(-5, 5)

        # 1. Atualizar e desenhar estrelas de fundo
        for star in self.stars:
            if self.state != "PAUSED":
                star["y"] += star["speed"]
                if star["y"] > HEIGHT:
                    star["y"] = 0
                    star["x"] = random.randint(0, WIDTH)
            s = star["size"]
            self.canvas.create_oval(
                star["x"] + ox,
                star["y"] + oy,
                star["x"] + s + ox,
                star["y"] + s + oy,
                fill=star["color"],
                outline="",
            )

        if self.state == "PLAYING":
            self.update_gameplay()

        # Atualizar e desenhar partículas
        for p in self.particles[:]:
            if self.state != "PAUSED":
                p["x"] += p["vx"]
                p["y"] += p["vy"]
                p["life"] -= 1
            if p["life"] <= 0:
                self.particles.remove(p)
            else:
                sz = p["size"]
                self.canvas.create_oval(
                    p["x"] - sz + ox,
                    p["y"] - sz + oy,
                    p["x"] + sz + ox,
                    p["y"] + sz + oy,
                    fill=p["color"],
                    outline="",
                )

        # Atualizar e desenhar textos flutuantes
        for ft in self.floating_texts[:]:
            if self.state != "PAUSED":
                ft["y"] -= 1.2
                ft["life"] -= 1
            if ft["life"] <= 0:
                self.floating_texts.remove(ft)
            else:
                self.canvas.create_text(
                    ft["x"] + ox,
                    ft["y"] + oy,
                    text=ft["text"],
                    fill=ft["color"],
                    font=("Consolas", 11, "bold"),
                )

        # Renderizar de acordo com o estado do jogo
        if self.state == "MENU":
            self.draw_menu()
        elif self.state == "PLAYING":
            self.draw_gameplay(ox, oy)
            self.draw_hud()
        elif self.state == "PAUSED":
            self.draw_gameplay(ox, oy)
            self.draw_hud()
            self.draw_pause()
        elif self.state == "GAMEOVER":
            self.draw_gameplay(ox, oy)
            self.draw_hud()
            self.draw_game_over()

        self.root.after(FPS, self.update)

    def add_score(self, base_points: int, x: float, y: float):
        points = base_points * self.combo
        self.score += points
        self.combo = min(8, self.combo + 1)
        self.combo_timer = 150  # ~2.5 segundos para manter combo
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
        label = f"+{points}" + (f" (x{self.combo})" if self.combo > 1 else "")
        self.add_floating_text(x, y, label, "#eccc68" if self.combo > 1 else "#ffffff")

    def spawn_powerup(self, x: float, y: float):
        kind = random.choices(
            ["rapid", "shield", "bomb", "heart"], weights=[45, 25, 15, 15], k=1
        )[0]
        icons = {"rapid": "⚡", "shield": "🛡️", "bomb": "💣", "heart": "❤️"}
        colors = {
            "rapid": "#2ed573",
            "shield": "#1e90ff",
            "bomb": "#ffa502",
            "heart": "#ff4757",
        }
        self.powerups.append(
            {"x": x, "y": y, "kind": kind, "icon": icons[kind], "color": colors[kind]}
        )

    def damage_player(self):
        if self.invulnerable > 0:
            return
        if self.shield_active:
            self.shield_active = False
            self.invulnerable = 45
            self.screen_shake = 8
            self.spawn_explosion(self.player_x, self.player_y, "#1e90ff", count=20)
            self.add_floating_text(self.player_x, self.player_y - 25, "ESCUDO QUEBROU!", "#1e90ff")
            return

        self.lives -= 1
        self.combo = 1
        self.invulnerable = 70
        self.screen_shake = 14
        self.spawn_explosion(self.player_x, self.player_y, "#66fcf1", count=28)
        if self.lives <= 0:
            self.save_high_score()
            self.state = "GAMEOVER"

    def update_gameplay(self):
        # Movimento do jogador (Teclado ou Arraste Mobile/Mouse)
        dx = int("right" in self.keys or "d" in self.keys) - int(
            "left" in self.keys or "a" in self.keys
        )
        dy = int("down" in self.keys or "s" in self.keys) - int(
            "up" in self.keys or "w" in self.keys
        )
        if dx and dy:
            diagonal_scale = 1 / math.sqrt(2)
            dx *= diagonal_scale
            dy *= diagonal_scale
        self.player_x += dx * self.player_speed
        self.player_y += dy * self.player_speed

        if self.touch_active:
            self.player_x += (self.touch_x - self.player_x) * 0.25
            self.player_y += (self.touch_y - 30 - self.player_y) * 0.25

        self.player_x = max(25, min(WIDTH - 25, self.player_x))
        self.player_y = max(70, min(HEIGHT - 35, self.player_y))

        # Timers
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.invulnerable > 0:
            self.invulnerable -= 1
        if self.rapid_fire_timer > 0:
            self.rapid_fire_timer -= 1
        if self.combo_timer > 0:
            self.combo_timer -= 1
            if self.combo_timer == 0:
                self.combo = 1

        # Disparo de lasers (Espaço ou Automático no Toque/Mouse)
        max_cooldown = 5 if self.rapid_fire_timer > 0 else 11
        if ("space" in self.keys or self.touch_active) and self.shoot_cooldown == 0:
            if self.rapid_fire_timer > 0:
                self.bullets.append({"x": self.player_x - 11, "y": self.player_y - 15, "vx": -0.5})
                self.bullets.append({"x": self.player_x, "y": self.player_y - 20, "vx": 0.0})
                self.bullets.append({"x": self.player_x + 11, "y": self.player_y - 15, "vx": 0.5})
            else:
                self.bullets.append({"x": self.player_x, "y": self.player_y - 20, "vx": 0.0})
            self.shoot_cooldown = max_cooldown

        # Atualizar projéteis do jogador
        for b in self.bullets[:]:
            b["y"] -= 13
            b["x"] += b.get("vx", 0.0)
            if b["y"] < -10:
                self.bullets.remove(b)

        # Atualizar projéteis inimigos
        for eb in self.enemy_bullets[:]:
            eb["x"] += eb["vx"]
            eb["y"] += eb["vy"]
            if eb["y"] > HEIGHT + 10 or eb["x"] < -10 or eb["x"] > WIDTH + 10:
                self.enemy_bullets.remove(eb)
                continue
            if math.hypot(eb["x"] - self.player_x, eb["y"] - self.player_y) < 16:
                self.enemy_bullets.remove(eb)
                self.damage_player()

        # Nível de dificuldade e aparição de Chefões (3 tipos de Boss)
        self.level = 1 + (self.score // 250)
        if self.boss is None and self.score >= self.next_boss_score:
            boss_types = [
                {
                    "type": "mothership",
                    "name": "NAVE-MÃE ESCARLATE",
                    "color": "#ff4757",
                    "core_color": "#66fcf1",
                    "vx": 3.5,
                    "hp_mult": 1.0,
                },
                {
                    "type": "phantom",
                    "name": "CRUZADOR FANTASMA",
                    "color": "#a55eea",
                    "core_color": "#2ed573",
                    "vx": 5.2,
                    "hp_mult": 1.2,
                },
                {
                    "type": "titan",
                    "name": "ENCOURAÇADO TITÃ",
                    "color": "#ffa502",
                    "core_color": "#ff4757",
                    "vx": 2.6,
                    "hp_mult": 1.6,
                },
            ]
            b_cfg = boss_types[self.boss_count % len(boss_types)]
            max_hp = int((20 + self.level * 10) * b_cfg["hp_mult"])
            self.boss = {
                "x": WIDTH // 2,
                "y": -60,
                "vx": b_cfg["vx"],
                "hp": max_hp,
                "max_hp": max_hp,
                "shoot_timer": 0,
                "special_timer": 0,
                "laser_active": 0,
                "type": b_cfg["type"],
                "name": b_cfg["name"],
                "color": b_cfg["color"],
                "core_color": b_cfg["core_color"],
                "phase": 0.0,
            }
            self.boss_count += 1
            self.add_floating_text(
                WIDTH // 2, 120, f"⚠️ {b_cfg['name']} DETECTADO!", b_cfg["color"]
            )

        # Atualizar Chefão (Boss)
        if self.boss:
            boss = self.boss
            boss["phase"] += 0.08
            if boss["y"] < 110:
                boss["y"] += 2
            else:
                boss["x"] += boss["vx"]
                if boss["type"] == "phantom":
                    boss["y"] = 110 + math.sin(boss["phase"]) * 28
                if boss["x"] < 70 or boss["x"] > WIDTH - 70:
                    boss["vx"] *= -1

            boss["shoot_timer"] += 1
            fire_interval = max(22, 55 - self.level * 3)
            if boss["shoot_timer"] >= fire_interval:
                boss["shoot_timer"] = 0
                base_angle = math.atan2(
                    self.player_y - boss["y"], self.player_x - boss["x"]
                )
                if boss["type"] == "mothership":
                    offsets = (-0.35, 0.0, 0.35)
                    speed = 5.5
                elif boss["type"] == "phantom":
                    offsets = (-0.5, -0.18, 0.18, 0.5)
                    speed = 6.5
                else:  # titan
                    offsets = (-0.6, -0.3, 0.0, 0.3, 0.6)
                    speed = 5.0

                for angle_offset in offsets:
                    angle = base_angle + angle_offset
                    self.enemy_bullets.append(
                        {
                            "x": boss["x"],
                            "y": boss["y"] + 30,
                            "vx": math.cos(angle) * speed,
                            "vy": math.sin(angle) * speed,
                            "color": boss["color"],
                        }
                    )

            # Habilidades especiais dos Bosses 2 e 3
            boss["special_timer"] += 1
            if boss["type"] == "phantom" and boss["special_timer"] >= 110:
                boss["special_timer"] = 0
                # Invoca mini-drone perseguidor
                self.asteroids.append(
                    {
                        "x": boss["x"],
                        "y": boss["y"] + 25,
                        "r": 12,
                        "speed": 6.0,
                        "vx": 2.2 if self.player_x > boss["x"] else -2.2,
                        "color": "#a55eea",
                    }
                )
            elif boss["type"] == "titan":
                if boss["special_timer"] == 120:
                    self.add_floating_text(boss["x"], boss["y"] + 45, "⚡ CARREGANDO MEGA LASER!", "#ffa502")
                elif boss["special_timer"] >= 165:
                    boss["laser_active"] = 35
                    boss["special_timer"] = 0
                    self.screen_shake = 6

            if boss.get("laser_active", 0) > 0:
                boss["laser_active"] -= 1
                if abs(self.player_x - boss["x"]) < 24 and self.player_y > boss["y"]:
                    self.damage_player()

            # Colisão laser -> Boss
            for b in self.bullets[:]:
                if abs(b["x"] - boss["x"]) < 58 and abs(b["y"] - boss["y"]) < 34:
                    self.bullets.remove(b)
                    boss["hp"] -= 1
                    self.spawn_explosion(b["x"], b["y"], boss["color"], count=5)
                    if boss["hp"] <= 0:
                        bx, by = boss["x"], boss["y"]
                        is_titan = boss["type"] == "titan"
                        b_color = boss["color"]
                        self.boss = None
                        self.next_boss_score = self.score + 500 + self.level * 150
                        self.screen_shake = 22
                        self.spawn_explosion(bx, by, b_color, count=50)
                        self.add_score(150 if is_titan else 100, bx, by)
                        self.spawn_powerup(bx - 15, by)
                        if is_titan:
                            self.spawn_powerup(bx + 15, by)
                        break

        # Gerar asteroides
        self.spawn_timer += 1
        spawn_rate = max(14, 42 - self.level * 3)
        if self.boss:
            spawn_rate *= 2  # Menos asteroides durante o chefão
        if self.spawn_timer >= spawn_rate:
            self.spawn_timer = 0
            radius = random.randint(14, 28)
            self.asteroids.append(
                {
                    "x": random.randint(radius, WIDTH - radius),
                    "y": -radius,
                    "r": radius,
                    "speed": random.uniform(2.5, 4.2 + self.level * 0.35),
                    "vx": random.uniform(-1.2, 1.2),
                    "color": random.choice(["#ff4757", "#ffa502", "#eccc68", "#ff6b81"]),
                }
            )

        # Atualizar asteroides e colisões
        for a in self.asteroids[:]:
            a["y"] += a["speed"]
            a["x"] += a["vx"]

            if a["x"] - a["r"] < 0 or a["x"] + a["r"] > WIDTH:
                a["vx"] *= -1

            if a["y"] - a["r"] > HEIGHT:
                self.asteroids.remove(a)
                continue

            # Colisão laser -> asteroide
            destroyed = False
            for b in self.bullets[:]:
                if math.hypot(a["x"] - b["x"], a["y"] - b["y"]) < a["r"] + 6:
                    self.bullets.remove(b)
                    self.asteroids.remove(a)
                    self.add_score(10, a["x"], a["y"])
                    self.spawn_explosion(a["x"], a["y"], a["color"], count=14)

                    if random.random() < 0.16:
                        self.spawn_powerup(a["x"], a["y"])
                    destroyed = True
                    break

            if destroyed:
                continue

            # Colisão asteroide -> jogador
            if math.hypot(a["x"] - self.player_x, a["y"] - self.player_y) < a["r"] + 16:
                self.asteroids.remove(a)
                self.damage_player()

        # Atualizar Power-ups
        for pw in self.powerups[:]:
            pw["y"] += 2.8
            if pw["y"] > HEIGHT:
                self.powerups.remove(pw)
                continue
            if math.hypot(pw["x"] - self.player_x, pw["y"] - self.player_y) < 26:
                self.powerups.remove(pw)
                kind = pw["kind"]
                self.spawn_explosion(pw["x"], pw["y"], pw["color"], count=15)
                if kind == "rapid":
                    self.rapid_fire_timer = 320
                    self.add_floating_text(pw["x"], pw["y"], "TIRO TRIPLO! ⚡", "#2ed573")
                elif kind == "shield":
                    self.shield_active = True
                    self.add_floating_text(pw["x"], pw["y"], "ESCUDO ATIVO! 🛡️", "#1e90ff")
                elif kind == "heart":
                    self.lives = min(5, self.lives + 1)
                    self.add_floating_text(pw["x"], pw["y"], "+1 VIDA! ❤️", "#ff4757")
                elif kind == "bomb":
                    self.screen_shake = 16
                    for ast in self.asteroids[:]:
                        self.spawn_explosion(ast["x"], ast["y"], ast["color"], count=10)
                        self.score += 10
                    self.asteroids.clear()
                    self.enemy_bullets.clear()
                    self.add_floating_text(pw["x"], pw["y"], "SUPERNOVA! 💣", "#ffa502")

    def draw_gameplay(self, ox=0, oy=0):
        # Desenhar Power-ups
        for pw in self.powerups:
            x, y = pw["x"] + ox, pw["y"] + oy
            self.canvas.create_oval(
                x - 12, y - 12, x + 12, y + 12, fill=pw["color"], outline="#ffffff", width=2
            )
            self.canvas.create_text(x, y, text=pw["icon"], fill="#ffffff", font=("Segoe UI Emoji", 10))

        # Desenhar Projéteis do Jogador
        for b in self.bullets:
            x, y = b["x"] + ox, b["y"] + oy
            color = "#2ed573" if self.rapid_fire_timer > 0 else "#66fcf1"
            self.canvas.create_rectangle(x - 2, y - 10, x + 2, y + 4, fill=color, outline="")

        # Desenhar Projéteis Inimigos
        for eb in self.enemy_bullets:
            x, y = eb["x"] + ox, eb["y"] + oy
            eb_color = eb.get("color", "#ff4757")
            self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill=eb_color, outline="#ffffff")

        # Desenhar Asteroides
        for a in self.asteroids:
            x, y, r = a["x"] + ox, a["y"] + oy, a["r"]
            self.canvas.create_oval(
                x - r, y - r, x + r, y + r, fill=a["color"], outline="#ffffff", width=2
            )
            self.canvas.create_oval(
                x - r * 0.4,
                y - r * 0.4,
                x + r * 0.1,
                y + r * 0.1,
                fill="#0b0c10",
                outline="",
            )

        # Desenhar Chefão (Boss)
        if self.boss:
            bx, by = self.boss["x"] + ox, self.boss["y"] + oy
            b_type = self.boss.get("type", "mothership")
            b_color = self.boss.get("color", "#ff4757")
            c_color = self.boss.get("core_color", "#66fcf1")

            if b_type == "phantom":
                # Formato furtivo angular (Cruzador Fantasma)
                self.canvas.create_polygon(
                    bx, by - 36,
                    bx - 60, by + 10,
                    bx - 25, by + 28,
                    bx, by + 14,
                    bx + 25, by + 28,
                    bx + 60, by + 10,
                    fill=b_color, outline="#ffffff", width=2,
                )
            elif b_type == "titan":
                # Formato blindado pesado (Encouraçado Titã)
                self.canvas.create_polygon(
                    bx - 65, by - 22,
                    bx - 35, by - 36,
                    bx + 35, by - 36,
                    bx + 65, by - 22,
                    bx + 55, by + 28,
                    bx - 55, by + 28,
                    fill=b_color, outline="#ffffff", width=3,
                )
            else:
                # Nave-Mãe Escarlate
                self.canvas.create_polygon(
                    bx - 55, by - 15,
                    bx - 25, by - 32,
                    bx + 25, by - 32,
                    bx + 55, by - 15,
                    bx + 35, by + 25,
                    bx - 35, by + 25,
                    fill=b_color, outline="#ffffff", width=2,
                )

            self.canvas.create_oval(
                bx - 16, by - 12, bx + 16, by + 12, fill="#0b0c10", outline=c_color, width=2
            )
            # Mega Laser do Titã (aviso ou feixe ativo)
            if b_type == "titan":
                if 120 <= self.boss.get("special_timer", 0) < 165:
                    self.canvas.create_line(
                        bx, by + 28, bx, HEIGHT, fill="#ffa502", width=2, dash=(6, 4)
                    )
                elif self.boss.get("laser_active", 0) > 0:
                    self.canvas.create_rectangle(
                        bx - 18, by + 28, bx + 18, HEIGHT, fill="#ffa502", outline="#ffffff", width=2
                    )
                    self.canvas.create_rectangle(
                        bx - 8, by + 28, bx + 8, HEIGHT, fill="#ffffff", outline=""
                    )
            # Nome e Barra de vida do Boss
            self.canvas.create_text(
                bx, by - 55, text=self.boss.get("name", "BOSS"), fill=b_color, font=("Consolas", 9, "bold")
            )
            hp_ratio = max(0, self.boss["hp"] / self.boss["max_hp"])
            self.canvas.create_rectangle(bx - 50, by - 46, bx + 50, by - 38, fill="#1f2833", outline="#ffffff")
            self.canvas.create_rectangle(
                bx - 50, by - 46, bx - 50 + int(100 * hp_ratio), by - 38, fill="#2ed573", outline=""
            )

        # Desenhar Nave do Jogador
        if self.invulnerable % 6 < 4:
            px, py = self.player_x + ox, self.player_y + oy

            # Escudo protetor
            if self.shield_active:
                self.canvas.create_oval(
                    px - 28, py - 28, px + 28, py + 28, outline="#1e90ff", width=3, dash=(4, 2)
                )

            # Chama do propulsor
            flame_h = random.randint(8, 19)
            self.canvas.create_polygon(
                px - 7,
                py + 15,
                px + 7,
                py + 15,
                px,
                py + 15 + flame_h,
                fill="#ffa502",
                outline="#ff4757",
            )
            # Corpo da Nave
            ship_color = "#2ed573" if self.rapid_fire_timer > 0 else "#66fcf1"
            self.canvas.create_polygon(
                px,
                py - 22,
                px - 20,
                py + 16,
                px - 6,
                py + 10,
                px + 6,
                py + 10,
                px + 20,
                py + 16,
                fill=ship_color,
                outline="#ffffff",
                width=2,
            )
            # Cockpit
            self.canvas.create_oval(
                px - 5, py - 6, px + 5, py + 6, fill="#0b0c10", outline="#ffffff"
            )

    def draw_hud(self):
        self.canvas.create_rectangle(0, 0, WIDTH, 48, fill="#1f2833", outline="")
        self.canvas.create_text(
            15,
            24,
            anchor="w",
            text=f"PONTOS: {self.score}  (x{self.combo})",
            fill="#66fcf1",
            font=("Consolas", 13, "bold"),
        )
        self.canvas.create_text(
            WIDTH // 2,
            24,
            anchor="center",
            text=f"NÍVEL {self.level}",
            fill="#ffffff",
            font=("Consolas", 13, "bold"),
        )
        hearts = "❤️" * self.lives + (" 🛡️" if self.shield_active else "")
        self.canvas.create_text(
            WIDTH - 15,
            24,
            anchor="e",
            text=hearts if hearts else "💀",
            fill="#ff4757",
            font=("Segoe UI Emoji", 12),
        )

        self.canvas.create_text(
            WIDTH // 2,
            HEIGHT - 12,
            anchor="center",
            text="Mover: Setas/WASD  |  Atirar: Espaço  |  Pausar: P",
            fill="#c5c6c7",
            font=("Consolas", 10),
        )

    def draw_menu(self):
        self.canvas.create_rectangle(
            65, 150, WIDTH - 65, 530, fill="#1f2833", outline="#66fcf1", width=3
        )
        self.canvas.create_text(
            WIDTH // 2,
            210,
            text="🚀 DEFENSOR ESTELAR",
            fill="#66fcf1",
            font=("Consolas", 25, "bold"),
        )
        self.canvas.create_text(
            WIDTH // 2,
            255,
            text=f"Recorde Atual: {self.high_score}",
            fill="#eccc68",
            font=("Consolas", 14, "bold"),
        )
        info = (
            "Destrua asteroides e naves-mãe!\n\n"
            "⚡ Tiro Triplo   🛡️ Escudo\n"
            "💣 Supernova     ❤️ Vida Extra\n\n"
            "Controles:\n"
            "Setas ou WASD para mover\n"
            "ESPAÇO para atirar | P para pausar"
        )
        self.canvas.create_text(
            WIDTH // 2,
            365,
            text=info,
            fill="#ffffff",
            justify="center",
            font=("Consolas", 12),
        )
        self.canvas.create_text(
            WIDTH // 2,
            485,
            text="Pressione [ESPAÇO] ou [ENTER] para Começar",
            fill="#2ed573",
            font=("Consolas", 13, "bold"),
        )

    def draw_pause(self):
        self.canvas.create_rectangle(
            140, 270, WIDTH - 140, 410, fill="#1f2833", outline="#eccc68", width=3
        )
        self.canvas.create_text(
            WIDTH // 2,
            320,
            text="JOGO PAUSADO",
            fill="#eccc68",
            font=("Consolas", 24, "bold"),
        )
        self.canvas.create_text(
            WIDTH // 2,
            365,
            text="Pressione [P] ou [ESPAÇO] para continuar",
            fill="#ffffff",
            font=("Consolas", 11),
        )

    def draw_game_over(self):
        self.canvas.create_rectangle(
            80, 210, WIDTH - 80, 460, fill="#1f2833", outline="#66fcf1", width=3
        )
        self.canvas.create_text(
            WIDTH // 2,
            265,
            text="FIM DE JOGO",
            fill="#ff4757",
            font=("Consolas", 28, "bold"),
        )
        self.canvas.create_text(
            WIDTH // 2,
            320,
            text=f"Pontuação Final: {self.score}",
            fill="#ffffff",
            font=("Consolas", 16),
        )
        self.canvas.create_text(
            WIDTH // 2,
            355,
            text=f"Recorde: {self.high_score}",
            fill="#eccc68",
            font=("Consolas", 14, "bold"),
        )
        self.canvas.create_text(
            WIDTH // 2,
            415,
            text="Pressione [ESPAÇO] ou [R] para jogar novamente",
            fill="#66fcf1",
            font=("Consolas", 11, "bold"),
        )


if __name__ == "__main__":
    root = tk.Tk()
    game = SpaceArcadeGame(root)
    root.mainloop()
