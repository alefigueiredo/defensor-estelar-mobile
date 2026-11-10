# ==============================================================================
# TRABALHO DE PROGRAMAÇÃO - JOGO GOL A GOL (1 CONTRA 1)
# ETAPA FINAL: INTEGRAÇÃO COMPLETA DO JOGO FUNCIONAL (TERMINAL + VISUAL TKINTER)
# Arquivo: jogo_gol_a_gol.py
# ==============================================================================

import random
import sys
import time
import tkinter as tk

# ------------------------------------------------------------------------------
# 1. ESTRUTURAS DE DADOS (ETAPA 04)
# ------------------------------------------------------------------------------

jogador = {
    "nome": "Craque",
    "gols": 0,
    "energia": 100,
    "bonus_precisao": 0,
    "inventario": ["Chuteira de Ouro", "Bebida Isotônica"],
}

adversario = {
    "nome": "Goleiro Paredão",
    "gols": 0,
    "forca": 7,
}

historico_partida = []
fases_torneio = ["Fase de Grupos", "Semifinal", "Grande Final"]


# ------------------------------------------------------------------------------
# 2. FUNÇÕES AUXILIARES E DE INTERFACE (MODO TERMINAL)
# ------------------------------------------------------------------------------

def exibir_cabecalho(fase_atual):
    print("=" * 60)
    print("           JOGO DE FUTEBOL: GOL A GOL (1x1)")
    print(f"           Etapa do Torneio: {fase_atual}")
    print("=" * 60)


def exibir_status(tempo_restante):
    print(f"\n[PLACAR]: {jogador['nome']} {jogador['gols']} x {adversario['gols']} {adversario['nome']}")
    print(f"[TEMPO RESTANTE]: {tempo_restante}s | [ENERGIA]: {jogador['energia']}%")
    print("-" * 60)


def usar_inventario():
    print("\n--- INVENTÁRIO DE RECURSOS ---")
    if not jogador["inventario"]:
        print("Seu inventário está vazio!")
        return

    for i, item in enumerate(jogador["inventario"], 1):
        print(f"{i}. {item}")
    print("0. Voltar sem usar")

    escolha = input("Escolha a opção: ").strip()
    if escolha == "0" or not escolha.isdigit():
        print("Voltando ao jogo...")
        return

    indice = int(escolha) - 1
    if not (0 <= indice < len(jogador["inventario"])):
        print("Opção inválida! Voltando ao jogo...")
        return

    item_escolhido = jogador["inventario"].pop(indice)
    if item_escolhido == "Chuteira de Ouro":
        jogador["bonus_precisao"] = 2
        print("\n>> Você calçou a CHUTEIRA DE OURO! Seus chutes têm +2 de precisão.")
        historico_partida.append(f"{jogador['nome']} equipou a Chuteira de Ouro.")
    elif item_escolhido == "Bebida Isotônica":
        jogador["energia"] = min(100, jogador["energia"] + 30)
        print("\n>> Você tomou a BEBIDA ISOTÔNICA e recuperou +30% de energia!")
        historico_partida.append(f"{jogador['nome']} usou Bebida Isotônica (+30% energia).")


# ------------------------------------------------------------------------------
# 3. LÓGICA DE DECISÕES E AÇÕES DO JOGO (ETAPAS 01 E 02)
# ------------------------------------------------------------------------------

def acao_chutar():
    print("\n>> Você ajeitou a bola e mandou um chutaço para o gol...")
    time.sleep(0.5)

    precisao_chute = random.randint(1, 10) + jogador.get("bonus_precisao", 0)
    jogador["energia"] -= 15

    if precisao_chute >= 7:
        print("⚽ GOOOOOOOOL! A bola foi no ângulo sem chances para o goleiro!")
        jogador["gols"] += 1
        historico_partida.append(f"Gol do {jogador['nome']} em chute no ângulo!")
    elif precisao_chute >= 4:
        print("🧤 DEFESAÇA! O goleiro espalmou a bola para escanteio!")
        historico_partida.append("Chute defendido pelo goleiro.")
    else:
        print("❌ PARA FORA! O chute saiu torto e foi direto para a linha de fundo.")
        historico_partida.append("Chute para fora.")


