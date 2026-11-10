"""Modulo de decisoes da corrida de carros com poderes."""

ITENS_DISPONIVEIS = {
    "turbo",
    "poder_especial",
    "escudo",
    "banana",
    "pedra",
    "correntes",
}


def decidir_uso_de_item(item):
    """Decide se o item informado pode ser utilizado no turno."""
    if not item or item not in ITENS_DISPONIVEIS:
        return "Item indisponivel para uso."
    return f"Usar item: {item}."


def decidir_efeito_do_ataque(item, escudo_ativo):
    """Retorna a mensagem descrevendo o resultado de um ataque recebido."""
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
    """Decide se o corredor pode coletar um novo item ao passar por uma caixa."""
    if not passou_por_caixa:
        return "Nao coletar: nenhuma caixa alcancada."
    if quantidade_itens >= limite_inventario:
        return "Nao coletar: inventario cheio."
    return "Coletar novo item da caixa."


def decidir_situacao_da_corrida(resistencia, posicao, distancia_chegada):
    """Avalia se o corredor perdeu por resistencia, venceu na chegada ou continua."""
    if resistencia <= 0:
        return "Derrota: carro ficou sem resistencia."
    if posicao >= distancia_chegada:
        return "Vitoria: cruzou a linha de chegada!"
    return "Continua na disputa."

