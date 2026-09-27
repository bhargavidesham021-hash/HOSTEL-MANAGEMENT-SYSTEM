"""Vercel's supported Flask WSGI entry point for the single deployment."""

from backend.app import create_app

app = create_app()