def acao_driblar():
    print("\n>> Você partiu para o drible no 1 contra 1...")
    time.sleep(0.5)

    agilidade_jogador = random.randint(1, 10)
    dificuldade_adversario = adversario["forca"]
    jogador["energia"] -= 10

    if agilidade_jogador > dificuldade_adversario:
        print("🔥 DRIBLE SENSACIONAL! Você deixou o marcador para trás!")
        historico_partida.append(f"{jogador['nome']} realizou um drible perfeito.")
    elif agilidade_jogador == dificuldade_adversario:
        print("⚔️ DISPUTA TRANCADA! Você passou na raça, mas perdeu velocidade.")
        historico_partida.append("Drible disputado dividida a dividida.")
    else:
        print("🛑 DESARMADO! O adversário roubou a bola com facilidade.")
        historico_partida.append("Desarme efetuado pelo adversário.")


def acao_descansar():
    print("\n>> Você cadenciou o jogo para recuperar o fôlego...")
    jogador["energia"] = min(100, jogador["energia"] + 20)
    print(f"Energia recuperada! Fôlego atual: {jogador['energia']}%")
    historico_partida.append(f"{jogador['nome']} descansou no campo.")


def turno_adversario():
    print("\n[TURNO DO ADVERSÁRIO] O adversário avança e finaliza...")
    time.sleep(0.5)

    sorteio_adv = random.randint(1, 10)
    if sorteio_adv >= 8:
        print("💥 GOL DO ADVERSÁRIO! Um chute forte no canto que balançou a rede!")
        adversario["gols"] += 1
        historico_partida.append(f"Gol do {adversario['nome']}.")
    else:
        print("🛡️ DEFESA SÓLIDA! Sua marcação travou o chute adversário.")
        historico_partida.append("Ataque do adversário defendido.")


# ------------------------------------------------------------------------------
# 4. LOOP PRINCIPAL DA PARTIDA E PRORROGAÇÃO (ETAPA 03)
# ------------------------------------------------------------------------------

def jogar_partida(fase):
    exibir_cabecalho(fase)
    tempo_restante = 180

    jogador["gols"] = 0
    adversario["gols"] = 0
    jogador["energia"] = 100
    historico_partida.clear()

    while tempo_restante > 0 and jogador["energia"] > 0:
        exibir_status(tempo_restante)

        print("Escolha sua jogada:")
        print("1. Chutar a gol")
        print("2. Driblar o marcador")
        print("3. Descansar e recuperar fôlego")
        print("4. Usar item do inventário")
        print("5. Desistir da partida")

        opcao = input("Digite o número da sua ação: ").strip()

        if opcao == "1":
            acao_chutar()
        elif opcao == "2":
            acao_driblar()
        elif opcao == "3":
            acao_descansar()
        elif opcao == "4":
            usar_inventario()
            continue
        elif opcao == "5":
            print("\n>> Você abandonou o campo! Derrota por W.O.")
            return False
        else:
            print("\n>> Opção inválida! Perdeu a vez na jogada.")

        turno_adversario()
        tempo_restante -= 30
        time.sleep(1)

    if jogador["energia"] <= 0:
        print("\n⚠️ EXAUSTÃO TOTAL! O jogador desmaiou de cansaço no campo.")
        print("❌ CONDIÇÃO DE DERROTA: Jogador sem energia suficiente!")
        return False

    print("\n================ FIM DO TEMPO REGULAMENTAR ================")
    print(f"PLACAR FINAL: {jogador['nome']} {jogador['gols']} x {adversario['gols']} {adversario['nome']}")

    if jogador["gols"] > adversario["gols"]:
        print("🎉 VITÓRIA! Você venceu no tempo regulamentar!")
        return True
    elif jogador["gols"] < adversario["gols"]:
        print("❌ DERROTA! O adversário marcou mais gols e venceu a partida.")
        return False
    else:
        print("\n⚡ EMPATE! A partida vai para a PRORROGAÇÃO (GOL DE OURO)!")
        print("Quem fizer o primeiro gol vence imediatamente!")

        prorrogacao_ativa = True
        minuto_prorrogacao = 91

        while prorrogacao_ativa:
            print(f"\n--- PRORROGAÇÃO ({minuto_prorrogacao}') --- Placar: {jogador['gols']} x {adversario['gols']}")
            print("1. Chutar a gol (Tudo ou Nada)")
            print("2. Driblar com cuidado")

            op_prorr = input("Escolha sua jogada decisiva: ").strip()

            if op_prorr == "1":
                if random.randint(1, 10) + jogador.get("bonus_precisao", 0) >= 6:
                    print("⚽ GOOOOOOOOL DE OURO! VOCÊ VENCEU A PARTIDA NA PRORROGAÇÃO!")
                    jogador["gols"] += 1
                    return True
                else:
                    print("🧤 Defendeu o goleiro! O jogo continua...")
            else:
                print("Você segurou a bola no meio de campo...")

            if random.randint(1, 10) >= 8:
                print("💥 GOL DE OURO DO ADVERSÁRIO! Você perdeu a partida na prorrogação.")
                adversario["gols"] += 1
                return False

            minuto_prorrogacao += 1
            time.sleep(1)


