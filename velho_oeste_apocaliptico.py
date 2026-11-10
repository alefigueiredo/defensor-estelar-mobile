"""Velho Oeste Apocalíptico - Modo Terminal e Interface Visual Tkinter."""

import sys
import tkinter as tk

jogador = {
    "nome": "Sam",
    "vida": 3,
    "local": "entrada da cidade",
}

inventario = {
    "cantis": 0,
    "municao": 4,
    "bandagens": 0,
}

ambiente = {
    "turno": 0,
    "limite_turnos": 8,
    "clima": "tempestade",
}

itens = {
    "cantis": "um cantil de água",
    "municao": "munição",
    "bandagens": "uma bandagem",
}

locais = [
    {
        "nome": "Saloon",
        "recompensa": "cantis",
        "ameaca": "bandido",
        "explorado": False,
    },
    {
        "nome": "Estação",
        "recompensa": "municao",
        "ameaca": None,
        "explorado": False,
    },
    {
        "nome": "Armazém",
        "recompensa": "cantis",
        "ameaca": "criatura",
        "explorado": False,
    },
    {
        "nome": "Poço",
        "recompensa": "cantis",
        "ameaca": None,
        "explorado": False,
    },
    {
        "nome": "Clínica",
        "recompensa": "bandagens",
        "ameaca": "bandido",
        "explorado": False,
    },
    {
        "nome": "Igreja",
        "recompensa": "cantis",
        "ameaca": None,
        "explorado": False,
    },
]

venceu = False


def jogar_terminal():
    global venceu
    print("VELHO OESTE APOCALÍPTICO")
    print("Encontre 3 cantis de água e chegue ao forte antes do fim dos turnos.")

    while (
        jogador["vida"] > 0
        and not venceu
        and ambiente["turno"] < ambiente["limite_turnos"]
    ):
        print("\nTurno:", ambiente["turno"], "/", ambiente["limite_turnos"])
        print("Vida:", jogador["vida"])
        print("Cantis:", inventario["cantis"])
        print("Munição:", inventario["municao"])
        print("Bandagens:", inventario["bandagens"])
        print("Clima:", ambiente["clima"])

        print("\n1 - Explorar um local")
        print("2 - Usar uma bandagem")
        print("3 - Ir ao forte")
        escolha = input("Escolha uma ação: ").strip()

        if escolha == "1":
            locais_disponiveis = []

            print("\nLocais ainda não explorados:")
            for local in locais:
                if not local["explorado"]:
                    locais_disponiveis.append(local)
                    print(len(locais_disponiveis), "-", local["nome"])

            if len(locais_disponiveis) == 0:
                print("Todos os locais já foram explorados.")
            else:
                numero_local = input("Qual local deseja explorar? ").strip()

                if numero_local.isdigit():
                    numero_local = int(numero_local)

                    if 1 <= numero_local <= len(locais_disponiveis):
                        local_escolhido = locais_disponiveis[numero_local - 1]
                        local_escolhido["explorado"] = True
                        jogador["local"] = local_escolhido["nome"]
                        ambiente["turno"] += 1

                        print("\nVocê explorou:", local_escolhido["nome"])
                        recompensa = local_escolhido["recompensa"]

                        if recompensa is not None:
                            inventario[recompensa] += 1
                            print("Você encontrou", itens[recompensa] + ".")

                        ameaca = local_escolhido["ameaca"]

                        if ameaca is not None:
                            print("Uma ameaça apareceu:", ameaca)

                            if inventario["municao"] > 0:
                                print("1 - Defender-se usando uma munição")
                                print("2 - Não se defender e perder vida")
                                resposta = input("Escolha: ").strip()

                                while resposta != "1" and resposta != "2":
                                    resposta = input("Digite 1 ou 2: ").strip()

                                if resposta == "1":
                                    inventario["municao"] -= 1
                                    print("Você se defendeu e gastou uma munição.")
                                else:
                                    jogador["vida"] -= 1
                                    print("Você foi atingido e perdeu um ponto de vida.")
                            else:
                                jogador["vida"] -= 1
                                print("Sem munição para se defender: você perdeu um ponto de vida.")
                    else:
                        print("Esse número não corresponde a um local.")
                else:
                    print("Digite o número de um local.")

        elif escolha == "2":
            if inventario["bandagens"] == 0:
                print("Você não tem bandagens.")
            elif jogador["vida"] >= 3:
                print("Você não precisa usar uma bandagem agora.")
            else:
                inventario["bandagens"] -= 1
                jogador["vida"] += 1
                ambiente["turno"] += 1
                print("Você usou uma bandagem e recuperou um ponto de vida.")

        elif escolha == "3":
            if inventario["cantis"] >= 3:
                ambiente["turno"] += 1
                jogador["local"] = "forte"
                venceu = True
                print("Você chegou ao forte com água suficiente!")
            else:
                faltam = 3 - inventario["cantis"]
                print("Ainda faltam", faltam, "cantil(is) de água para poder ir ao forte.")

        else:
            print("Opção inválida. Escolha 1, 2 ou 3.")

    if venceu:
        print("\nVITÓRIA! Você sobreviveu à jornada.")
    elif jogador["vida"] <= 0:
        print("\nFIM DE JOGO. Você ficou sem pontos de vida.")
    else:
        print("\nFIM DE JOGO. Os turnos acabaram antes de você chegar ao forte.")

    try:
        input("\nPressione ENTER para sair...")
    except EOFError:
        pass


