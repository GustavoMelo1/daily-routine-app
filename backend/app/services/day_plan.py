from app.repositories.day import insert_day
from app.repositories.task import insert_task


def create_day_plan(connection, plan):
    with connection:
        day_id = insert_day(connection, plan.data.isoformat(), plan.minutos_estudados,
                            plan.frase_do_dia, plan.autor_frase, plan.tipo)
        for description in plan.tarefas:
            insert_task(connection, day_id, description, 0)
    return day_id
