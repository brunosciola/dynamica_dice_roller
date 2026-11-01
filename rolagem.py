import random
from dataclasses import dataclass


FALHA = "Falha"
ACERTO_PARCIAL = "Acerto Parcial"
ACERTO_CHEIO = "Acerto Cheio"


class RandomPool:
    def __init__(self, rng=None):
        self._rng = rng or random
        self._pool = None
        self._index = 0

    def _gerar_pool(self):
        pool_inicial = [self._rng.randint(1, 20) for _ in range(1000)]
        
        selecionados_100 = self._rng.sample(pool_inicial, 100)
        selecionados_10 = self._rng.sample(selecionados_100, 10)
        selecionados_1 = self._rng.sample(selecionados_10, 1)
        
        self._pool = selecionados_1
        self._index = 0

    def randint(self, min_val: int, max_val: int) -> int:
        if self._pool is None or self._index >= len(self._pool):
            self._gerar_pool()
        
        valor_base = self._pool[self._index]
        self._index += 1
        
        if min_val == 1 and max_val == 20:
            return valor_base
        
        valor_normalizado = (valor_base - 1) / 19
        return min_val + int(valor_normalizado * (max_val - min_val + 1))

    def sample(self, population, k):
        return self._rng.sample(population, k)


@dataclass(frozen=True)
class ResultadoRolagem:
    dado: int
    modificador: int
    final: int
    categoria: str
    xp: int

    @property
    def detalhe(self) -> str:
        if self.modificador == 0:
            return str(self.dado)

        if self.modificador > 0:
            return f"{self.dado}+{self.modificador}"

        return f"{self.dado}{self.modificador}"

    def formatar(self) -> str:
        return f"{self.categoria} ({self.xp} XP): {self.final} ({self.detalhe})"


def classificar_resultado(final: int) -> tuple[str, int]:
    if final <= 7:
        return FALHA, 1

    if final <= 13:
        return ACERTO_PARCIAL, 2

    return ACERTO_CHEIO, 1


def rolar_d20(modificador: int = 0, pool: RandomPool = None) -> ResultadoRolagem:
    pool = pool or RandomPool()

    dado = pool.randint(1, 20)
    final = dado + modificador
    categoria, xp = classificar_resultado(final)

    return ResultadoRolagem(
        dado=dado,
        modificador=modificador,
        final=final,
        categoria=categoria,
        xp=xp,
    )


def interpretar_modificador(texto: str) -> int:
    texto = texto.strip()

    if not texto:
        return 0

    if any(ch.isspace() for ch in texto):
        raise ValueError("Use /r, /r +2 ou /r -1.")

    try:
        valor = int(texto)
    except ValueError as exc:
        raise ValueError("Use /r, /r +2 ou /r -1.") from exc

    if valor < -1000 or valor > 1000:
        raise ValueError("Modificador fora do limite razoável.")

    return valor