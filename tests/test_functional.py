import mock
from . import FunctionalTest
from cv_ostf_adapter.db import models


class TestRootController(FunctionalTest):
    def test_tests_get_succeeds(self):
        response = self.app.get('/tests')
        assert response.status_int == 200

    def test_testsets_get_succeeds(self):
        response = self.app.get('/testsets')
        assert response.status_int == 200

    def test_testruns_get_succeeds(self):
        response = self.app.get('/testruns')
        assert response.status_int == 200

    def test_get(self):
        response = self.app.get('/', expect_errors=True)
        assert response.status_int == 404

    def test_run(self):
        response = self.app.post('/tests/123/run')
        assert response.status_int == 202

    def test_get_by_id(self):
        response = self.app.get('/tests/123')
        assert response.status_int == 200

    def test_query(self):
        response = self.app.get('/tests/query?name=somename&group=somegroup')
        print response
        self.fail()


class TestModels(FunctionalTest):
    def test_get_all_testsets_returns_list(self):
        assert isinstance(models.get_all_tests(), list)

    def test_get_returns_list(self):
        id = mock.Mock()
        assert isinstance(models.get(id), list)