import yfinance as yf


def obtener_historico(simbolo, periodo="1mo", intervalo="1d"):
    """
    Devuelve el histórico de precios de un activo.
    """

    try:
        ticker = yf.Ticker(simbolo)

        datos = ticker.history(
            period=periodo,
            interval=intervalo
        )

        return datos

    except Exception as e:
        print(e)
        return None


def obtener_info(simbolo):
    """
    Devuelve información general del activo.
    """

    try:

        ticker = yf.Ticker(simbolo)

        return ticker.fast_info

    except Exception:

        return None

