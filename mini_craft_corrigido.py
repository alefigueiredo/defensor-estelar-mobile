"""Exemplo executável, modo terminal e interface visual Tkinter para Mini-Craft.

Execute com: python mini_craft_corrigido.py
"""

import sys
import tkinter as tk


class MiniCraft:
    def __init__(self):
        self.jogador = {
            "nome": "Minerador",
            "vida": 100,
            "energia": 50,
            "posicao_x": 8,
            "posicao_y": 5,
            "nivel": 1,
        }
        self.recursos = {
            "Madeira": 4,
            "Pedra": 2,
            "Ouro": 1,
            "Moedas": 10,
        }
        self.ferramentas = ["Picareta de Madeira"]
        self.locais_mapa = [
            {
                "nome": "Floresta Inicial",
                "perigo": "Baixo",
                "recurso_principal": "Madeira",
            },
            {
                "nome": "Mina de Pedra",
                "perigo": "Médio",
                "recurso_principal": "Pedra",
            },
            {
                "nome": "Caverna Dourada",
                "perigo": "Alto",
                "recurso_principal": "Ouro",
            },
        ]
        self.inimigos = [
            {"nome": "Zumbi Lento", "dano": 15, "vida": 30, "ativo": True},
            {
                "nome": "Aranha das Cavernas",
                "dano": 25,
                "vida": 20,
                "ativo": False,
            },
        ]
        self.receitas_crafting = [
            {
                "item": "Picareta de Pedra",
                "custo": {"Madeira": 3, "Pedra": 3},
            },
            {"item": "Tocha", "custo": {"Madeira": 1, "Pedra": 1}},
        ]
        self.historico_acoes = ["Jogador iniciou a jornada"]

    def coletar(self, recurso, quantidade=1):
        """Coleta um recurso conhecido; retorna False para entrada inválida."""
        if recurso not in self.recursos or quantidade <= 0:
            return False
        self.recursos[recurso] += quantidade
        self.historico_acoes.append(f"Coletou {quantidade} {recurso}")
        return True

    def adicionar_recurso(self, recurso, quantidade=0):
        """Cria ou atualiza um recurso, inclusive com quantidade zero."""
        if not recurso or quantidade < 0:
            return False
        self.recursos[recurso] = self.recursos.get(recurso, 0) + quantidade
        self.historico_acoes.append(f"Adicionou {quantidade} {recurso} ao inventário")
        return True

    def fabricar(self, nome_item):
        """Fabrica um item apenas se houver materiais suficientes."""
        receita = next(
            (r for r in self.receitas_crafting if r["item"] == nome_item),
            None,
        )
        if receita is None or nome_item in self.ferramentas:
            return False

        custo = receita["custo"]
        if any(self.recursos.get(item, 0) < qtd for item, qtd in custo.items()):
            return False

        for item, qtd in custo.items():
            self.recursos[item] -= qtd
        self.ferramentas.append(nome_item)
        self.historico_acoes.append(f"Fabricou {nome_item}")
        return True

    def remover_ferramenta(self, nome_item):
        """Remove uma ferramenta somente se ela estiver no inventário."""
        if nome_item not in self.ferramentas:
            return False
        self.ferramentas.remove(nome_item)
        self.historico_acoes.append(f"Removeu {nome_item} do inventário")
        return True

    def derrotar_inimigo(self, nome):
        """Remove da lista o inimigo derrotado; não altera a lista se não existir."""
        for indice, inimigo in enumerate(self.inimigos):
            if inimigo["nome"] == nome:
                self.inimigos.pop(indice)
                self.historico_acoes.append(f"Derrotou {nome}")
                return True
        return False


def demonstracao():
    jogo = MiniCraft()

    print(f"Jogador: {jogo.jogador['nome']} | Vida: {jogo.jogador['vida']}")
    print(f"Recursos iniciais: {jogo.recursos}")

    print("Fabricar antes de coletar pedra:", jogo.fabricar("Picareta de Pedra"))

    jogo.coletar("Pedra")
    print("Fabricar depois de coletar pedra:", jogo.fabricar("Picareta de Pedra"))
    print(f"Ferramentas: {jogo.ferramentas}")
    print(f"Recursos após a fabricação: {jogo.recursos}")

    if "Picareta de Pedra" in jogo.ferramentas:
        print("Possui a Picareta de Pedra!")
    else:
        print("Não possui a Picareta de Pedra.")

    jogo.adicionar_recurso("Carvão")
    print(f"Carvão no inventário: {jogo.recursos['Carvão']}")
    print(f"Primeiro local: {jogo.locais_mapa[0]['nome']}")
    print(f"Ações: {jogo.historico_acoes}")