# ------------------------------------------------------------------------------
# 5. MENU PRINCIPAL (TERMINAL) E INTERFACE VISUAL (TKINTER)
# ------------------------------------------------------------------------------

def menu_principal():
    """Menu do jogo que roda continuamente no terminal até a escolha de sair."""
    menu_ativo = True

    while menu_ativo:
        print("\n" + "=" * 60)
        print("          🏆 CAMPEONATO DE FUTEBOL GOL A GOL 🏆")
        print("=" * 60)
        print("1. Iniciar Torneio (Modo Carreira)")
        print("2. Ver Histórico do Último Jogo")
        print("3. Instruções e Regras")
        print("4. Sair do Jogo")

        opcao_menu = input("Escolha uma opção (1-4): ").strip()

        if opcao_menu == "1":
            print("\n>> Digite o nome do seu jogador: ")
            nome_input = input("Nome: ").strip()
            if nome_input != "":
                jogador["nome"] = nome_input

            jogador["inventario"] = ["Chuteira de Ouro", "Bebida Isotônica"]
            jogador["bonus_precisao"] = 0

            venceu_torneio = True
            for fase in fases_torneio:
                resultado = jogar_partida(fase)

                if resultado:
                    print(f"\n🎉 PARABÉNS! Você avançou na etapa '{fase}'!")
                    input("Pressione ENTER para ir para a próxima etapa...")
                else:
                    print(f"\n❌ ELIMINADO! Você foi derrotado na etapa '{fase}'.")
                    venceu_torneio = False
                    break

            if venceu_torneio:
                print("\n🏆🏆🏆 CAMPEÃO! VOCÊ VENCEU A GRANDE FINAL DO GOL A GOL! 🏆🏆🏆")

        elif opcao_menu == "2":
            print("\n--- HISTÓRICO DE LANCES DA PARTIDA ---")
            if not historico_partida:
                print("Nenhuma partida jogada ainda nesta sessão.")
            else:
                for idx, lance in enumerate(historico_partida, 1):
                    print(f"{idx}. {lance}")

        elif opcao_menu == "3":
            print("\n--- REGRAS E INSTRUÇÕES ---")
            print("1. A partida dura até 3 minutos (180 segundos).")
            print("2. Cada ação consome tempo e energia do jogador.")
            print("3. Se sua energia chegar a 0%, você perde por exaustão.")
            print("4. Em caso de empate nos 3 minutos, haverá Prorrogação com Gol de Ouro.")
            print("5. Vença todas as 3 etapas para se tornar o Campeão do Torneio!")

        elif opcao_menu == "4":
            print("\n>> Obrigado por jogar Futebol Gol a Gol! Até a próxima.")
            menu_ativo = False
        else:
            print("\n>> Opção inválida! Tente novamente.")


