# # back/tasks.py
# from celery_app import celery
# from app.algorithm.csp_algoritm import solve_schedule
# from socketio_server import socketio
# @celery.task(bind=True)
# def generate_schedule(self, socket_id):
#     # from run import socketio

#     print(f"[generate_schedule] started for socket_id={socket_id}")

#     result = solve_schedule()  # your CSP solver
#     print("[generate_schedule] solver returned:", "no result" if not result else "ok")

#     if not result:
#         print("[generate_schedule] no feasible solution")
#         return {"error": "no-solution"}

#     solution, text = result
#     print("[generate_schedule] emitting schedule_ready")
#     socketio.emit(
#         "schedule_ready",
#         {"solution": solution, "text": text},
#         room=socket_id
#     )
#     print("[generate_schedule] done")
#     return {"status": "ok"}


# back/tasks.py
from celery_app import celery      # או פשוט: from celery_app import celery
from socketio_server import socketio
from app.algorithm.csp_algoritm import solve_schedule

@celery.task(bind=True)
def generate_schedule(self, socket_id):
    print(f"[generate_schedule] start for socket_id={socket_id}")
    result = solve_schedule()
    if not result:
        print("[generate_schedule] no solution")
        socketio.emit(
            "schedule_error",
            {"error": "אין פתרון אפשרי"},
            namespace="/",
            room=socket_id
        )
        return

    solution, text = result
    print("[generate_schedule] emitting schedule_ready")
    socketio.emit(
        "schedule_ready",
        {"solution": solution, "text": text},
        namespace="/",
        room=socket_id
    )
    print("[generate_schedule] done")
    return {"status": "ok"}
