# reacao.py
class ReacaoManager:
    def __init__(self):
        self.modo_reacao_ativado = False
        self.rolagens_reacao = []
        self.ordem_vez = []

    def iniciar_reacao(self):
        self.modo_reacao_ativado = True
        self.rolagens_reacao = []

    def finalizar_reacao(self):
        self.modo_reacao_ativado = False
        # Ordena do maior para o menor
        self.ordem_vez = sorted(self.rolagens_reacao, key=lambda x: x[1], reverse=True)
        return self.ordem_vez

    def adicionar_rolagem_reacao(self, nome, resultado):
        self.rolagens_reacao.append((nome, resultado))

    def obter_ordem_vez(self):
        return self.ordem_vez

    def limpar_reacao(self):
        self.rolagens_reacao = []
        self.ordem_vez = []