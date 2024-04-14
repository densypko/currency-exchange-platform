from django.test import TestCase

from ..factories import ProviderFactory


class TestProvider(TestCase):

    def test_provider_attributes(self):
        provider = ProviderFactory(
            name='Test Provider',
            priority=1,
            adapter_code="""
def custom_function(x, y):
    return x + y
return_value = custom_function(2, 3)
"""
        )

        self.assertEqual(provider.name, 'Test Provider')
        self.assertEqual(provider.priority, 1)
        self.assertEqual(provider.adapter_code.strip(), """
def custom_function(x, y):
    return x + y
return_value = custom_function(2, 3)
""".strip())

    def test_execute_adapter_code(self):
        provider = ProviderFactory(
            name='Test Provider',
            priority=1,
            adapter_code="""
def custom_function(x, y):
    return x + y
return_value = custom_function(2, 3)
"""
        )

        context = {}
        result = provider.execute_adapter_code(context)
        self.assertEqual(result, 5)
