"""Test case for autocomplete implementations."""

import uuid
import time

from django import VERSION
from django.contrib.contenttypes.models import ContentType
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.urlresolvers import reverse
from django.utils import six

from selenium.common.exceptions import NoSuchElementException

from splinter import Browser
from splinter.exceptions import ElementDoesNotExist
import unittest


GLOBAL_BROWSER = None


class AutocompleteTestCase(StaticLiveServerTestCase):
    """Provide a class-persistent selenium instance and assertions."""

    @classmethod
    def setUpClass(cls):
        global GLOBAL_BROWSER

        if GLOBAL_BROWSER is None:
            GLOBAL_BROWSER = Browser()
        cls.browser = GLOBAL_BROWSER

        super(AutocompleteTestCase, cls).setUpClass()

    def get(self, url):
        self.browser.visit('%s%s' % (
            self.live_server_url,
            url
        ))

        if '/admin/login/' in self.browser.url:
            # Should be pre-filled by HTML template
            # self.browser.fill('username', 'test')
            # self.browser.fill('password', 'test')
            self.browser.find_by_value('Log in').click()

    def click(self, selector):
        self.browser.find_by_css(selector).click()

    def enter_text(self, selector, text):
        self.browser.find_by_css(selector).type(text)

    def assert_not_visible(self, selector):
        e = self.browser.find_by_css(selector)
        assert not e or e.visible is False

    def assert_visible(self, selector):
        assert self.browser.find_by_css(selector).visible is True

    def wait_until_not_visible(self, selector):
        e = self.browser.find_by_css(selector)
        # WARNING, infinitie loop
        try:
            i = 0

            while e or e[0].visible:
                time.sleep(0.1)
                i += 1

                if i > 1000:
                    self.fail()
        except ElementDoesNotExist:
            # Element is gone !
            return

    def wait_until_element_contains(self, selector, content):
        i = 0

        while content not in self.browser.find_by_css(selector).html:
            time.sleep(0.1)
            i += 1

            if i > 1000:
                self.fail()


class AdminMixin(object):
    """Mixin for tests that should happen in ModelAdmin."""

    def get_modeladmin_url(self, action, **kwargs):
        """Return a modeladmin url for a model and action."""
        return reverse('admin:%s_%s_%s' % (
            self.model._meta.app_label,
            self.model._meta.model_name,
            action
        ), kwargs=kwargs)

    def fill_name(self):
        """Fill in the name input."""
        i = self.id()
        half = int(len(i))
        not_id = i[half:] + i[:half]
        self.browser.fill('name', not_id)


class OptionMixin(object):
    """Mixin to make a unique option per test."""

    def create_option(self):
        """Create a unique option from self.model into self.option."""
        unique_name = six.text_type(uuid.uuid1())

        if VERSION < (1, 10):
            # Support for the name to be changed through a popup in the admin.
            unique_name = unique_name.replace('-', '')

        option, created = self.model.objects.get_or_create(
            name=unique_name)
        return option


class ContentTypeOptionMixin(OptionMixin):
    """Same as option mixin, with content type."""

    def create_option(self):
        """Return option, content type."""
        option = super(ContentTypeOptionMixin, self).create_option()
        ctype = ContentType.objects.get_for_model(option)
        return option, ctype
