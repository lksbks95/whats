import logging
import sys

# Configura o log para ser bem detalhado e aparecer nos logs da Koyeb
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] DEBUG_RUNNER: %(message)s',
    stream=sys.stderr,
)

logging.info("--- INICIANDO O DEBUG RUNNER ---")

# Este é o objeto que vamos expor ao Gunicorn
callable_app = None

try:
    # Este é o passo crítico. Estamos tentando fazer o que o Gunicorn faz.
    logging.info("Tentando importar 'socketio' de 'src.main'...")
    from src.main import socketio

    logging.info("Importação de 'src.main' foi concluída.")
    logging.info("Verificando o estado do objeto 'socketio' importado...")
    logging.info(f"  - Tipo do objeto (type): {type(socketio)}")
    logging.info(f"  - O objeto é 'None'?: {socketio is None}")

    # Verifica se o objeto é "chamável" (callable), como o Gunicorn exige
    is_it_callable = callable(socketio)
    logging.info(f"  - O objeto é 'callable()'?: {is_it_callable}")

    if is_it_callable:
        logging.info("SUCESSO: O objeto 'socketio' parece ser válido e chamável.")
        callable_app = socketio
    else:
        logging.error("!!! FALHA NA DEPURAÇÃO: O objeto 'socketio' FOI IMPORTADO, MAS NÃO é chamável. Gunicorn irá falhar por este motivo. !!!")
        callable_app = socketio

except ImportError as e:
    logging.error(f"!!! ERRO DE IMPORTAÇÃO: Não foi possível importar 'socketio' de 'src.main'. Verifique o erro abaixo. !!!", exc_info=True)
    raise e

except Exception as e:
    # Se QUALQUER outra exceção acontecer durante a importação do 'main.py', nós a capturamos aqui.
    # Esta é nossa melhor chance de ver um erro escondido.
    logging.error("!!! EXCEÇÃO CRÍTICA OCORREU DURANTE A IMPORTAÇÃO DE 'src.main' !!!", exc_info=True)
    # exc_info=True irá imprimir o traceback completo da exceção
    raise e

finally:
    logging.info("--- DEBUG RUNNER CONCLUÍDO ---")
    # O Gunicorn agora irá tentar usar o objeto 'callable_app'.
    # Se for válido, a aplicação inicia. Se não, ela trava, mas nossos logs nos dirão o porquê.
