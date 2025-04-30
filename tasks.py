# back/tasks.py
from celery_app import celery
from app.algorithm.csp_algoritm import solve_schedule
from socketio_server import socketio

@celery.task(bind=True)
def generate_schedule(self, socket_id):
    # from run import socketio

    print(f"[generate_schedule] started for socket_id={socket_id}")

    result = solve_schedule()  # your CSP solver
    print("[generate_schedule] solver returned:", "no result" if not result else "ok")

    if not result:
        print("[generate_schedule] no feasible solution")
        return {"error": "no-solution"}

    solution, text = result
    print("[generate_schedule] emitting schedule_ready")
    socketio.emit(
        "schedule_ready",
        {"solution": solution, "text": text},
        room=socket_id
    )
    print("[generate_schedule] done")
    return {"status": "ok"}
