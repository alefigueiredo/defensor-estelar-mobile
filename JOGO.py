import time
import tkinter as tk


LARGURA = 800
ALTURA = 540
RAIO_BOLA = 8
LARGURA_PLATAFORMA = 110
ALTURA_PLATAFORMA = 14
VELOCIDADE_PLATAFORMA = 7
VELOCIDADE_BOLA_X = 4
VELOCIDADE_BOLA_Y = -5
INTERVALO = 1 / 60


def criar_estado():
    """Cria os dados da partida sem iniciar a interface."""
    return {
        "aberto": True,
        "ativo": False,
        "lancada": False,
        "jogador": {
            "nome": "Jogador 1",
            "vidas": 3,
            "pontuacao": 0,
        },
        "recursos": {"fichas": 0},
        "fases": [
            {"nome": "Salão Neon", "linhas": 4, "pontos": 10},
            {"nome": "Galeria Pixel", "linhas": 5, "pontos": 20},
        ],
        "fase_atual": 0,
        "blocos": [],
        "recordes": [],
        "teclas": set(),
        "plataforma_x": LARGURA / 2,
        "bola_x": LARGURA / 2,
        "bola_y": ALTURA - 60,
        "bola_dx": VELOCIDADE_BOLA_X,
        "bola_dy": VELOCIDADE_BOLA_Y,
        "plataforma_id": None,
        "bola_id": None,
        "mensagem": "Pressione Jogar para começar.",
    }


def desenhar_menu(canvas):
    canvas.delete("all")
    canvas.create_text(
        LARGURA / 2,
        150,
        text="REBATEDOR RETRÔ",
        fill="#ffe66d",
        font=("Courier", 30, "bold"),
    )
    canvas.create_text(
        LARGURA / 2,
        220,
        text="Rebata a bola e destrua todos os blocos!",
        fill="#f3f0e8",
        font=("Courier", 15),
    )
    canvas.create_text(
        LARGURA / 2,
        280,
        text="Setas ou A/D: mover   |   ESPAÇO: lançar",
        fill="#50e3c2",
        font=("Courier", 13),
    )
    canvas.create_text(
        LARGURA / 2,
        340,
        text="Você tem 3 vidas. Complete as duas fases para vencer.",
        fill="#f3f0e8",
        font=("Courier", 12),
    )


def criar_blocos(jogo, canvas):
    """Cria a lista de blocos da fase atual e desenha cada um."""
    fase = jogo["fases"][jogo["fase_atual"]]
    jogo["blocos"] = []

    cores = ["#ff5c8a", "#ff9f43", "#ffe66d", "#50e3c2", "#a78bfa"]
    colunas = 8
    largura_bloco = 82
    altura_bloco = 22
    espacamento = 10
    inicio_x = 39
    inicio_y = 65

    for linha in range(fase["linhas"]):
        for coluna in range(colunas):
            x = inicio_x + coluna * (largura_bloco + espacamento)
            y = inicio_y + linha * (altura_bloco + 9)
            bloco_id = canvas.create_rectangle(
                x,
                y,
                x + largura_bloco,
                y + altura_bloco,
                fill=cores[linha % len(cores)],
                outline="#171526",
                width=2,
            )
            jogo["blocos"].append(
                {
                    "id": bloco_id,
                    "x1": x,
                    "y1": y,
                    "x2": x + largura_bloco,
                    "y2": y + altura_bloco,
                    "pontos": fase["pontos"],
                }
            )


def posicionar_bola_na_plataforma(jogo):
    jogo["plataforma_x"] = LARGURA / 2
    jogo["bola_x"] = jogo["plataforma_x"]
    jogo["bola_y"] = ALTURA - 60
    jogo["bola_dx"] = VELOCIDADE_BOLA_X
    jogo["bola_dy"] = VELOCIDADE_BOLA_Y
    jogo["lancada"] = False


def iniciar_partida(jogo, canvas, pontuacao_var, vidas_var, fase_var, mensagem_var):
    jogo["jogador"]["vidas"] = 3
    jogo["jogador"]["pontuacao"] = 0
    jogo["recursos"]["fichas"] = 0
    jogo["fase_atual"] = 0
    jogo["ativo"] = True
    jogo["teclas"].clear()
    posicionar_bola_na_plataforma(jogo)

    canvas.delete("all")
    criar_blocos(jogo, canvas)
    jogo["plataforma_id"] = canvas.create_rectangle(
        0,
        0,
        0,
        0,
        fill="#50e3c2",
        outline="",
    )
    jogo["bola_id"] = canvas.create_oval(
        0,
        0,
        0,
        0,
        fill="#ffffff",
        outline="#ffe66d",
        width=2,
    )
    atualizar_desenho(jogo, canvas)
    pontuacao_var.set("Pontos: 0")
    vidas_var.set("Vidas: 3")
    fase_var.set("Fase: " + jogo["fases"][0]["nome"])
    mensagem_var.set("Pressione ESPAÇO para lançar a bola.")
    canvas.focus_set()


