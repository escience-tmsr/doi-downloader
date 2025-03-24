from doi_downloader import loader as ld

def test_loading_plugins():
    plugins = ld.plugins
    assert plugins
