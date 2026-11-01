from dataclasses import dataclass
from rolagem import RandomPool


NIVEL_MINIMO = 1
NIVEL_MAXIMO = 5


@dataclass
class Combatente:
    chave: str
    nome: str
    nivel: int
    bonus: int
    dado: int
    total: int
    chegada: int
    eh_npc: bool


class InitiativeManager:
    def __init__(self):
        self._pool = RandomPool()
        self.aberta = False
        self.combatentes = {}
        self._seq = 0

    def start(self):
        self.aberta = True
        self.combatentes.clear()
        self._seq = 0

    def _proximo_seq(self):
        self._seq += 1
        return self._seq

    @staticmethod
    def _validar_nivel(nivel):
        try:
            valor = int(nivel)
        except (TypeError, ValueError) as exc:
            raise ValueError("Nível inválido. Use 1 a 5.") from exc

        if valor < NIVEL_MINIMO or valor > NIVEL_MAXIMO:
            raise ValueError("Nível inválido. Use 1 a 5.")

        return valor

    @staticmethod
    def _bonus_por_nivel(nivel: int) -> int:
        return (nivel - 1) * 2

    def _nomes_usados(self, excluir_chave=None):
        return {
            combatente.nome.lower()
            for chave, combatente in self.combatentes.items()
            if chave != excluir_chave
        }

    def _gerar_nome_unico(self, base: str, excluir_chave=None) -> str:
        import re
        
        base = " ".join(base.split())

        if not base:
            raise ValueError("Nome inválido.")

        usados = self._nomes_usados(excluir_chave)

        if base.lower() not in usados:
            return base

        padrao_sufixo = re.compile(r"^(?P<prefixo>.+?)\s+(?P<numero>\d+)$")
        alvo = padrao_sufixo.match(base)

        if alvo:
            prefixo = alvo.group("prefixo")
            numero = int(alvo.group("numero")) + 1
        else:
            prefixo = base
            numero = 2

        while True:
            candidato = f"{prefixo} {numero}"

            if candidato.lower() not in usados:
                return candidato

            numero += 1

    def _registrar(self, chave: str, nome: str, nivel, eh_npc: bool) -> Combatente:
        nivel_validado = self._validar_nivel(nivel)
        bonus = self._bonus_por_nivel(nivel_validado)

        dado = self._pool.randint(1, 20)
        total = dado + bonus
        chegada = self._proximo_seq()

        combatente = Combatente(
            chave=chave,
            nome=nome,
            nivel=nivel_validado,
            bonus=bonus,
            dado=dado,
            total=total,
            chegada=chegada,
            eh_npc=eh_npc,
        )

        self.combatentes[chave] = combatente

        return combatente

    def adicionar_jogador(self, autor_id: str, nome_exibicao: str, nivel) -> Combatente:
        if not self.aberta:
            raise ValueError("Iniciativa fechada. Use /ini start para abrir.")

        if not autor_id:
            raise ValueError("Autor inválido.")

        chave = f"player:{autor_id}"
        existente = self.combatentes.get(chave)

        base = " ".join((nome_exibicao or "").split()) or "Jogador"

        if existente and existente.nome.lower() == base.lower():
            nome_final = existente.nome
        else:
            nome_final = self._gerar_nome_unico(base, excluir_chave=chave)

        return self._registrar(
            chave=chave,
            nome=nome_final,
            nivel=nivel,
            eh_npc=False,
        )

    def adicionar_npc(self, nome: str, nivel) -> Combatente:
        if not self.aberta:
            raise ValueError("Iniciativa fechada. Use /ini start para abrir.")

        nome_final = self._gerar_nome_unico(nome)
        chave = f"npc:{nome_final.lower()}"

        return self._registrar(
            chave=chave,
            nome=nome_final,
            nivel=nivel,
            eh_npc=True,
        )

    def ordem(self):
        return sorted(
            self.combatentes.values(),
            key=lambda c: (-c.total, -c.nivel, c.chegada),
        )

    def encerrar(self):
        self.aberta = False
        return self.ordem()


class ControleIniciativaPorCanal:
    def __init__(self):
        self._gerenciadores = {}

    def obter(self, canal_id) -> InitiativeManager:
        if canal_id not in self._gerenciadores:
            self._gerenciadores[canal_id] = InitiativeManager()

        return self._gerenciadores[canal_id]