class VelhoOesteGUI:
    """Interface visual em Tkinter para Velho Oeste Apocalíptico."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🤠 Velho Oeste Apocalíptico")
        self.root.geometry("800x630")
        self.root.resizable(False, False)
        self.root.configure(bg="#271c15")

        self.historico = []
        self._criar_widgets()
        self.reiniciar()

    def _criar_widgets(self):
        tk.Label(
            self.root,
            text="🤠 VELHO OESTE APOCALÍPTICO",
            font=("Georgia", 20, "bold"),
            bg="#271c15",
            fg="#f59e0b",
            pady=8,
        ).pack()

        self.lbl_status = tk.Label(
            self.root,
            text="",
            font=("Consolas", 12, "bold"),
            bg="#3f2e21",
            fg="#fef3c7",
            padx=16,
            pady=6,
        )
        self.lbl_status.pack(pady=4)

        self.canvas = tk.Canvas(
            self.root, width=740, height=220, bg="#78350f", highlightthickness=2, highlightbackground="#f59e0b"
        )
        self.canvas.pack(pady=6)

        self.frame_locais = tk.Frame(self.root, bg="#271c15")
        self.frame_locais.pack(pady=6)

        self.botoes_locais = []
        estilo = {"font": ("Segoe UI", 9, "bold"), "padx": 10, "pady": 5, "takefocus": False}
        for idx, loc in enumerate(locais):
            btn = tk.Button(
                self.frame_locais,
                text=f"🏚️ Explorar {loc['nome']}",
                bg="#d97706",
                fg="#ffffff",
                command=lambda i=idx: self.explorar_local(i),
                **estilo,
            )
            btn.grid(row=idx // 3, column=idx % 3, padx=5, pady=4, sticky="ew")
            self.botoes_locais.append(btn)

        frame_acoes = tk.Frame(self.root, bg="#271c15")
        frame_acoes.pack(pady=4)

        self.btn_bandagem = tk.Button(
            frame_acoes, text="🩹 Usar Bandagem (+1 Vida)", bg="#16a34a", fg="#ffffff",
            command=self.usar_bandagem, **estilo
        )
        self.btn_bandagem.grid(row=0, column=0, padx=5, pady=4)

        self.btn_forte = tk.Button(
            frame_acoes, text="🏰 Ir ao Forte (Requer 3 Cantis)", bg="#2563eb", fg="#ffffff",
            command=self.ir_ao_forte, **estilo
        )
        self.btn_forte.grid(row=0, column=1, padx=5, pady=4)

        tk.Button(
            frame_acoes, text="🔄 Nova Jornada", bg="#57534e", fg="#ffffff",
            command=self.reiniciar, **estilo
        ).grid(row=0, column=2, padx=5, pady=4)

        self.lbl_log = tk.Label(
            self.root,
            text="",
            font=("Consolas", 10),
            bg="#3f2e21",
            fg="#fde68a",
            justify="left",
            anchor="nw",
            width=88,
            height=6,
            padx=12,
            pady=8,
        )
        self.lbl_log.pack(padx=16, pady=6)

    def registrar(self, msg: str):
        self.historico.append(msg)
        self.lbl_log.config(text="\n".join(self.historico[-5:]))

    def reiniciar(self):
        global venceu
        venceu = False
        jogador["vida"] = 3
        jogador["local"] = "entrada da cidade"
        inventario["cantis"] = 0
        inventario["municao"] = 4
        inventario["bandagens"] = 0
        ambiente["turno"] = 0
        for loc in locais:
            loc["explorado"] = False
        self.historico.clear()
        self.registrar("🌵 Encontre 3 cantis de água e chegue ao Forte antes do turno 8!")
        self.atualizar_tela()

    def jogo_ativo(self) -> bool:
        return jogador["vida"] > 0 and not venceu and ambiente["turno"] < ambiente["limite_turnos"]

    def explorar_local(self, idx: int):
        if not self.jogo_ativo():
            return
        local = locais[idx]
        if local["explorado"]:
            return

        local["explorado"] = True
        jogador["local"] = local["nome"]
        ambiente["turno"] += 1

        recompensa = local["recompensa"]
        if recompensa:
            inventario[recompensa] += 1
            self.registrar(f"📍 Explorou {local['nome']} e encontrou {itens[recompensa]}!")

        ameaca = local["ameaca"]
        if ameaca:
            if inventario["municao"] > 0:
                inventario["municao"] -= 1
                self.registrar(f"🔫 Ameaça ({ameaca}) apareceu! Você se defendeu usando 1 munição.")
            else:
                jogador["vida"] -= 1
                self.registrar(f"💥 Ameaça ({ameaca}) apareceu! Sem munição, você perdeu 1 de vida!")

        self.verificar_fim()
        self.atualizar_tela()

    def usar_bandagem(self):
        if not self.jogo_ativo():
            return
        if inventario["bandagens"] <= 0:
            self.registrar("⚠️ Você não tem bandagens no inventário.")
        elif jogador["vida"] >= 3:
            self.registrar("ℹ️ Sua vida já está cheia (3/3).")
        else:
            inventario["bandagens"] -= 1
            jogador["vida"] += 1
            ambiente["turno"] += 1
            self.registrar("🩹 Você usou uma bandagem e recuperou +1 ponto de vida!")
            self.verificar_fim()
        self.atualizar_tela()

    def ir_ao_forte(self):
        global venceu
        if not self.jogo_ativo():
            return
        if inventario["cantis"] >= 3:
            ambiente["turno"] += 1
            jogador["local"] = "Forte"
            venceu = True
            self.registrar("🏆 VITÓRIA! Você chegou ao Forte com água suficiente e sobreviveu!")
        else:
            faltam = 3 - inventario["cantis"]
            self.registrar(f"🚫 Ainda faltam {faltam} cantil(is) de água para viajar ao Forte!")
        self.verificar_fim()
        self.atualizar_tela()

    def verificar_fim(self):
        if venceu:
            return
        if jogador["vida"] <= 0:
            self.registrar("💀 FIM DE JOGO: Você ficou sem pontos de vida.")
        elif ambiente["turno"] >= ambiente["limite_turnos"]:
            self.registrar("⏳ FIM DE JOGO: A tempestade chegou e os turnos acabaram!")

    def atualizar_tela(self):
        ativo = self.jogo_ativo()
        self.lbl_status.config(
            text=(
                f"⏳ Turno: {ambiente['turno']}/{ambiente['limite_turnos']}  |  "
                f"❤️ Vida: {jogador['vida']}  |  💧 Cantis: {inventario['cantis']}/3  |  "
                f"🔫 Munição: {inventario['municao']}  |  🩹 Bandagens: {inventario['bandagens']}"
            )
        )

        for idx, btn in enumerate(self.botoes_locais):
            explorado = locais[idx]["explorado"]
            btn.config(
                state="normal" if (ativo and not explorado) else "disabled",
                bg="#78716c" if explorado else "#d97706",
            )

        self.btn_bandagem.config(state="normal" if (ativo and inventario["bandagens"] > 0 and jogador["vida"] < 3) else "disabled")
        self.btn_forte.config(state="normal" if ativo else "disabled")

        c = self.canvas
        c.delete("all")
        coords = [
            (95, 65), (255, 65), (415, 65),
            (95, 155), (255, 155), (415, 155),
        ]
        for idx, loc in enumerate(locais):
            lx, ly = coords[idx]
            cor = "#57534e" if loc["explorado"] else "#b45309"
            borda = "#facc15" if jogador["local"] == loc["nome"] else "#fde68a"
            c.create_rectangle(lx - 65, ly - 32, lx + 65, ly + 32, fill=cor, outline=borda, width=2)
            status = "✓" if loc["explorado"] else "?"
            c.create_text(lx, ly, text=f"{loc['nome']} [{status}]", fill="#ffffff", font=("Segoe UI", 9, "bold"))

        # Forte à direita
        cor_forte = "#16a34a" if venceu else "#1d4ed8"
        c.create_rectangle(560, 45, 710, 175, fill=cor_forte, outline="#ffffff", width=3)
        c.create_text(635, 110, text="🏰 FORTE\n(Meta: 3 Cantis)", fill="#ffffff", justify="center", font=("Segoe UI", 10, "bold"))


if __name__ == "__main__":
    if "--terminal" in sys.argv or not sys.stdin.isatty():
        jogar_terminal()
    else:
        root = tk.Tk()
        app = VelhoOesteGUI(root)
        root.mainloop()
