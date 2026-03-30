from collections import defaultdict, deque

_history: dict[int, deque] = defaultdict(lambda: deque(maxlen=10))  # 5 pairs = 10 entries


def add_to_history(user_id: int, role: str, content: str):
    _history[user_id].append({"role": role, "content": content})


def get_history(user_id: int) -> list[dict]:
    return list(_history[user_id])


def clear_history(user_id: int):
    _history[user_id].clear()
