"""Smoke-тесты: проверяют, что каркас проекта собирается и импортируется."""


def test_project_structure_exists() -> None:
    """Проверяем, что базовые пакеты проекта импортируются без ошибок."""
    import app  # noqa: F401
    import app.api  # noqa: F401
    import app.core  # noqa: F401
    import app.ml  # noqa: F401
    import app.services  # noqa: F401


def test_health_endpoint_placeholder() -> None:
    """Заглушка: проверяем, что FastAPI-приложение создаётся."""
    from app.main import app

    assert app is not None
    assert app.title == "Demand & Price Forecasting API"
