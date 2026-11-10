"""Jogo local de corrida com poderes, feito com Tkinter e Python basico."""

import random
import tkinter as tk
from tkinter import ttk

try:
    from decisoes_corrida import (
        decidir_coleta_de_item,
        decidir_efeito_do_ataque,
        decidir_situacao_da_corrida,
        decidir_uso_de_item,
    )
except ImportError:
    def decidir_uso_de_item(item):
        if not item or item not in ITENS:
            return "Item indisponivel para uso."
        return f"Usar item: {item}."

    def decidir_efeito_do_ataque(item, escudo_ativo):
        if escudo_ativo:
            return "bloqueou o ataque com o escudo!"
        if item == "banana":
            return "escorregou na banana e perdeu 15 de avanco."
        if item == "pedra":
            return "foi atingido por uma pedra (-10 avanco e -1 resistencia)."
        if item == "correntes":
            return "foi preso por correntes e ficou sem usar itens neste turno."
        return "ataque desconhecido, sem efeito."

    def decidir_coleta_de_item(passou_por_caixa, quantidade_itens, limite_inventario):
        if not passou_por_caixa:
            return "Nao coletar: nenhuma caixa alcancada."
        if quantidade_itens >= limite_inventario:
            return "Nao coletar: inventario cheio."
        return "Coletar novo item da caixa."

    def decidir_situacao_da_corrida(resistencia, posicao, distancia_chegada):
        if resistencia <= 0:
            return "Derrota: carro ficou sem resistencia."
        if posicao >= distancia_chegada:
            return "Vitoria: cruzou a linha de chegada!"
        return "Continua na disputa."


DISTANCIA_CHEGADA = 300
LIMITE_INVENTARIO = 2
AVANCO_BASE = 30
LARGURA_PISTA = 900
ALTURA_PISTA = 250
MARGEM_PISTA = 70

ITENS = {
    "turbo": {"tipo": "bonus", "descricao": "avanca 25 unidades extras"},
    "poder_especial": {
        "tipo": "bonus",
        "descricao": "avanca 40 unidades extras",
    },
    "escudo": {"tipo": "defesa", "descricao": "bloqueia um ataque ou obstaculo"},
    "banana": {"tipo": "ataque", "descricao": "reduz o avanco em 15"},
    "pedra": {"tipo": "ataque", "descricao": "reduz o avanco e a resistencia"},
    "correntes": {"tipo": "ataque", "descricao": "bloqueia o uso de itens"},
}


def criar_corredor(nome, cor, itens_iniciais):
    """Cria um dicionario com o estado inicial de um corredor."""
    return {
        "nome": nome,
        "cor": cor,
        "posicao": 0,
        "resistencia": 3,
        "inventario": itens_iniciais[:],
        "escudo": False,
        "itens_bloqueados": False,
        "efeitos_pendentes": [],
        "caixas_coletadas": [],
        "obstaculos_vistos": [],
    }


