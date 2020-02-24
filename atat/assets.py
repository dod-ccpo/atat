from flask_assets import Environment, Bundle

environment = Environment()

css = Bundle(
    "../static/assets/index.css", output="../static/assets/index.%(version)s.css"
)

environment.register("css", css)

js = Bundle("../static/assets/index.js", output="../static/assets/index.%(version)s.js")
environment.register("js_all", js)
