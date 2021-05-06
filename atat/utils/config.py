import json
import os
from configparser import ConfigParser
from enum import Enum

import pendulum

from atat.utils.environment import get_application_environment_name
from atat.utils.path import get_path_from_root


def make_config(direct_config=None):
    """Assemble a ConfigParser object to pass to map_config

    Configuration values are possibly applied from multiple sources. They are
    applied in the following order. At each step, options that are currently set
    are overwritten by options of the same name:
    1. The base config file, `base.ini`
    2. An environment's config file -- e.g. if ENV="test", `test.ini`
    3. Optionally: If an OVERRIDE_CONFIG_DIRECTORY environment variable is
        present, configuration files in that directory
    4. Environment variables
    5. Optionally: A dictionary passed in as the `direct_config` parameter

    After the configuration is finished being written / overwritten, a database
    uri, redis uri, and broker uri (in our case, a celery uri) are set.

    Finally, the final ConfigParser object is passed to `map_config()`
    """

    config = ConfigParser(allow_no_value=True, interpolation=None)
    config.optionxform = str

    # Global environment name for the ATAT Application
    environment_name = get_application_environment_name()

    # Read configuration values from base and environment configuration files
    BASE_CONFIG_FILENAME = get_path_from_root("config/base.ini")
    ENV_CONFIG_FILENAME = get_path_from_root(f"config/{environment_name.lower()}.ini")
    config_files = [BASE_CONFIG_FILENAME, ENV_CONFIG_FILENAME]
    # ENV_CONFIG will override values in BASE_CONFIG.
    config.read(config_files)
    # Copy hybrid section to default section
    apply_hybrid_config_options(config)

    # Optionally read configuration files that overwrite base and environment files
    OVERRIDE_CONFIG_DIRECTORY = os.getenv("OVERRIDE_CONFIG_DIRECTORY")
    if OVERRIDE_CONFIG_DIRECTORY:
        apply_config_from_directory(OVERRIDE_CONFIG_DIRECTORY, config)

    # Check for ENV variables to override config files
    apply_config_from_environment(config)

    # Finally, override any options set to this point with the direct_config parameter
    if direct_config:
        config.read_dict(direct_config)
        # Copy hybrid section to default section
        apply_hybrid_config_options(config)

    # Assemble DATABASE_URI value
    database_uri = "postgresql://{}:{}@{}:{}/{}".format(  # pragma: allowlist secret
        config.get("default", "PGUSER"),
        config.get("default", "PGPASSWORD"),
        config.get("default", "PGHOST"),
        config.get("default", "PGPORT"),
        config.get("default", "PGDATABASE"),
    )
    config.set("default", "DATABASE_URI", database_uri)

    # Assemble REDIS_URI value
    redis_use_ssl = config["default"].getboolean("REDIS_TLS")
    redis_uri = "redis{}://{}:{}@{}".format(  # pragma: allowlist secret
        ("s" if redis_use_ssl else ""),
        (config.get("default", "REDIS_USER") or ""),
        (config.get("default", "REDIS_PASSWORD") or ""),
        config.get("default", "REDIS_HOST"),
    )
    if redis_use_ssl:
        ssl_mode = config.get("default", "REDIS_SSLMODE")
        ssl_checkhostname = "false"

        if config["default"].getboolean("REDIS_SSLCHECKHOSTNAME"):
            ssl_checkhostname = "true"

        redis_uri = f"{redis_uri}/?ssl_cert_reqs={ssl_mode}&ssl_check_hostname={ssl_checkhostname}"

    # Pre set some additional variables as default
    config.set("default", "REDIS_URI", redis_uri)
    config.set("default", "BROKER_URL", redis_uri)
    config.set("default", "ENV", environment_name)

    return map_config(config)


def map_config(config):
    return {
        **config["default"],
        "USE_AUDIT_LOG": config["default"].getboolean("USE_AUDIT_LOG"),
        "DEBUG": config["default"].getboolean("DEBUG"),
        "DEBUG_MAILER": config["default"].getboolean("DEBUG_MAILER"),
        "DEBUG_SMTP": int(config["default"]["DEBUG_SMTP"]),
        "SQLALCHEMY_ECHO": config["default"].getboolean("SQLALCHEMY_ECHO"),
        "PORT": int(config["default"]["PORT"]),
        "SQLALCHEMY_DATABASE_URI": config["default"]["DATABASE_URI"],
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SQLALCHEMY_ENGINE_OPTIONS": {
            "json_serializer": sqlalchemy_dumps,
            "connect_args": {
                "sslmode": config["default"]["PGSSLMODE"],
                "sslrootcert": config["default"]["PGSSLROOTCERT"],
            },
            "pool_pre_ping": True,
        },
        "WTF_CSRF_ENABLED": config.getboolean("default", "WTF_CSRF_ENABLED"),
        "PERMANENT_SESSION_LIFETIME": config.getint(
            "default", "PERMANENT_SESSION_LIFETIME"
        ),
        "LOG_JSON": config.getboolean("default", "LOG_JSON"),
        "LIMIT_CONCURRENT_SESSIONS": config.getboolean(
            "default", "LIMIT_CONCURRENT_SESSIONS"
        ),
        # Store the celery task results in a database table (celery_taskmeta)
        "CELERY_RESULT_BACKEND": "db+{}".format(config.get("default", "DATABASE_URI")),
        # Do not automatically delete results (by default, Celery will do this
        # with a Beat job once a day)
        "CELERY_RESULT_EXPIRES": 0,
        "CELERY_RESULT_EXTENDED": True,
        "CELERYBEAT_SCHEDULE_VALUE": config.getint(
            "default", "CELERYBEAT_SCHEDULE_VALUE"
        ),
        "CONTRACT_START_DATE": pendulum.from_format(
            config.get("default", "CONTRACT_START_DATE"), "YYYY-MM-DD"
        ).date(),
        "CONTRACT_END_DATE": pendulum.from_format(
            config.get("default", "CONTRACT_END_DATE"), "YYYY-MM-DD"
        ).date(),
        "SESSION_COOKIE_SECURE": config.getboolean("default", "SESSION_COOKIE_SECURE"),
        "ALLOW_LOCAL_ACCESS": config.getboolean("default", "ALLOW_LOCAL_ACCESS"),
        "SAML_SSL_VERIFY": config.getboolean("default", "SAML_SSL_VERIFY"),
    }


def apply_hybrid_config_options(config: ConfigParser):
    """Copy config options in [hybrid] section to [default] section of config"""

    config.read_dict({"default": dict(config.items("hybrid"))})


def apply_config_from_directory(config_dir, config, section="default"):
    """
    Loop files in a directory, check if the names correspond to
    known config values, and apply the file contents as the value
    for that setting if they do.
    """
    for confsetting in os.listdir(config_dir):
        if confsetting in config.options(section):
            full_path = os.path.join(config_dir, confsetting)
            with open(full_path, "r") as conf_file:
                config.set(section, confsetting, conf_file.read().strip())

    return config


def apply_config_from_environment(config, section="default"):
    """
    Loops all the configuration settings in a given section of a
    config object and checks whether those settings also exist as
    environment variables. If so, it applies the environment
    variables value as the new configuration setting value.
    """
    for confsetting in config.options(section):
        env_override = os.getenv(confsetting.upper())
        if env_override:
            config.set(section, confsetting, env_override)

    return config


def sqlalchemy_dumps(dct):
    def _default(obj):
        if isinstance(obj, Enum):
            return obj.name
        else:
            raise TypeError()

    return json.dumps(dct, default=_default)
