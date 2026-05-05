"""Application layer: use cases orchestrating domain behavior.

This layer depends only on the domain (entities + ports). It must not import
FastAPI, Pydantic, or any infrastructure adapters.
"""
