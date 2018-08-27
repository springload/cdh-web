from cdhweb.resources.templatetags.cdh_tags import url_to_icon

def test_url_to_icon():
    assert url_to_icon('/people/staff/') == 'people'
    assert url_to_icon('/projects/') == 'folder'
    assert url_to_icon('/events/') == 'cal'
    assert url_to_icon('/contact/') == 'convo'
    assert url_to_icon('/grants/seed-grant/') == 'seed'
    assert url_to_icon('/graduate-fellowships/') == 'medal'
    assert url_to_icon('/grants/') == 'grant'
    assert url_to_icon('/unknown/') == ''
