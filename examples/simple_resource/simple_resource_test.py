# coding=utf-8
"""
Simple Lambda Handler
"""
import unittest
from lbz.dev.test import Client

from simple_resource import HelloWorld


class PublicTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = Client(resource=HelloWorld)

    def test_filter_queries_all_active_when_no_params(self):
        data = self.client.get("/").to_dict()["body"]
        self.assertEqual(data, '{"message":"HelloWorld"}')
