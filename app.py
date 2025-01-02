from app import app
import os

if __name__ == "__main__":
    host = '127.0.0.1'
    port = 5000

    # Verifica se o processo atual é o principal
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        print(f"Servidor rodando em http://{host}:{port} (Debug: {'Ativado' if app.debug else 'Desativado'})")

    app.run(debug=True, host=host, port=port)
