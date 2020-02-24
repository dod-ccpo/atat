#!/usr/bin/env python

from atat.app import make_app, make_config

config = make_config()
app = make_app(config)

if __name__ == "__main__":
    port = int(config["PORT"])
    app.run(port=port, extra_files=["translations.yaml"])
    print("Listening on http://localhost:%i" % port)
