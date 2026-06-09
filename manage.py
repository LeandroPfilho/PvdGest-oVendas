#!/usr/bin/env python
"""Arquivo de entrada para executar comandos do Django."""
import os
import sys


def main():
    """Configura o projeto e executa o comando informado no terminal."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
