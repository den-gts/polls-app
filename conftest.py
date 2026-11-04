import pytest

def pytest_collection_modifyitems(session, config, items):
    """Автоматически добавляет маркер django_db ко всем тестам, если он еще не установлен."""
    for item in items:
        if not any(marker.name == 'django_db' for marker in item.iter_markers()):
            item.add_marker(pytest.mark.django_db)