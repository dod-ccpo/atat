from configparser import ConfigParser

import pytest

from atat.utils.config import (
    apply_config_from_directory,
    apply_config_from_environment,
    apply_hybrid_config_options,
    make_config,
)


@pytest.fixture
def config_object(request):
    config = ConfigParser(interpolation=None)
    config.optionxform = str
    config.read_dict(request.param)
    return config


DEFAULT_CONFIG = {"default": {"FOO": "BALONEY"}}


@pytest.mark.parametrize(
    "config_object",
    [DEFAULT_CONFIG],
    indirect=["config_object"],
)
def test_apply_config_from_directory(config_object, tmpdir):
    config_setting = tmpdir.join("FOO")
    with open(config_setting, "w") as conf_file:
        conf_file.write("MAYO")

    apply_config_from_directory(tmpdir, config_object)
    assert config_object.get("default", "FOO") == "MAYO"


@pytest.mark.parametrize(
    "config_object",
    [DEFAULT_CONFIG],
    indirect=["config_object"],
)
def test_apply_config_from_directory_skips_unknown_settings(config_object, tmpdir):
    config_setting = tmpdir.join("FLARF")
    with open(config_setting, "w") as conf_file:
        conf_file.write("MAYO")

    apply_config_from_directory(tmpdir, config_object)
    assert "FLARF" not in config_object.options("default")


@pytest.mark.parametrize(
    "config_object",
    [DEFAULT_CONFIG],
    indirect=["config_object"],
)
def test_apply_config_from_environment(config_object, monkeypatch):
    monkeypatch.setenv("FOO", "MAYO")
    apply_config_from_environment(config_object)
    assert config_object.get("default", "FOO") == "MAYO"


@pytest.mark.parametrize(
    "config_object",
    [DEFAULT_CONFIG],
    indirect=["config_object"],
)
def test_apply_config_from_environment_skips_unknown_settings(
    config_object, monkeypatch
):
    monkeypatch.setenv("FLARF", "MAYO")
    apply_config_from_environment(config_object)
    assert "FLARF" not in config_object.options("default")


@pytest.mark.parametrize(
    "config_object",
    [
        {"default": {"CSP": "mock"}, "hybrid": {"HYBRID_OPTION": "value"}},
        {"default": {"CSP": "hybrid"}, "hybrid": {"HYBRID_OPTION": "value"}},
    ],
    indirect=["config_object"],
)
def test_apply_hybrid_config_options(config_object):
    apply_hybrid_config_options(config_object)
    assert config_object.get("default", "HYBRID_OPTION") == "value"


class TestMakeConfig:
    def test_redis_ssl_connection(self):
        config = make_config({"default": {"REDIS_TLS": True}})
        uri = config.get("REDIS_URI")
        assert "rediss" in uri
        assert "ssl_cert_reqs" in uri

    def test_non_redis_ssl_connection(self):
        config = make_config({"default": {"REDIS_TLS": False}})
        uri = config.get("REDIS_URI")
        assert "rediss" not in uri
        assert "redis" in uri
        assert "ssl_cert_reqs" not in uri