def jogar_interativo():
    jogo = MiniCraft()
    print("\n" + "=" * 55)
    print("         ⛏️  MINI-CRAFT: JORNADA DO MINERADOR  ⛏️")
    print("=" * 55)

    while jogo.jogador["vida"] > 0:
        print(
            f"\n[STATUS] {jogo.jogador['nome']} (Nível {jogo.jogador['nivel']}) | "
            f"Vida: {jogo.jogador['vida']} | Energia: {jogo.jogador['energia']}"
        )
        print(f"[RECURSOS] {jogo.recursos}")
        print(f"[FERRAMENTAS] {', '.join(jogo.ferramentas)}")
        print("-" * 55)
        print("1 - Explorar local e minerar recurso")
        print("2 - Fabricar item (Crafting)")
        print("3 - Enfrentar inimigo")
        print("4 - Descansar (+20 Energia, +10 Vida)")
        print("5 - Ver histórico de ações")
        print("0 - Sair do jogo")

        try:
            opcao = input("Escolha uma ação: ").strip()
        except EOFError:
            break

        if opcao == "1":
            if jogo.jogador["energia"] < 10:
                print("\n>> Você está sem energia! Escolha descansar primeiro.")
                continue
            print("\nLocais disponíveis:")
            for idx, loc in enumerate(jogo.locais_mapa, 1):
                print(
                    f"{idx} - {loc['nome']} (Perigo: {loc['perigo']} | "
                    f"Recurso: {loc['recurso_principal']})"
                )
            escolha_loc = input("Qual local deseja explorar? ").strip()
            if escolha_loc.isdigit() and 1 <= int(escolha_loc) <= len(jogo.locais_mapa):
                local = jogo.locais_mapa[int(escolha_loc) - 1]
                recurso = local["recurso_principal"]
                qtd = 2 if "Picareta de Pedra" in jogo.ferramentas else 1
                jogo.coletar(recurso, qtd)
                jogo.jogador["energia"] -= 10
                print(f"\n>> Você explorou {local['nome']} e coletou +{qtd} {recurso}!")
                if local["perigo"] == "Alto" and "Tocha" not in jogo.ferramentas:
                    jogo.jogador["vida"] -= 15
                    print(">> A caverna estava escura (sem Tocha)! Você perdeu 15 de vida.")
            else:
                print("\n>> Local inválido.")

        elif opcao == "2":
            print("\nReceitas disponíveis:")
            for idx, rec in enumerate(jogo.receitas_crafting, 1):
                custo_txt = ", ".join(f"{k}: {v}" for k, v in rec["custo"].items())
                status = "(Já possui)" if rec["item"] in jogo.ferramentas else f"(Custo: {custo_txt})"
                print(f"{idx} - {rec['item']} {status}")
            escolha_rec = input("Qual item deseja fabricar? ").strip()
            if escolha_rec.isdigit() and 1 <= int(escolha_rec) <= len(jogo.receitas_crafting):
                nome_item = jogo.receitas_crafting[int(escolha_rec) - 1]["item"]
                if jogo.fabricar(nome_item):
                    print(f"\n>> Sucesso! Você fabricou {nome_item}!")
                else:
                    print(f"\n>> Não foi possível fabricar {nome_item} (recursos insuficientes ou já possui).")
            else:
                print("\n>> Opção inválida.")

        elif opcao == "3":
            if not jogo.inimigos:
                print("\n>> Todos os inimigos já foram derrotados! Você limpou a região!")
                continue
            print("\nInimigos na região:")
            for idx, ini in enumerate(jogo.inimigos, 1):
                print(f"{idx} - {ini['nome']} (Dano: {ini['dano']} | Vida: {ini['vida']})")
            escolha_ini = input("Qual inimigo deseja enfrentar? ").strip()
            if escolha_ini.isdigit() and 1 <= int(escolha_ini) <= len(jogo.inimigos):
                inimigo = jogo.inimigos[int(escolha_ini) - 1]
                dano_recebido = inimigo["dano"]
                if "Picareta de Pedra" in jogo.ferramentas:
                    dano_recebido = max(5, dano_recebido - 10)
                jogo.jogador["vida"] -= dano_recebido
                jogo.derrotar_inimigo(inimigo["nome"])
                jogo.coletar("Moedas", 15)
                jogo.jogador["nivel"] += 1
                print(
                    f"\n>> Você derrotou {inimigo['nome']}! Ganhou +15 Moedas e subiu para o Nível {jogo.jogador['nivel']}!"
                )
            else:
                print("\n>> Inimigo inválido.")

        elif opcao == "4":
            jogo.jogador["energia"] = min(100, jogo.jogador["energia"] + 20)
            jogo.jogador["vida"] = min(100, jogo.jogador["vida"] + 10)
            jogo.historico_acoes.append("Descansou no acampamento")
            print("\n>> Você descansou! Energia e vida recuperadas.")

        elif opcao == "5":
            print("\n--- HISTÓRICO DE AÇÕES ---")
            for idx, acao in enumerate(jogo.historico_acoes, 1):
                print(f"{idx}. {acao}")

        elif opcao == "0":
            print("\n>> Até a próxima aventura no Mini-Craft!")
            break
        else:
            print("\n>> Opção inválida.")

    if jogo.jogador["vida"] <= 0:
        print("\n💀 FIM DE JOGO: Sua vida chegou a zero nas minas!")


