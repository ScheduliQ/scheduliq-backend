# back/tasks.py
from celery_app import celery
from app.algorithm.csp_algoritm import solve_schedule

@celery.task(bind=True)
def generate_schedule(self, socket_id):
    from run import socketio

    """
    Runs your CSP solver off-process, then pushes the result
    back to the browser over the same Socket.IO connection.
    """
    result = solve_schedule()  # returns (formatted_json, text_output)
    if not result:
        return {"error": "no-solution"}

    solution, text = result
    # emit into the room matching the client’s socket_id
    socketio.emit(
        "schedule_ready",
        {"solution": solution, "text": text},
        room=socket_id
    )
    return {"status": "ok"}
