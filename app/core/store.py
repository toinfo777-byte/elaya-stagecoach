# --- metrics & stats ---------------------------------------------------------
def get_stats() -> dict:
    """
    Сводка для HQ-панели.
    Возвращает агрегаты:
      - users: количество пользователей с состоянием
      - last_update: последний ts из scene_state
      - counts: словарь по последним сценам (intro / reflect / transition)
      - last_reflection: последняя непустая рефлексия с timestamp
    """
    with _lock, sqlite3.connect(_DB_PATH) as con:
        con.row_factory = sqlite3.Row

        # users / last_update
        row = con.execute(
            """
            SELECT COUNT(*) AS users_cnt,
                   MAX(updated_at) AS last_update
            FROM scene_state
            """
        ).fetchone()
        users_cnt = int(row["users_cnt"] or 0)
        last_update = row["last_update"]

        # counts by last_scene
        counts = {"intro": 0, "reflect": 0, "transition": 0}
        for r in con.execute(
            """
            SELECT last_scene, COUNT(*) AS c
            FROM scene_state
            GROUP BY last_scene
            """
        ):
            if r["last_scene"] in counts:
                counts[r["last_scene"]] = int(r["c"] or 0)

        # last non-null reflection
        ref = con.execute(
            """
            SELECT last_reflect, updated_at
            FROM scene_state
            WHERE last_reflect IS NOT NULL AND TRIM(last_reflect) <> ''
            ORDER BY updated_at DESC
            LIMIT 1
            """
        ).fetchone()
        last_reflect = ref["last_reflect"] if ref else None
        last_reflect_at = ref["updated_at"] if ref else None

    return {
        "users": users_cnt,
        "last_update": last_update,
        "counts": counts,
        "last_reflection": {
            "text": last_reflect,
            "at": last_reflect_at,
        },
    }
