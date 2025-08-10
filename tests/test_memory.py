from spirits import memory


def test_last_real_command_ignores_johny_user(monkeypatch, tmp_path):
    db_path = tmp_path / "memory.db"
    monkeypatch.setattr(memory, "DB_PATH", db_path)
    memory._init_db()
    memory.log("user", "ls")
    memory.log("johny_user", "привет, Джонни, как дела?")
    assert memory.last_real_command() == "ls"