class JogoCorrida:
    def __init__(self, janela):
        self.janela = janela
        self.janela.title("Corrida de Carros com Poderes")
        self.janela.geometry("1000x740")
        self.janela.minsize(900, 680)
        self.janela.configure(bg="#101820")

        self.corrida = {}
        self.historico = []
        self.status_var = tk.StringVar(value="Prepare-se para a largada!")
        self.item_var = tk.StringVar()
        self.inventario_var = tk.StringVar(value="Itens: -")
        self.jogador_var = tk.StringVar(value="JOGADOR  |  Resistência: -")
        self.rival_var = tk.StringVar(value="RIVAL  |  Resistência: -")

        self._criar_interface()
        self.iniciar_corrida()

    def _criar_interface(self):
        titulo = tk.Label(
            self.janela,
            text="CORRIDA DE CARROS COM PODERES",
            font=("Segoe UI", 22, "bold"),
            bg="#101820",
            fg="#f2aa4c",
            pady=12,
        )
        titulo.pack()

        self.status_label = tk.Label(
            self.janela,
            textvariable=self.status_var,
            font=("Segoe UI", 12, "bold"),
            bg="#101820",
            fg="#ffffff",
            pady=4,
        )
        self.status_label.pack()

        self.pista = tk.Canvas(
            self.janela,
            width=LARGURA_PISTA,
            height=ALTURA_PISTA,
            bg="#d9e8d0",
            highlightthickness=0,
        )
        self.pista.pack(padx=18, pady=10, fill="x")

        painel_status = tk.Frame(self.janela, bg="#101820")
        painel_status.pack(fill="x", padx=35, pady=3)

        tk.Label(
            painel_status,
            textvariable=self.jogador_var,
            font=("Segoe UI", 11, "bold"),
            bg="#101820",
            fg="#64c8ff",
        ).pack(side="left", padx=12)

        tk.Label(
            painel_status,
            textvariable=self.rival_var,
            font=("Segoe UI", 11, "bold"),
            bg="#101820",
            fg="#ff8078",
        ).pack(side="right", padx=12)

        tk.Label(
            self.janela,
            textvariable=self.inventario_var,
            font=("Segoe UI", 10),
            bg="#101820",
            fg="#dce4ec",
            pady=5,
        ).pack()

        controles = tk.Frame(self.janela, bg="#101820")
        controles.pack(pady=8)

        self.iniciar_botao = ttk.Button(
            controles, text="Nova corrida", command=self.iniciar_corrida
        )
        self.iniciar_botao.grid(row=0, column=0, padx=6, pady=4)

        self.acelerar_botao = ttk.Button(
            controles,
            text="Acelerar",
            command=lambda: self._jogar_turno("acelerar"),
        )
        self.acelerar_botao.grid(row=0, column=1, padx=6, pady=4)

        self.item_seletor = ttk.Combobox(
            controles,
            textvariable=self.item_var,
            state="readonly",
            width=14,
            values=(),
        )
        self.item_seletor.grid(row=0, column=2, padx=6, pady=4)

        self.item_botao = ttk.Button(
            controles,
            text="Usar item",
            command=self._usar_item_selecionado,
        )
        self.item_botao.grid(row=0, column=3, padx=6, pady=4)

        tk.Label(
            self.janela,
            text="Relato da corrida",
            font=("Segoe UI", 11, "bold"),
            bg="#101820",
            fg="#f2aa4c",
            anchor="w",
        ).pack(fill="x", padx=35, pady=(8, 2))

        self.relato_label = tk.Label(
            self.janela,
            text="Clique em Nova corrida para comecar.",
            font=("Segoe UI", 10),
            bg="#1c2b36",
            fg="#e8eef2",
            justify="left",
            anchor="nw",
            padx=12,
            pady=8,
            height=7,
            wraplength=920,
        )
        self.relato_label.pack(fill="x", padx=28, pady=(0, 12))

        tk.Label(
            self.janela,
            text=(
                "Acelere ou use um item por turno. Itens de ataque atingem "
                "o rival no turno seguinte."
            ),
            font=("Segoe UI", 9),
            bg="#101820",
            fg="#aab8c2",
        ).pack(pady=(0, 10))

    def iniciar_corrida(self):
        """Prepara os corredores, os obstaculos e as caixas da nova partida."""
        self.historico = []
        self.corrida = {
            "ativa": True,
            "rodada": 0,
            "corredores": [
                criar_corredor("Voce", "#168bd2", ["turbo", "banana"]),
                criar_corredor("Rival", "#e4564f", ["turbo", "correntes"]),
            ],
            "obstaculos": [
                {"id": 1, "posicao": 105},
                {"id": 2, "posicao": 215},
            ],
            "caixas": [
                {"id": 1, "posicao": 65},
                {"id": 2, "posicao": 145},
                {"id": 3, "posicao": 235},
            ],
        }
        self.status_var.set("Corrida iniciada! Escolha sua acao.")
        self._registrar("Largada! Voce comeca com turbo e banana.")
        self._atualizar_tela()

    def _usar_item_selecionado(self):
        item = self.item_var.get()
        if not item:
            self.status_var.set("Escolha um item do inventario primeiro.")
            return
        self._jogar_turno(item)

    def _jogar_turno(self, acao_jogador):
        """Executa um turno completo quando o jogador escolhe uma acao."""
        if not self.corrida.get("ativa"):
            self.status_var.set("Inicie uma nova corrida para jogar.")
            return

        jogador, rival = self.corrida["corredores"]
        self.corrida["rodada"] += 1
        rodada = self.corrida["rodada"]
        self._registrar("Turno " + str(rodada) + ".")

        jogador["itens_bloqueados"] = False
        rival["itens_bloqueados"] = False
        penalidades = {}

        for corredor in self.corrida["corredores"]:
            penalidades[corredor["nome"]] = self._resolver_efeitos_pendentes(
                corredor
            )

        if jogador["resistencia"] <= 0:
            self._encerrar_corrida("derrota", "Seu carro ficou sem resistencia.")
            return
        if rival["resistencia"] <= 0:
            self._encerrar_corrida("vitoria", "O carro rival ficou sem resistencia.")
            return

        jogador["bonus_avanco"] = 0
        rival["bonus_avanco"] = 0

        if jogador["itens_bloqueados"] and acao_jogador != "acelerar":
            self._registrar("Correntes impediram voce de usar um item.")
            acao_jogador = "acelerar"

        if acao_jogador != "acelerar":
            if acao_jogador not in jogador["inventario"]:
                self.status_var.set("Esse item nao esta mais no inventario.")
                self._atualizar_tela()
                return
            self._aplicar_item(jogador, rival, acao_jogador)

        acao_rival = self._escolher_acao_rival(rival)
        if acao_rival:
            self._aplicar_item(rival, jogador, acao_rival)

        posicoes_anteriores = {
            corredor["nome"]: corredor["posicao"]
            for corredor in self.corrida["corredores"]
        }

        for corredor in self.corrida["corredores"]:
            penalidade = penalidades[corredor["nome"]]
            avanco = AVANCO_BASE + corredor["bonus_avanco"] - penalidade
            if avanco < 0:
                avanco = 0
            corredor["posicao"] += avanco
            self._registrar(
                corredor["nome"]
                + " avancou "
                + str(avanco)
                + " unidades."
            )

        for corredor in self.corrida["corredores"]:
            self._verificar_obstaculos(
                corredor, posicoes_anteriores[corredor["nome"]]
            )
            self._verificar_caixas(
                corredor, posicoes_anteriores[corredor["nome"]]
            )

        self._verificar_fim_da_corrida()
        if self.corrida["ativa"]:
            self.status_var.set("Turno " + str(rodada) + " concluido.")
        self._atualizar_tela()

    def _aplicar_item(self, usuario, alvo, item):
        """Consome um item e aplica seu efeito ou prepara um ataque."""
        decisao = decidir_uso_de_item(item)
        if decisao.startswith("Item indisponivel"):
            self._registrar(decisao)
            return

        usuario["inventario"].remove(item)
        if item == "turbo":
            usuario["bonus_avanco"] += 25
            self._registrar(usuario["nome"] + " ativou o turbo!")
        elif item == "poder_especial":
            usuario["bonus_avanco"] += 40
            self._registrar(usuario["nome"] + " usou o poder especial!")
        elif item == "escudo":
            usuario["escudo"] = True
            self._registrar(usuario["nome"] + " ativou o escudo.")
        elif item in ("banana", "pedra", "correntes"):
            alvo["efeitos_pendentes"].append(item)
            self._registrar(
                usuario["nome"]
                + " soltou "
                + item
                + " contra "
                + alvo["nome"]
                + "."
            )

    def _escolher_acao_rival(self, rival):
        """Escolhe uma acao simples para o rival, sem inteligencia artificial."""
        if rival["itens_bloqueados"] or not rival["inventario"]:
            return None

        if random.random() < 0.4:
            return random.choice(rival["inventario"])
        return None

    def _resolver_efeitos_pendentes(self, corredor):
        """Resolve ataques recebidos e retorna a penalidade de avanco."""
        penalidade = 0
        efeitos = corredor["efeitos_pendentes"]

        while efeitos:
            item = efeitos.pop(0)
            mensagem = decidir_efeito_do_ataque(item, corredor["escudo"])

            if corredor["escudo"]:
                corredor["escudo"] = False
                self._registrar(corredor["nome"] + ": " + mensagem)
            elif item == "banana":
                penalidade += 15
                self._registrar(corredor["nome"] + ": " + mensagem)
            elif item == "pedra":
                penalidade += 10
                corredor["resistencia"] -= 1
                self._registrar(corredor["nome"] + ": " + mensagem)
            elif item == "correntes":
                corredor["itens_bloqueados"] = True
                self._registrar(corredor["nome"] + ": " + mensagem)
            else:
                self._registrar(
                    corredor["nome"] + ": ataque desconhecido, sem efeito."
                )

        return penalidade

    def _verificar_obstaculos(self, corredor, posicao_anterior):
        """Aplica o efeito de cada obstaculo que o carro atravessou."""
        for obstaculo in self.corrida["obstaculos"]:
            id_obstaculo = obstaculo["id"]
            cruzou = (
                posicao_anterior < obstaculo["posicao"]
                <= corredor["posicao"]
            )
            if cruzou and id_obstaculo not in corredor["obstaculos_vistos"]:
                corredor["obstaculos_vistos"].append(id_obstaculo)
                if corredor["escudo"]:
                    corredor["escudo"] = False
                    self._registrar(
                        corredor["nome"] + " bloqueou um obstaculo com escudo."
                    )
                else:
                    corredor["resistencia"] -= 1
                    corredor["posicao"] = max(
                        posicao_anterior, corredor["posicao"] - 15
                    )
                    self._registrar(
                        corredor["nome"]
                        + " atingiu um obstaculo: -1 resistencia e -15 avanco."
                    )

    def _verificar_caixas(self, corredor, posicao_anterior):
        """Entrega itens ao cruzar caixas, respeitando o limite do inventario."""
        for caixa in self.corrida["caixas"]:
            id_caixa = caixa["id"]
            cruzou = posicao_anterior < caixa["posicao"] <= corredor["posicao"]
            if cruzou and id_caixa not in corredor["caixas_coletadas"]:
                corredor["caixas_coletadas"].append(id_caixa)
                decisao = decidir_coleta_de_item(
                    True, len(corredor["inventario"]), LIMITE_INVENTARIO
                )
                if decisao.startswith("Coletar"):
                    item = random.choice(list(ITENS.keys()))
                    corredor["inventario"].append(item)
                    self._registrar(
                        corredor["nome"] + " encontrou uma caixa: " + item + "."
                    )
                else:
                    self._registrar(
                        corredor["nome"] + " encontrou uma caixa, "
                        "mas o inventario esta cheio."
                    )

    def _verificar_fim_da_corrida(self):
        """Determina a derrota, a vitoria ou se a corrida continua."""
        jogador, rival = self.corrida["corredores"]
        situacao_jogador = decidir_situacao_da_corrida(
            jogador["resistencia"],
            jogador["posicao"],
            DISTANCIA_CHEGADA,
        )

        if situacao_jogador.startswith("Derrota"):
            self._encerrar_corrida("derrota", "Seu carro ficou sem resistencia.")
        elif rival["resistencia"] <= 0:
            self._encerrar_corrida("vitoria", "O rival foi eliminado da corrida.")
        elif (
            jogador["posicao"] >= DISTANCIA_CHEGADA
            and rival["posicao"] >= DISTANCIA_CHEGADA
        ):
            if jogador["posicao"] >= rival["posicao"]:
                self._encerrar_corrida("vitoria", "Voce cruzou a chegada primeiro!")
            else:
                self._encerrar_corrida("derrota", "O rival cruzou a chegada primeiro.")
        elif jogador["posicao"] >= DISTANCIA_CHEGADA:
            self._encerrar_corrida("vitoria", "Voce cruzou a linha de chegada!")
        elif rival["posicao"] >= DISTANCIA_CHEGADA:
            self._encerrar_corrida("derrota", "O rival chegou antes de voce.")

    def _encerrar_corrida(self, resultado, mensagem):
        self.corrida["ativa"] = False
        if resultado == "vitoria":
            self.status_var.set("VITORIA! " + mensagem)
        else:
            self.status_var.set("FIM DE JOGO. " + mensagem)
        self._registrar(mensagem)

    def _registrar(self, mensagem):
        self.historico.append(mensagem)
        self.relato_label.configure(
            text="\n".join(self.historico[-7:])
        )

    def _atualizar_tela(self):
        """Atualiza a pista, os indicadores e os controles."""
        ativa = self.corrida.get("ativa", False)
        self.acelerar_botao.configure(
            state="normal" if ativa else "disabled"
        )

        jogador = None
        rival = None
        if self.corrida.get("corredores"):
            jogador, rival = self.corrida["corredores"]
            valores = jogador["inventario"][:]
            self.item_seletor.configure(values=valores)
            if self.item_var.get() not in valores:
                self.item_var.set(valores[0] if valores else "")
            item_habilitado = ativa and bool(valores) and not jogador[
                "itens_bloqueados"
            ]
            self.item_botao.configure(
                state="normal" if item_habilitado else "disabled"
            )
            self.inventario_var.set(
                "Seus itens: "
                + (", ".join(jogador["inventario"]) or "nenhum")
            )
            self.jogador_var.set(
                "VOCE  |  Resistencia: "
                + str(max(0, jogador["resistencia"]))
                + "  |  Posicao: "
                + str(jogador["posicao"])
            )
            self.rival_var.set(
                "RIVAL  |  Resistencia: "
                + str(max(0, rival["resistencia"]))
                + "  |  Posicao: "
                + str(rival["posicao"])
            )
        else:
            self.item_seletor.configure(values=())
            self.item_var.set("")
            self.item_botao.configure(state="disabled")
            self.inventario_var.set("Itens: -")
            self.jogador_var.set("JOGADOR  |  Resistência: -")
            self.rival_var.set("RIVAL  |  Resistência: -")

        self._desenhar_pista(jogador, rival)

    def _desenhar_pista(self, jogador, rival):
        """Desenha a pista, os itens, os obstaculos e os carros no canvas."""
        canvas = self.pista
        canvas.delete("all")
        esquerda = MARGEM_PISTA
        direita = LARGURA_PISTA - MARGEM_PISTA
        largura_util = direita - esquerda

        canvas.create_rectangle(
            esquerda, 38, direita, 210, fill="#50565c", outline=""
        )
        canvas.create_line(
            esquerda, 124, direita, 124, fill="#f3f0d7", dash=(12, 8), width=2
        )
        canvas.create_text(
            esquerda, 20, text="LARGADA", fill="#263238", anchor="w",
            font=("Segoe UI", 9, "bold")
        )
        canvas.create_text(
            direita, 20, text="CHEGADA", fill="#263238", anchor="e",
            font=("Segoe UI", 9, "bold")
        )

        marca = 50
        while marca < DISTANCIA_CHEGADA:
            x = esquerda + largura_util * marca / DISTANCIA_CHEGADA
            canvas.create_line(x, 38, x, 210, fill="#777d82", dash=(3, 5))
            canvas.create_text(
                x, 222, text=str(marca), fill="#263238",
                font=("Segoe UI", 8)
            )
            marca += 50

        x_chegada = direita - 5
        canvas.create_line(
            x_chegada, 38, x_chegada, 210, fill="#ffffff", width=5
        )

        if self.corrida.get("caixas"):
            for caixa in self.corrida["caixas"]:
                x = esquerda + largura_util * caixa["posicao"] / DISTANCIA_CHEGADA
                canvas.create_rectangle(
                    x - 8, 111, x + 8, 127,
                    fill="#f2aa4c", outline="#fff4d6", width=2
                )
                canvas.create_text(
                    x, 100, text="?", fill="#263238",
                    font=("Segoe UI", 10, "bold")
                )

            for obstaculo in self.corrida["obstaculos"]:
                x = esquerda + largura_util * obstaculo["posicao"] / DISTANCIA_CHEGADA
                canvas.create_polygon(
                    x, 122, x - 8, 105, x - 16, 122,
                    fill="#e4564f", outline="#ffffff"
                )

        if jogador is not None and rival is not None:
            for corredor, y in ((jogador, 82), (rival, 162)):
                posicao = min(corredor["posicao"], DISTANCIA_CHEGADA)
                x = esquerda + largura_util * posicao / DISTANCIA_CHEGADA
                x = min(x, direita - 22)
                self._desenhar_carro(canvas, x, y, corredor["cor"])

    @staticmethod
    def _desenhar_carro(canvas, x, y, cor):
        """Desenha um carro simples usando formas do Tkinter Canvas."""
        canvas.create_rectangle(
            x - 20, y - 10, x + 20, y + 8, fill=cor, outline="#17232b", width=2
        )
        canvas.create_polygon(
            x - 10, y - 10, x - 5, y - 18, x + 10, y - 18,
            x + 16, y - 10, fill=cor, outline="#17232b"
        )
        canvas.create_oval(
            x - 14, y + 4, x - 5, y + 14, fill="#17232b", outline=""
        )
        canvas.create_oval(
            x + 7, y + 4, x + 16, y + 14, fill="#17232b", outline=""
        )


def main():
    janela = tk.Tk()
    JogoCorrida(janela)
    janela.mainloop()


if __name__ == "__main__":
    main()