class MiniCraftGUI:
    """Interface visual em Tkinter para o Mini-Craft."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("⛏️ Mini-Craft - Aventura do Minerador")
        self.root.geometry("780x620")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1c23")
        self.jogo = MiniCraft()
        self.local_atual_idx = 0

        self._criar_widgets()
        self.atualizar_tela()

    def _criar_widgets(self):
        tk.Label(
            self.root,
            text="⛏️ MINI-CRAFT: JORNADA DO MINERADOR",
            font=("Consolas", 18, "bold"),
            bg="#1a1c23",
            fg="#4ade80",
            pady=8,
        ).pack()

        self.lbl_status = tk.Label(
            self.root,
            text="",
            font=("Consolas", 12, "bold"),
            bg="#262936",
            fg="#ffffff",
            padx=16,
            pady=6,
        )
        self.lbl_status.pack(pady=4)

        self.lbl_recursos = tk.Label(
            self.root,
            text="",
            font=("Consolas", 11),
            bg="#1a1c23",
            fg="#facc15",
            pady=4,
        )
        self.lbl_recursos.pack()

        self.canvas = tk.Canvas(
            self.root, width=720, height=210, bg="#14532d", highlightthickness=2, highlightbackground="#4ade80"
        )
        self.canvas.pack(pady=6)

        painel = tk.Frame(self.root, bg="#1a1c23")
        painel.pack(pady=6)
        estilo = {"font": ("Segoe UI", 9, "bold"), "padx": 8, "pady": 5, "takefocus": False}

        tk.Button(
            painel, text="🌲 Explorar Floresta (+Madeira)", bg="#22c55e", fg="#0f172a",
            command=lambda: self.explorar(0), **estilo
        ).grid(row=0, column=0, padx=4, pady=4)
        tk.Button(
            painel, text="⛰️ Explorar Mina (+Pedra)", bg="#94a3b8", fg="#0f172a",
            command=lambda: self.explorar(1), **estilo
        ).grid(row=0, column=1, padx=4, pady=4)
        tk.Button(
            painel, text="✨ Explorar Caverna (+Ouro)", bg="#eab308", fg="#0f172a",
            command=lambda: self.explorar(2), **estilo
        ).grid(row=0, column=2, padx=4, pady=4)

        tk.Button(
            painel, text="🔨 Fabricar Picareta de Pedra (3 Mad, 3 Ped)", bg="#38bdf8", fg="#0f172a",
            command=lambda: self.fabricar("Picareta de Pedra"), **estilo
        ).grid(row=1, column=0, padx=4, pady=4)
        tk.Button(
            painel, text="🔦 Fabricar Tocha (1 Mad, 1 Ped)", bg="#fb923c", fg="#0f172a",
            command=lambda: self.fabricar("Tocha"), **estilo
        ).grid(row=1, column=1, padx=4, pady=4)
        tk.Button(
            painel, text="⚔️ Enfrentar Inimigo", bg="#ef4444", fg="#ffffff",
            command=self.lutar, **estilo
        ).grid(row=1, column=2, padx=4, pady=4)

        tk.Button(
            painel, text="⛺ Descansar (+20 Energia / +10 Vida)", bg="#a855f7", fg="#ffffff",
            command=self.descansar, **estilo
        ).grid(row=2, column=0, columnspan=2, padx=4, pady=4, sticky="ew")
        tk.Button(
            painel, text="🔄 Reiniciar Jogo", bg="#475569", fg="#ffffff",
            command=self.reiniciar, **estilo
        ).grid(row=2, column=2, padx=4, pady=4, sticky="ew")

        self.lbl_log = tk.Label(
            self.root,
            text="",
            font=("Consolas", 10),
            bg="#262936",
            fg="#e2e8f0",
            justify="left",
            anchor="nw",
            width=86,
            height=6,
            padx=10,
            pady=6,
        )
        self.lbl_log.pack(padx=16, pady=6)

    def explorar(self, idx: int):
        if self.jogo.jogador["vida"] <= 0:
            return
        if self.jogo.jogador["energia"] < 10:
            self.jogo.historico_acoes.append("⚠️ Sem energia para minerar! Descanse no acampamento.")
            self.atualizar_tela()
            return

        self.local_atual_idx = idx
        local = self.jogo.locais_mapa[idx]
        recurso = local["recurso_principal"]
        qtd = 2 if "Picareta de Pedra" in self.jogo.ferramentas else 1
        self.jogo.coletar(recurso, qtd)
        self.jogo.jogador["energia"] -= 10
        if local["perigo"] == "Alto" and "Tocha" not in self.jogo.ferramentas:
            self.jogo.jogador["vida"] = max(0, self.jogo.jogador["vida"] - 15)
            self.jogo.historico_acoes.append("🌑 Caverna escura sem Tocha! Perdeu 15 de vida.")
        self.atualizar_tela()

    def fabricar(self, item: str):
        if self.jogo.jogador["vida"] <= 0:
            return
        if not self.jogo.fabricar(item):
            self.jogo.historico_acoes.append(f"❌ Recursos insuficientes ou você já possui {item}.")
        self.atualizar_tela()

    def lutar(self):
        if self.jogo.jogador["vida"] <= 0:
            return
        if not self.jogo.inimigos:
            self.jogo.historico_acoes.append("🏆 Todos os inimigos da região já foram derrotados!")
            self.atualizar_tela()
            return
        inimigo = self.jogo.inimigos[0]
        dano = inimigo["dano"]
        if "Picareta de Pedra" in self.jogo.ferramentas:
            dano = max(5, dano - 10)
        self.jogo.jogador["vida"] = max(0, self.jogo.jogador["vida"] - dano)
        self.jogo.derrotar_inimigo(inimigo["nome"])
        self.jogo.coletar("Moedas", 15)
        self.jogo.jogador["nivel"] += 1
        self.atualizar_tela()

    def descansar(self):
        if self.jogo.jogador["vida"] <= 0:
            return
        self.jogo.jogador["energia"] = min(100, self.jogo.jogador["energia"] + 20)
        self.jogo.jogador["vida"] = min(100, self.jogo.jogador["vida"] + 10)
        self.jogo.historico_acoes.append("⛺ Descansou no acampamento (+20 Energia, +10 Vida).")
        self.atualizar_tela()

    def reiniciar(self):
        self.jogo = MiniCraft()
        self.local_atual_idx = 0
        self.atualizar_tela()

    def atualizar_tela(self):
        j = self.jogo.jogador
        self.lbl_status.config(
            text=f"👷 {j['nome']} (Nível {j['nivel']})  |  ❤️ Vida: {j['vida']}/100  |  ⚡ Energia: {j['energia']}/100  |  🛠️ {', '.join(self.jogo.ferramentas)}"
        )
        rec_txt = "   ".join(f"{k}: {v}" for k, v in self.jogo.recursos.items())
        self.lbl_recursos.config(text=f"🎒 Recursos:  {rec_txt}")
        self.lbl_log.config(text="\n".join(self.jogo.historico_acoes[-5:]))

        c = self.canvas
        c.delete("all")
        zonas = [
            (120, "🌲 Floresta Inicial\n(Madeira)", "#166534"),
            (360, "⛰️ Mina de Pedra\n(Pedra)", "#334155"),
            (600, "✨ Caverna Dourada\n(Ouro)", "#854d0e"),
        ]
        for idx, (zx, titulo, cor) in enumerate(zonas):
            borda = "#facc15" if idx == self.local_atual_idx else "#ffffff"
            larg = 3 if idx == self.local_atual_idx else 1
            c.create_rectangle(zx - 105, 20, zx + 105, 190, fill=cor, outline=borda, width=larg)
            c.create_text(zx, 50, text=titulo, fill="#ffffff", justify="center", font=("Segoe UI", 10, "bold"))

        # Desenhar Minerador na zona atual
        mx = zonas[self.local_atual_idx][0]
        c.create_oval(mx - 18, 95, mx + 18, 131, fill="#38bdf8", outline="#ffffff", width=2)
        c.create_text(mx, 148, text="⛏️ Minerador", fill="#ffffff", font=("Segoe UI", 9, "bold"))

        # Inimigos restantes
        ini_txt = ", ".join(i["nome"] for i in self.jogo.inimigos) or "Nenhum (Região Segura!)"
        c.create_text(360, 178, text=f"👾 Inimigos ativos: {ini_txt}", fill="#fca5a5", font=("Consolas", 10, "bold"))


if __name__ == "__main__":
    demonstracao()
    if "--terminal" in sys.argv or not sys.stdin.isatty():
        jogar_interativo()
    else:
        root = tk.Tk()
        app = MiniCraftGUI(root)
        root.mainloop()