def atualizar_desenho(jogo, canvas):
    """Desenha a plataforma e a bola nas posições atuais."""
    metade_plataforma = LARGURA_PLATAFORMA / 2
    topo_plataforma = ALTURA - 40
    canvas.coords(
        jogo["plataforma_id"],
        jogo["plataforma_x"] - metade_plataforma,
        topo_plataforma,
        jogo["plataforma_x"] + metade_plataforma,
        topo_plataforma + ALTURA_PLATAFORMA,
    )
    canvas.coords(
        jogo["bola_id"],
        jogo["bola_x"] - RAIO_BOLA,
        jogo["bola_y"] - RAIO_BOLA,
        jogo["bola_x"] + RAIO_BOLA,
        jogo["bola_y"] + RAIO_BOLA,
    )


def encerrar_partida(jogo, mensagem, mensagem_var):
    jogo["ativo"] = False
    jogo["recordes"].append(
        {
            "jogador": jogo["jogador"]["nome"],
            "pontuacao": jogo["jogador"]["pontuacao"],
        }
    )
    mensagem_var.set(mensagem)


def mover_plataforma(jogo):
    teclas_norm = {t.lower() for t in jogo["teclas"]}
    esquerda = "left" in teclas_norm or "a" in teclas_norm
    direita = "right" in teclas_norm or "d" in teclas_norm

    if esquerda and not direita:
        jogo["plataforma_x"] -= VELOCIDADE_PLATAFORMA
    elif direita and not esquerda:
        jogo["plataforma_x"] += VELOCIDADE_PLATAFORMA
    else:
        pass

    metade_plataforma = LARGURA_PLATAFORMA / 2
    if jogo["plataforma_x"] < metade_plataforma:
        jogo["plataforma_x"] = metade_plataforma
    elif jogo["plataforma_x"] > LARGURA - metade_plataforma:
        jogo["plataforma_x"] = LARGURA - metade_plataforma

    if not jogo["lancada"]:
        jogo["bola_x"] = jogo["plataforma_x"]


def atualizar_bola(jogo, canvas, pontuacao_var, vidas_var, fase_var, mensagem_var):
    """Avança a bola e verifica paredes, plataforma, blocos e vidas."""
    if not jogo["lancada"]:
        return

    jogo["bola_x"] += jogo["bola_dx"]
    jogo["bola_y"] += jogo["bola_dy"]

    if jogo["bola_x"] - RAIO_BOLA <= 0:
        jogo["bola_x"] = RAIO_BOLA
        jogo["bola_dx"] = abs(jogo["bola_dx"])
    elif jogo["bola_x"] + RAIO_BOLA >= LARGURA:
        jogo["bola_x"] = LARGURA - RAIO_BOLA
        jogo["bola_dx"] = -abs(jogo["bola_dx"])

    if jogo["bola_y"] - RAIO_BOLA <= 0:
        jogo["bola_y"] = RAIO_BOLA
        jogo["bola_dy"] = abs(jogo["bola_dy"])

    topo_plataforma = ALTURA - 40
    if (
        jogo["bola_dy"] > 0
        and jogo["bola_y"] + RAIO_BOLA >= topo_plataforma
        and jogo["bola_y"] - RAIO_BOLA <= topo_plataforma + ALTURA_PLATAFORMA
        and abs(jogo["bola_x"] - jogo["plataforma_x"]) <= LARGURA_PLATAFORMA / 2
    ):
        distancia = (jogo["bola_x"] - jogo["plataforma_x"]) / (LARGURA_PLATAFORMA / 2)
        jogo["bola_y"] = topo_plataforma - RAIO_BOLA
        jogo["bola_dx"] = distancia * 5
        jogo["bola_dy"] = -5

    bloco_atingido = None
    bola_esquerda = jogo["bola_x"] - RAIO_BOLA
    bola_direita = jogo["bola_x"] + RAIO_BOLA
    bola_topo = jogo["bola_y"] - RAIO_BOLA
    bola_base = jogo["bola_y"] + RAIO_BOLA

    for bloco in jogo["blocos"]:
        if (
            bola_direita >= bloco["x1"]
            and bola_esquerda <= bloco["x2"]
            and bola_base >= bloco["y1"]
            and bola_topo <= bloco["y2"]
        ):
            bloco_atingido = bloco
            break

    if bloco_atingido is not None:
        jogo["blocos"].remove(bloco_atingido)
        canvas.delete(bloco_atingido["id"])
        jogo["jogador"]["pontuacao"] += bloco_atingido["pontos"]
        jogo["bola_dy"] *= -1
        pontuacao_var.set("Pontos: " + str(jogo["jogador"]["pontuacao"]))

        if not jogo["blocos"]:
            if jogo["fase_atual"] + 1 < len(jogo["fases"]):
                jogo["fase_atual"] += 1
                criar_blocos(jogo, canvas)
                posicionar_bola_na_plataforma(jogo)
                fase_var.set("Fase: " + jogo["fases"][jogo["fase_atual"]]["nome"])
                mensagem_var.set("Fase concluída! Pressione ESPAÇO para continuar.")
            else:
                encerrar_partida(jogo, "Você venceu! Destruiu todos os blocos!", mensagem_var)
                return

    if jogo["bola_y"] - RAIO_BOLA > ALTURA:
        jogo["jogador"]["vidas"] -= 1
        vidas_var.set("Vidas: " + str(jogo["jogador"]["vidas"]))

        if jogo["jogador"]["vidas"] <= 0:
            encerrar_partida(jogo, "Fim de jogo: suas vidas acabaram.", mensagem_var)
            return

        posicionar_bola_na_plataforma(jogo)
        mensagem_var.set("Você perdeu uma vida. Pressione ESPAÇO para tentar novamente.")


