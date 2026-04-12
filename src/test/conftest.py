"""Fixtures compartidas para pruebas.

Este archivo es cargado automaticamente por pytest. Define aqui
las fixtures que se usan en multiples archivos de pruebas.
"""

import pytest


@pytest.fixture
def sample_book():
    """Retorna un diccionario de prueba con datos de un libro.

    Returns:
        dict: Diccionario con campos de un libro de prueba.
    """
    return {
        "name": "Clean Code",
        "author": "Robert C. Martin",
        "description": "A Handbook of Agile Software Craftsmanship",
        "url": "https://example.com/clean-code",
        "content": "Chapter 1: Clean Code...",
    }
