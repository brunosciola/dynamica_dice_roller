from rolagem import rolar_d20, interpretar_modificador
from iniciativa import ControleIniciativaPorCanal


class ComandoBot:
    def __init__(self):
        self.iniciativas = ControleIniciativaPorCanal()

    def processar(self, canal_id, autor_id, nome_exibicao, texto):
        texto = (texto or "").strip()

        if not texto.startswith("/"):
            return None

        partes = texto.split()

        if not partes:
            return None

        comando = partes[0].lower()
        args = partes[1:]

        if comando == "/r":
            return self._comando_r(args, nome_exibicao)

        if comando == "/ini":
            return self._comando_ini(
                canal_id=canal_id,
                autor_id=autor_id,
                nome_exibicao=nome_exibicao,
                args=args,
            )

        return "Comando inválido. Use /r ou /ini."

    def _comando_r(self, args, nome_exibicao):
    
        if len(args) > 1:
            return "Use /r, /r +2 ou /r -1."

        try:
            modificador = interpretar_modificador(args[0] if args else "")
            resultado = rolar_d20(modificador)
            return f"{nome_exibicao}: {resultado.formatar()}"
        except ValueError as exc:
            return str(exc)

    def _comando_ini(self, canal_id, autor_id, nome_exibicao, args):
        if not args:
            return "Use /ini start, /ini end ou /ini <nível> [nome]."

        manager = self.iniciativas.obter(canal_id)
        subcomando = args[0].lower()

        if subcomando == "start":
            manager.start()
            return "Iniciativa aberta. Use /ini <nivel>." # para mestres: /ini <nível> [nome] 

        if subcomando == "end":
            ordem = manager.encerrar()

            if not ordem:
                return "Nenhum combatente registrado."

            linhas = ["Ordem de Iniciativa:"]

            for indice, combatente in enumerate(ordem, 1):
                if combatente.bonus == 0:
                    detalhe = str(combatente.dado)
                elif combatente.bonus > 0:
                    detalhe = f"{combatente.dado}+{combatente.bonus}"
                else:
                    detalhe = f"{combatente.dado}{combatente.bonus}"

                linhas.append(
                    f"{indice}. {combatente.nome} (Nv {combatente.nivel}) — {combatente.total} ({detalhe})"
                )

            return "\n".join(linhas)

        try:
            nivel = int(args[0])
        except ValueError:
            return None

        if len(args) == 1:
            try:
                manager.adicionar_jogador(
                    autor_id=autor_id,
                    nome_exibicao=nome_exibicao,
                    nivel=nivel,
                )
            except ValueError:
                return None
        else:
            nome = " ".join(args[1:]).strip()

            try:
                manager.adicionar_npc(
                    nome=nome,
                    nivel=nivel,
                )
            except ValueError:
                return None

        return None