def processar_tecla(
    jogo, tecla, canvas=None, pontuacao_var=None, vidas_var=None, fase_var=None, mensagem_var=None
):
    if tecla in ("space", "Space", "Return"):
        if not jogo["ativo"] and canvas is not None:
            iniciar_partida(
                jogo, canvas, pontuacao_var, vidas_var, fase_var, mensagem_var
            )
        elif jogo["ativo"] and not jogo["lancada"]:
            jogo["lancada"] = True
            if mensagem_var is not None:
                mensagem_var.set("Rebata a bola e destrua todos os blocos!")


def executar():
    jogo = criar_estado()
    janela = tk.Tk()
    janela.title("Rebatedor Retrô")
    janela.configure(bg="#171526")
    janela.resizable(False, False)

    estilo = {
        "bg": "#171526",
        "fg": "#f3f0e8",
        "font": ("Courier", 11, "bold"),
    }
    topo = tk.Frame(janela, bg="#171526", padx=12, pady=10)
    topo.pack(fill="x")

    pontuacao_var = tk.StringVar(value="Pontos: 0")
    vidas_var = tk.StringVar(value="Vidas: 3")
    fase_var = tk.StringVar(value="Fase: --")
    tk.Label(topo, textvariable=pontuacao_var, **estilo).pack(side="left", padx=10)
    tk.Label(topo, textvariable=vidas_var, **estilo).pack(side="left", padx=10)
    tk.Label(topo, textvariable=fase_var, **estilo).pack(side="right", padx=10)

    canvas = tk.Canvas(
        janela,
        width=LARGURA,
        height=ALTURA,
        bg="#211e35",
        highlightthickness=3,
        highlightbackground="#50e3c2",
    )
    canvas.pack(padx=12)
    desenhar_menu(canvas)

    mensagem_var = tk.StringVar(value=jogo["mensagem"])
    tk.Label(
        janela,
        textvariable=mensagem_var,
        bg="#171526",
        fg="#ffe66d",
        font=("Courier", 11, "bold"),
        pady=8,
    ).pack()

    botoes = tk.Frame(janela, bg="#171526", pady=6)
    botoes.pack()
    tk.Button(
        botoes,
        text="Jogar / reiniciar",
        takefocus=False,
        command=lambda: iniciar_partida(
            jogo, canvas, pontuacao_var, vidas_var, fase_var, mensagem_var
        ),
        bg="#50e3c2",
        fg="#171526",
        font=("Courier", 10, "bold"),
        padx=12,
    ).pack(side="left", padx=6)
    tk.Label(
        janela,
        text="Mover: ← → ou A / D     Lançar: ESPAÇO",
        **estilo,
        pady=8,
    ).pack()

    def ao_pressionar(evento):
        tecla = evento.keysym
        jogo["teclas"].add(tecla)
        processar_tecla(
            jogo, tecla, canvas, pontuacao_var, vidas_var, fase_var, mensagem_var
        )

    def ao_soltar(evento):
        jogo["teclas"].discard(evento.keysym)

    def ao_perder_foco(_evento):
        jogo["teclas"].clear()

    def fechar_janela():
        jogo["aberto"] = False

    janela.bind("<KeyPress>", ao_pressionar)
    janela.bind("<KeyRelease>", ao_soltar)
    janela.bind("<FocusOut>", ao_perder_foco)
    janela.protocol("WM_DELETE_WINDOW", fechar_janela)
    janela.focus_set()

    # Este while é o ciclo principal explícito; Tk atualiza os eventos e a tela.
    while jogo["aberto"]:
        inicio = time.perf_counter()
        try:
            janela.update()
        except tk.TclError:
            break

        if not jogo["aberto"]:
            break

        if jogo["ativo"]:
            mover_plataforma(jogo)
            atualizar_bola(
                jogo, canvas, pontuacao_var, vidas_var, fase_var, mensagem_var
            )
            atualizar_desenho(jogo, canvas)

        tempo_restante = INTERVALO - (time.perf_counter() - inicio)
        if tempo_restante > 0:
            time.sleep(tempo_restante)

    try:
        janela.destroy()
    except tk.TclError:
        pass


if __name__ == "__main__":
    executar()
