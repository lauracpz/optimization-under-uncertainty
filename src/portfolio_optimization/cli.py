"""Punto de entrada de línea de comandos del proyecto."""

from .models import ejecutar_modelos, imprimir_resultados


def main() -> None:
    """Resuelve los cinco modelos y muestra sus resultados."""
    imprimir_resultados(ejecutar_modelos())


if __name__ == "__main__":
    main()
