from bs4 import BeautifulSoup
import pytest
import yaml
import requests
from collections import namedtuple


Site = namedtuple('Site', 'homepage redirect title today')

BASE_SITE = "https://{code}.wikipedia.org"

def load_sites():
    with open("sites.yaml") as f:
        params = yaml.load(f)
    for code, data in params['sites'].items():
        data['homepage'] = BASE_SITE.format(code=code)
        yield Site(**data)


@pytest.mark.parametrize("site", load_sites())
def test_site_redirect(site):
    r = requests.head(site.homepage, allow_redirects=True)
    assert r.ok
    redirect, = r.history
    assert redirect.is_permanent_redirect
    assert len(r.history) == 1
    assert r.url == site.redirect


@pytest.mark.parametrize("site", load_sites())
def test_home_today_article(site):
    r = requests.get(site.homepage)
    assert r.ok, "Could not load site"
    soup = BeautifulSoup(r.content, 'html.parser')
    assert site.title == soup.title.string
    assert soup.find(id=site.today)
