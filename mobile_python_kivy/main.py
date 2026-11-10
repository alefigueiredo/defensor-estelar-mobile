"""Defensor Estelar - Versão Mobile 100% Python (Kivy) para compilação em APK Android via Buildozer."""

import math
import random
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, Quad, Triangle, Rectangle
from kivy.uix.label import Label
from kivy.uix.widget import Widget

# Em desktop simula proporção mobile vertical
Window.size = (420, 740)


class SpaceArcadeKivyWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state = "MENU"  # MENU, PLAYING, GAMEOVER
        self.high_score = 0
        self.stars = [
            {
                "rx": random.random(),
                "ry": random.random(),
                "size": random.choice([2, 3, 4]),
                "speed": random.uniform(0.002, 0.006),
            }
            for _ in range(70)
        ]

        self.hud_label = Label(
            text="TOQUE NA TELA PARA COMEÇAR",
            font_size="18sp",
            bold=True,
            pos_hint={"center_x": 0.5, "top": 0.98},
            size_hint=(1, 0.08),
        )
        self.add_widget(self.hud_label)

        self.center_label = Label(
            text="🚀 DEFENSOR ESTELAR MOBILE\n\nArraste o dedo para mover e atirar!\n\n[ TOQUE PARA JOGAR ]",
            halign="center",
            valign="middle",
            font_size="18sp",
            bold=True,
        )
        self.add_widget(self.center_label)

        self.reset_game()
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def reset_game(self):
        self.player_rx = 0.5
        self.player_ry = 0.14
        self.lives = 3
        self.score = 0
        self.combo = 1
        self.combo_timer = 0
        self.level = 1
        self.shoot_cooldown = 0
        self.invulnerable = 0
        self.shield_active = False
        self.rapid_fire_timer = 0
        self.spawn_timer = 0
        self.touch_active = False

        self.bullets = []
        self.enemy_bullets = []
        self.asteroids = []
        self.particles = []
        self.powerups = []
        self.boss = None
        self.boss_count = 0
        self.next_boss_score = 300

    def on_touch_down(self, touch):
        if self.state in ("MENU", "GAMEOVER"):
            self.reset_game()
            self.state = "PLAYING"
            self.center_label.text = ""
        self.touch_active = True
        self._move_to_touch(touch)
        return True

    def on_touch_move(self, touch):
        if self.state == "PLAYING":
            self._move_to_touch(touch)
        return True

    def on_touch_up(self, _touch):
        self.touch_active = False
        return True

    def _move_to_touch(self, touch):
        if self.width > 0 and self.height > 0:
            target_rx = touch.x / self.width
            target_ry = (touch.y + 45) / self.height
            self.player_rx = max(0.06, min(0.94, target_rx))
            self.player_ry = max(0.08, min(0.88, target_ry))

    def spawn_explosion(self, x, y, rgb=(1.0, 0.4, 0.4), count=14):
        for _ in range(count):
            ang = random.uniform(0, 2 * math.pi)
            spd = random.uniform(2.0, 7.0)
            self.particles.append(
                {
                    "x": x,
                    "y": y,
                    "vx": math.cos(ang) * spd,
                    "vy": math.sin(ang) * spd,
                    "life": random.randint(14, 28),
                    "rgb": rgb,
                }
            )

    def damage_player(self):
        if self.invulnerable > 0:
            return
        px, py = self.player_rx * self.width, self.player_ry * self.height
        if self.shield_active:
            self.shield_active = False
            self.invulnerable = 45
            self.spawn_explosion(px, py, (0.12, 0.56, 1.0), 20)
            return

        self.lives -= 1
        self.combo = 1
        self.invulnerable = 65
        self.spawn_explosion(px, py, (0.4, 0.98, 0.94), 25)
        if self.lives <= 0:
            self.state = "GAMEOVER"
            self.center_label.text = (
                f"FIM DE JOGO\n\nPontos: {self.score}\nRecorde: {self.high_score}\n\n"
                "[ TOQUE PARA JOGAR NOVAMENTE ]"
            )

    def update(self, _dt):
        w, h = max(1, self.width), max(1, self.height)
        self.center_label.center = (w * 0.5, h * 0.5)
        self.hud_label.pos = (0, h - 50)
        self.hud_label.size = (w, 45)

        if self.state == "PLAYING":
            self.update_gameplay(w, h)

        self.draw_scene(w, h)

    def update_gameplay(self, w, h):
        px, py = self.player_rx * w, self.player_ry * h

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

        max_cd = 5 if self.rapid_fire_timer > 0 else 10
        if self.touch_active and self.shoot_cooldown == 0:
            if self.rapid_fire_timer > 0:
                self.bullets.append({"x": px - 12, "y": py + 20, "vx": -0.6})
                self.bullets.append({"x": px, "y": py + 24, "vx": 0.0})
                self.bullets.append({"x": px + 12, "y": py + 20, "vx": 0.6})
            else:
                self.bullets.append({"x": px, "y": py + 22, "vx": 0.0})
            self.shoot_cooldown = max_cd

        for b in self.bullets[:]:
            b["y"] += 13
            b["x"] += b["vx"]
            if b["y"] > h + 20:
                self.bullets.remove(b)

        for eb in self.enemy_bullets[:]:
            eb["x"] += eb["vx"]
            eb["y"] += eb["vy"]
            if eb["y"] < -20 or eb["x"] < -20 or eb["x"] > w + 20:
                self.enemy_bullets.remove(eb)
                continue
            if math.hypot(eb["x"] - px, eb["y"] - py) < 18:
                self.enemy_bullets.remove(eb)
                self.damage_player()

        self.level = 1 + (self.score // 250)
        if self.boss is None and self.score >= self.next_boss_score:
            boss_configs = [
                ("NAVE-MÃE ESCARLATE", (1.0, 0.28, 0.34), 3, 1.0),
                ("CRUZADOR FANTASMA", (0.65, 0.37, 0.92), 4, 1.25),
                ("ENCOURAÇADO TITÃ", (1.0, 0.65, 0.01), 5, 1.6),
            ]
            name, rgb, shots, mult = boss_configs[self.boss_count % len(boss_configs)]
            max_hp = int((20 + self.level * 10) * mult)
            self.boss = {
                "x": w * 0.5,
                "y": h - 95,
                "vx": 3.8,
                "hp": max_hp,
                "max_hp": max_hp,
                "timer": 0,
                "name": name,
                "rgb": rgb,
                "shots": shots,
            }
            self.boss_count += 1

        if self.boss:
            boss = self.boss
            boss["x"] += boss["vx"]
            if boss["x"] < 65 or boss["x"] > w - 65:
                boss["vx"] *= -1
            boss["timer"] += 1
            if boss["timer"] >= max(24, 52 - self.level * 3):
                boss["timer"] = 0
                base_ang = math.atan2(py - boss["y"], px - boss["x"])
                spread = boss["shots"]
                for i in range(spread):
                    offset = (i - (spread - 1) / 2.0) * 0.28
                    ang = base_ang + offset
                    self.enemy_bullets.append(
                        {
                            "x": boss["x"],
                            "y": boss["y"] - 25,
                            "vx": math.cos(ang) * 5.5,
                            "vy": math.sin(ang) * 5.5,
                            "rgb": boss["rgb"],
                        }
                    )

            for b in self.bullets[:]:
                if abs(b["x"] - boss["x"]) < 52 and abs(b["y"] - boss["y"]) < 30:
                    self.bullets.remove(b)
                    boss["hp"] -= 1
                    self.spawn_explosion(b["x"], b["y"], boss["rgb"], 4)
                    if boss["hp"] <= 0:
                        bx, by = boss["x"], boss["y"]
                        self.spawn_explosion(bx, by, boss["rgb"], 40)
                        self.boss = None
                        self.score += 120 * self.combo
                        self.high_score = max(self.high_score, self.score)
                        self.next_boss_score = self.score + 500 + self.level * 150
                        self.powerups.append(
                            {
                                "x": bx,
                                "y": by,
                                "kind": random.choice(["rapid", "shield", "bomb", "heart"]),
                            }
                        )
                        break

        self.spawn_timer += 1
        spawn_rate = max(14, 42 - self.level * 3)
        if self.boss:
            spawn_rate *= 2
        if self.spawn_timer >= spawn_rate:
            self.spawn_timer = 0
            r = random.randint(14, 26)
            self.asteroids.append(
                {
                    "x": random.randint(r, int(w - r)),
                    "y": h + r,
                    "r": r,
                    "speed": random.uniform(2.6, 4.4 + self.level * 0.35),
                    "vx": random.uniform(-1.2, 1.2),
                    "rgb": random.choice(
                        [(1.0, 0.28, 0.34), (1.0, 0.65, 0.01), (0.92, 0.8, 0.4)]
                    ),
                }
            )

        for a in self.asteroids[:]:
            a["y"] -= a["speed"]
            a["x"] += a["vx"]
            if a["x"] - a["r"] < 0 or a["x"] + a["r"] > w:
                a["vx"] *= -1
            if a["y"] + a["r"] < 0:
                self.asteroids.remove(a)
                continue

            hit = False
            for b in self.bullets[:]:
                if math.hypot(a["x"] - b["x"], a["y"] - b["y"]) < a["r"] + 6:
                    self.bullets.remove(b)
                    self.asteroids.remove(a)
                    self.score += 10 * self.combo
                    self.combo = min(8, self.combo + 1)
                    self.combo_timer = 140
                    self.high_score = max(self.high_score, self.score)
                    self.spawn_explosion(a["x"], a["y"], a["rgb"], 12)
                    if random.random() < 0.16:
                        self.powerups.append(
                            {
                                "x": a["x"],
                                "y": a["y"],
                                "kind": random.choice(["rapid", "shield", "bomb", "heart"]),
                            }
                        )
                    hit = True
                    break
            if hit:
                continue

            if math.hypot(a["x"] - px, a["y"] - py) < a["r"] + 16:
                self.asteroids.remove(a)
                self.damage_player()

        for pw in self.powerups[:]:
            pw["y"] -= 2.8
            if pw["y"] < -20:
                self.powerups.remove(pw)
                continue
            if math.hypot(pw["x"] - px, pw["y"] - py) < 26:
                self.powerups.remove(pw)
                k = pw["kind"]
                if k == "rapid":
                    self.rapid_fire_timer = 320
                elif k == "shield":
                    self.shield_active = True
                elif k == "heart":
                    self.lives = min(5, self.lives + 1)
                elif k == "bomb":
                    for ast in self.asteroids:
                        self.spawn_explosion(ast["x"], ast["y"], ast["rgb"], 8)
                        self.score += 10
                    self.asteroids.clear()
                    self.enemy_bullets.clear()

        self.hud_label.text = (
            f"PONTOS: {self.score} (x{self.combo})   |   NÍVEL {self.level}   |   VIDAS: {self.lives}"
        )

    def draw_scene(self, w, h):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.04, 0.05, 0.06, 1)
            Rectangle(pos=(0, 0), size=(w, h))

            # Estrelas
            Color(0.4, 0.98, 0.94, 0.85)
            for s in self.stars:
                s["ry"] -= s["speed"]
                if s["ry"] < 0:
                    s["ry"] = 1.0
                    s["rx"] = random.random()
                Ellipse(pos=(s["rx"] * w, s["ry"] * h), size=(s["size"], s["size"]))

            # Partículas
            for p in self.particles[:]:
                p["x"] += p["vx"]
                p["y"] += p["vy"]
                p["life"] -= 1
                if p["life"] <= 0:
                    self.particles.remove(p)
                else:
                    Color(*p["rgb"], 1)
                    Ellipse(pos=(p["x"] - 3, p["y"] - 3), size=(6, 6))

            if self.state == "PLAYING":
                # Powerups
                Color(0.18, 0.84, 0.45, 1)
                for pw in self.powerups:
                    Ellipse(pos=(pw["x"] - 11, pw["y"] - 11), size=(22, 22))

                # Lasers do jogador
                Color(0.18, 0.84, 0.45, 1) if self.rapid_fire_timer > 0 else Color(
                    0.4, 0.98, 0.94, 1
                )
                for b in self.bullets:
                    Rectangle(pos=(b["x"] - 2, b["y"] - 6), size=(4, 14))

                # Tiros inimigos
                for eb in self.enemy_bullets:
                    Color(*eb["rgb"], 1)
                    Ellipse(pos=(eb["x"] - 5, eb["y"] - 5), size=(10, 10))

                # Asteroides
                for a in self.asteroids:
                    Color(*a["rgb"], 1)
                    r = a["r"]
                    Ellipse(pos=(a["x"] - r, a["y"] - r), size=(r * 2, r * 2))

                # Boss
                if self.boss:
                    bx, by = self.boss["x"], self.boss["y"]
                    Color(*self.boss["rgb"], 1)
                    Triangle(points=[bx - 55, by + 15, bx + 55, by + 15, bx, by - 28])
                    hp_ratio = max(0.0, self.boss["hp"] / self.boss["max_hp"])
                    Color(0.18, 0.84, 0.45, 1)
                    Rectangle(pos=(bx - 45, by + 24), size=(90 * hp_ratio, 7))

                # Nave do Jogador
                if self.invulnerable % 6 < 4:
                    px, py = self.player_rx * w, self.player_ry * h
                    if self.shield_active:
                        Color(0.12, 0.56, 1.0, 0.9)
                        Line(circle=(px, py, 28), width=2)
                    Color(1.0, 0.65, 0.01, 1)
                    Triangle(points=[px - 7, py - 14, px + 7, py - 14, px, py - 28])
                    Color(0.18, 0.84, 0.45, 1) if self.rapid_fire_timer > 0 else Color(
                        0.4, 0.98, 0.94, 1
                    )
                    Triangle(points=[px - 20, py - 14, px + 20, py - 14, px, py + 22])


class DefensorEstelarMobileApp(App):
    def build(self):
        self.title = "Defensor Estelar Mobile"
        return SpaceArcadeKivyWidget()


if __name__ == "__main__":
    DefensorEstelarMobileApp().run()

