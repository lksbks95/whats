# Este ficheiro é o ponto de entrada para o nosso servidor WSGI (Gunicorn).
# Ele importa a aplicação e o socketio do nosso ficheiro principal.

from .main import app, socketio

# O Gunicorn irá usar o objeto 'socketio' para iniciar a aplicação,
# garantindo que o suporte a WebSockets funcione corretamente.
# Se não estivéssemos a usar WebSockets, apontaríamos para 'app'.
