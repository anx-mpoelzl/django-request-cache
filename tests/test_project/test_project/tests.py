# -*- coding: utf-8 -*-
from django.test import TestCase
from django_request_cache import cache_for_request
from django.contrib.auth.models import User
from contextlib import redirect_stdout
import unittest.mock as mock
import io


@cache_for_request
def method_to_cache(a, b, c):
    print('stdout')
    return a * b * c


helper = mock.create_autospec(method_to_cache)


class RequestCacheTests(TestCase):
    """
    Test for request cache functionality.
    """
    def test_method_calls(self):
        """
        Ensure that the method gets called several times.
        """
        User.objects.create_superuser('admin', 'foo@foo.com', 'admin')
        self.client.login(username='admin', password='admin')

        helper(1, 2, 3)
        helper.assert_called_once_with(1, 2, 3)
        self.assertEqual(helper.call_count, 1)

        helper(1, 2, 3)
        helper.assert_called_with(1, 2, 3)
        self.assertEqual(helper.call_count, 2)

        helper(3, 2, 1)
        helper.assert_called_once_with(3, 2, 1)
        self.assertEqual(helper.call_count, 3)

    def test_request_cache(self):
        """
        Ensure that the request cache prevents multiple calls.
        """
        User.objects.create_superuser('admin', 'foo@foo.com', 'admin')
        self.client.login(username='admin', password='admin')

        with io.StringIO() as buffer, redirect_stdout(buffer):
            method_to_cache(1, 2, 3)
            buffer.seek(0)
            output = buffer.getvalue()
            self.assertEqual(output, 'stdout\n')

            method_to_cache(1, 2, 3)
            buffer.seek(0)
            output = buffer.getvalue()
            self.assertEqual(output, 'stdout\n')

            method_to_cache(4, 5, 6)
            buffer.seek(0)
            output = buffer.getvalue()
            self.assertEqual(output, 'stdout\nstdout\n')
