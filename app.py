#!/usr/bin/env python

from atat.app import make_app, make_config

config = make_config()
app = make_app(config)

if __name__ == "__main__":
    port = int(config["PORT"])
    cert_path = config["APP_SSL_CERT_PATH"]
    key_path = config["APP_SSL_KEY_PATH"]

    ssl_context = None

    if cert_path is not None and key_path is not None:
        ssl_context = (cert_path, key_path)

    app.run(
        port=port, extra_files=["translations.yaml"], ssl_context=ssl_context,
    )
    print(f"Listening on http{'s' if ssl_context else ''}://localhost:%i" % port)
