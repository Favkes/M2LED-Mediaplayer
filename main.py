from utils.globals import Globals
from utils.simple_logs import Logger, Logtype
from gui import core
import colorama


# Initializing color support for cmd.exe
colorama.init()


logger = Logger(__name__, 'green')


# TODO: Add a playlist functionality (Preferably file based with
#       a file editor included)


def main():
    logger.log('Initiating core.AppStructure setup...', Logtype.init)
    app = core.AppStructure()
    app.load()
    app.ledcomm_init()
    logger.log('Running app...', Logtype.info)
    app.run_app()



def cleanup():
    logger.log('Sentencing all threads to die...', Logtype.kill)
    Globals.killall()


if __name__ == "__main__":
    exception = None

    try:
        main()

    except Exception as e:
        exception = str(e)
        logger.log('CRITICAL ERROR - Program exit imminent.', Logtype.error)

    finally:
        logger.log('Running the cleanup sequence...', Logtype.info)
        cleanup()

    logger.log('Program exited successfully.', Logtype.info)

    if exception is not None:
        logger.log(f'Error code: {exception}', Logtype.error)