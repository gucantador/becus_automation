from datetime import date, timedelta, datetime
import holidays
from enum import Enum

from . import db
from .models import History

# Lista de feriados no Brasil
br_holidays = holidays.Brazil(years=[2025, 2026, 2027, 2028, 2029])

def prazo(inicio: date | str, dias: int):
    if isinstance(inicio, str):
        data = datetime.strptime(inicio, "%d/%m/%Y").date()
    else:
        data = inicio
    cont = 0
    while cont < dias:
        data += timedelta(days=1)
        # Pula se for fim de semana ou feriado
        if data.weekday() < 5 and data not in br_holidays:
            cont += 1
    return data

class Status(Enum):
    AGENDAR = "agendar"
    PROGRAMADO = "programado"
    ESPERA = "espera"
    EM_EXECUCAO = "em_execucao"
    EM_PAUSA = "em_pausa"
    PENDENTE = "pendente"
    CONCLUIDO = "concluido"
    ENTREGUE = "entregue"
    CANCELADO = "cancelado"
    EM_REVISAO = "em_revisao"


class Actions:
    CRIAR_PROJETO = "Criou o projeto"
    ATUALIZAR_PROJETO = "Atualizou o projeto"
    DELETAR_PROJETO = "Deletou o projeto"

    @staticmethod
    def update_status(before: str, after: str) -> str:
        return f"Alterou o status de {before} para {after}"

    @staticmethod
    def log_action(user_id: int, project_id: int, action: str):
        """
        Salva uma ação no histórico de um projeto.
        """
        hist = History(
            user_id=user_id,
            project_id=project_id,
            action=action,
            timestamp=datetime.utcnow()
        )
        db.session.add(hist)
        db.session.commit()