class JogoGolAGolGUI:
    """Interface gráfica em Tkinter para o Jogo Gol a Gol (1x1)."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("⚽ Campeonato de Futebol: Gol a Gol (1x1)")
        self.root.geometry("780x640")
        self.root.resizable(False, False)
        self.root.configure(bg="#0f172a")

        self.fase_idx = 0
        self.tempo_restante = 180
        self.em_prorrogacao = False
        self.partida_ativa = False
        self.bola_pos = [370, 145]
        self.bonus_drible = 0

        self._criar_widgets()
        self.iniciar_torneio()

    def _criar_widgets(self):
        tk.Label(
            self.root,
            text="🏆 CAMPEONATO DE FUTEBOL: GOL A GOL (1x1)",
            font=("Segoe UI", 18, "bold"),
            bg="#0f172a",
            fg="#38bdf8",
            pady=8,
        ).pack()

        self.lbl_fase = tk.Label(
            self.root,
            text="Etapa: Fase de Grupos",
            font=("Segoe UI", 12, "bold"),
            bg="#0f172a",
            fg="#facc15",
        )
        self.lbl_fase.pack()

        self.lbl_placar = tk.Label(
            self.root,
            text="",
            font=("Consolas", 15, "bold"),
            bg="#1e293b",
            fg="#ffffff",
            padx=20,
            pady=6,
        )
        self.lbl_placar.pack(pady=6)

        self.canvas = tk.Canvas(
            self.root, width=720, height=250, bg="#15803d", highlightthickness=2, highlightbackground="#ffffff"
        )
        self.canvas.pack(pady=6)

        painel_acoes = tk.Frame(self.root, bg="#0f172a")
        painel_acoes.pack(pady=8)

        estilo_btn = {"font": ("Segoe UI", 10, "bold"), "padx": 10, "pady": 5, "takefocus": False}
        self.btn_chutar = tk.Button(
            painel_acoes, text="⚽ Chutar a Gol (-15% Energia)", bg="#22c55e", fg="#0f172a",
            command=self.jogada_chutar, **estilo_btn
        )
        self.btn_chutar.grid(row=0, column=0, padx=5, pady=4)

        self.btn_driblar = tk.Button(
            painel_acoes, text="🔥 Driblar (-10% Energia)", bg="#38bdf8", fg="#0f172a",
            command=self.jogada_driblar, **estilo_btn
        )
        self.btn_driblar.grid(row=0, column=1, padx=5, pady=4)

        self.btn_descansar = tk.Button(
            painel_acoes, text="💤 Descansar (+20% Energia)", bg="#eab308", fg="#0f172a",
            command=self.jogada_descansar, **estilo_btn
        )
        self.btn_descansar.grid(row=0, column=2, padx=5, pady=4)

        self.btn_chuteira = tk.Button(
            painel_acoes, text="👟 Usar Chuteira de Ouro", bg="#a855f7", fg="#ffffff",
            command=lambda: self.usar_item("Chuteira de Ouro"), **estilo_btn
        )
        self.btn_chuteira.grid(row=1, column=0, padx=5, pady=4)

        self.btn_bebida = tk.Button(
            painel_acoes, text="🥤 Usar Bebida Isotônica", bg="#ec4899", fg="#ffffff",
            command=lambda: self.usar_item("Bebida Isotônica"), **estilo_btn
        )
        self.btn_bebida.grid(row=1, column=1, padx=5, pady=4)

        self.btn_novo = tk.Button(
            painel_acoes, text="🔄 Reiniciar Torneio", bg="#64748b", fg="#ffffff",
            command=self.iniciar_torneio, **estilo_btn
        )
        self.btn_novo.grid(row=1, column=2, padx=5, pady=4)

        self.lbl_narracao = tk.Label(
            self.root,
            text="",
            font=("Consolas", 10),
            bg="#1e293b",
            fg="#e2e8f0",
            justify="left",
            anchor="nw",
            width=86,
            height=7,
            padx=12,
            pady=8,
        )
        self.lbl_narracao.pack(padx=20, pady=6)

    def registrar(self, texto: str):
        historico_partida.append(texto)
        self.lbl_narracao.config(text="\n".join(historico_partida[-6:]))

    def iniciar_torneio(self):
        self.fase_idx = 0
        jogador["inventario"] = ["Chuteira de Ouro", "Bebida Isotônica"]
        jogador["bonus_precisao"] = 0
        self.iniciar_etapa()

    def iniciar_etapa(self):
        jogador["gols"] = 0
        adversario["gols"] = 0
        jogador["energia"] = 100
        self.tempo_restante = 180
        self.em_prorrogacao = False
        self.partida_ativa = True
        self.bonus_drible = 0
        self.bola_pos = [360, 125]
        historico_partida.clear()
        fase = fases_torneio[self.fase_idx]
        self.registrar(f"▶️ Início da etapa: {fase}! Escolha sua jogada.")
        self.atualizar_interface()

    def usar_item(self, item: str):
        if not self.partida_ativa or item not in jogador["inventario"]:
            return
        jogador["inventario"].remove(item)
        if item == "Chuteira de Ouro":
            jogador["bonus_precisao"] = 2
            self.registrar("👟 Você calçou a Chuteira de Ouro! (+2 de precisão nos chutes)")
        elif item == "Bebida Isotônica":
            jogador["energia"] = min(100, jogador["energia"] + 30)
            self.registrar("🥤 Você tomou a Bebida Isotônica e recuperou +30% de energia!")
        self.atualizar_interface()

    def jogada_chutar(self):
        if not self.partida_ativa:
            return
        jogador["energia"] -= 15
        precisao = random.randint(1, 10) + jogador.get("bonus_precisao", 0) + self.bonus_drible
        self.bonus_drible = 0

        if precisao >= 7:
            jogador["gols"] += 1
            self.bola_pos = [675, random.randint(85, 165)]
            self.registrar(f"⚽ GOOOOOOOOL de {jogador['nome']}! Chute certeiro no ângulo!")
        elif precisao >= 4:
            self.bola_pos = [630, 125]
            self.registrar("🧤 DEFESAÇA! O Goleiro Paredão espalmou para escanteio!")
        else:
            self.bola_pos = [690, 35]
            self.registrar("❌ PARA FORA! O chute subiu demais.")

        self._pos_jogada_jogador()

    def jogada_driblar(self):
        if not self.partida_ativa:
            return
        jogador["energia"] -= 10
        agilidade = random.randint(1, 10)
        if agilidade > adversario["forca"]:
            self.bonus_drible = 2
            self.bola_pos = [520, 125]
            self.registrar("🔥 DRIBLE SENSACIONAL! Próximo chute terá +2 de precisão!")
        elif agilidade == adversario["forca"]:
            self.bonus_drible = 1
            self.bola_pos = [450, 125]
            self.registrar("⚔️ Disputa acirrada! Você ganhou espaço (+1 precisão no próximo chute).")
        else:
            self.bonus_drible = 0
            self.bola_pos = [260, 125]
            self.registrar("🛑 DESARMADO! O adversário roubou a bola.")

        self._pos_jogada_jogador()

    def jogada_descansar(self):
        if not self.partida_ativa:
            return
        jogador["energia"] = min(100, jogador["energia"] + 20)
        self.bola_pos = [360, 125]
        self.registrar(f"💤 Você cadenciou o jogo. Energia atual: {jogador['energia']}%.")
        self._pos_jogada_jogador()

    def _pos_jogada_jogador(self):
        if self.em_prorrogacao and jogador["gols"] > adversario["gols"]:
            self._vencer_etapa("⚽ GOL DE OURO! Vitória na prorrogação!")
            return

        # Turno do adversário
        if random.randint(1, 10) >= 8:
            adversario["gols"] += 1
            self.bola_pos = [45, 125]
            self.registrar(f"💥 GOL DO ADVERSÁRIO! {adversario['nome']} marcou no contra-ataque!")
        else:
            self.registrar("🛡️ Defesa sólida! Você travou o contra-ataque adversário.")

        if self.em_prorrogacao and adversario["gols"] > jogador["gols"]:
            self.partida_ativa = False
            self.registrar("❌ Gol de Ouro do adversário! Fim de torneio.")
            self.atualizar_interface()
            return

        if not self.em_prorrogacao:
            self.tempo_restante = max(0, self.tempo_restante - 30)

        if jogador["energia"] <= 0:
            self.partida_ativa = False
            self.registrar("⚠️ EXAUSTÃO TOTAL! Sua energia chegou a 0%. Você perdeu a partida!")
        elif not self.em_prorrogacao and self.tempo_restante <= 0:
            if jogador["gols"] > adversario["gols"]:
                self._vencer_etapa("🎉 Fim do tempo regulamentar! Você venceu a partida!")
            elif jogador["gols"] < adversario["gols"]:
                self.partida_ativa = False
                self.registrar("❌ Fim de jogo! O adversário venceu no tempo regulamentar.")
            else:
                self.em_prorrogacao = True
                self.registrar("⚡ EMPATE! PRORROGAÇÃO (GOL DE OURO): quem marcar primeiro vence!")

        self.atualizar_interface()

    def _vencer_etapa(self, msg: str):
        self.registrar(msg)
        if self.fase_idx + 1 < len(fases_torneio):
            self.fase_idx += 1
            self.registrar(f"🏆 Avançando para: {fases_torneio[self.fase_idx]}!")
            self.root.after(1200, self.iniciar_etapa)
        else:
            self.partida_ativa = False
            self.registrar("🏆🏆🏆 CAMPEÃO! VOCÊ VENCEU TODAS AS ETAPAS DO TORNEIO! 🏆🏆🏆")
        self.atualizar_interface()

    def atualizar_interface(self):
        fase = fases_torneio[self.fase_idx]
        tempo_str = "GOL DE OURO" if self.em_prorrogacao else f"{self.tempo_restante}s"
        self.lbl_fase.config(text=f"Etapa {self.fase_idx + 1}/3: {fase}")
        self.lbl_placar.config(
            text=f"{jogador['nome']} {jogador['gols']}  x  {adversario['gols']} {adversario['nome']}   |   ⏱️ {tempo_str}   |   ⚡ Energia: {max(0, jogador['energia'])}%"
        )

        estado_btn = "normal" if self.partida_ativa else "disabled"
        self.btn_chutar.config(state=estado_btn)
        self.btn_driblar.config(state=estado_btn)
        self.btn_descansar.config(state=estado_btn)
        self.btn_chuteira.config(
            state="normal" if (self.partida_ativa and "Chuteira de Ouro" in jogador["inventario"]) else "disabled"
        )
        self.btn_bebida.config(
            state="normal" if (self.partida_ativa and "Bebida Isotônica" in jogador["inventario"]) else "disabled"
        )

        self._desenhar_campo()

    def _desenhar_campo(self):
        c = self.canvas
        c.delete("all")
        # Gramado e linhas
        for i in range(0, 720, 60):
            cor = "#16a34a" if (i // 60) % 2 == 0 else "#15803d"
            c.create_rectangle(i, 0, i + 60, 250, fill=cor, outline="")
        c.create_rectangle(20, 15, 700, 235, outline="#ffffff", width=2)
        c.create_line(360, 15, 360, 235, fill="#ffffff", width=2)
        c.create_oval(310, 75, 410, 175, outline="#ffffff", width=2)
        # Áreas e traves
        c.create_rectangle(20, 65, 95, 185, outline="#ffffff", width=2)
        c.create_rectangle(625, 65, 700, 185, outline="#ffffff", width=2)
        c.create_rectangle(8, 90, 20, 160, fill="#e2e8f0", outline="#ffffff")
        c.create_rectangle(700, 90, 712, 160, fill="#e2e8f0", outline="#ffffff")

        # Jogador (Azul) e Goleiro Adversário (Vermelho)
        c.create_oval(215, 110, 245, 140, fill="#38bdf8", outline="#ffffff", width=2)
        c.create_text(230, 155, text=jogador["nome"], fill="#ffffff", font=("Segoe UI", 9, "bold"))

        c.create_oval(640, 110, 670, 140, fill="#ef4444", outline="#ffffff", width=2)
        c.create_text(655, 155, text=adversario["nome"], fill="#ffffff", font=("Segoe UI", 9, "bold"))

        # Bola
        bx, by = self.bola_pos
        c.create_oval(bx - 9, by - 9, bx + 9, by + 9, fill="#ffffff", outline="#0f172a", width=2)


if __name__ == "__main__":
    if "--terminal" in sys.argv or not sys.stdin.isatty():
        menu_principal()
    else:
        root = tk.Tk()
        app = JogoGolAGolGUI(root)
        root.mainloop()
