from atat.routes.routes_helpers import match_url_pattern


def test_match_url_patter():
    # checking good urls
    assert not any(
        x is None
        for x in (
            match_url_pattern("/home"),
            match_url_pattern("/login", "POST"),
            match_url_pattern("/login"),
        )
    )
    # checking bad urls
    assert all(
        x is None
        for x in (
            match_url_pattern("http://not.a.real.url.gov/#"),
            match_url_pattern("http://not.a.real.url.gov/#", "POST"),
            match_url_pattern("/home", "POST"),
        )
    )
