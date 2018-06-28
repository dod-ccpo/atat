#!/usr/bin/env python

import tornado.ioloop

from atst.app import make_app, make_deps, make_config

config = make_config()
deps = make_deps(config)
app = make_app(config, deps)

if __name__ == "__main__":
    port = int(config["default"]["PORT"])
    app.listen(port)
    print("Listening on http://localhost:%i" % port)
    tornado.ioloop.IOLoop.current().start()
