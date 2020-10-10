import pytest

@pytest.mark.parametrize(
    ('company_number', 'name'),
    (
        ('03033654', 'Centrica PLC'),
        ('00660457', 'Merck Chemicals')
    )
)
def test_get_companies_house_data(client, auth, company_number, name):
    url = '/companies_house/' + company_number
    auth.login()
    with client:
        response = client.get(url)
        assert response.status_code == 200
        assert name in str(response.data)
