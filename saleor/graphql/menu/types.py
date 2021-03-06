from textwrap import dedent

import graphene
import graphene_django_optimizer as gql_optimizer
from django.db.models import Prefetch
from graphene import relay

from ...menu import models
from ..core.connection import CountableDjangoObjectType
from ..translations.enums import LanguageCodeEnum
from ..translations.resolvers import resolve_translation
from ..translations.types import MenuItemTranslation


def prefetch_menus(info, *args, **kwargs):
    qs = models.MenuItem.objects.filter(level=0)
    return Prefetch(
        'items', queryset=gql_optimizer.query(qs, info),
        to_attr='prefetched_items')


class Menu(CountableDjangoObjectType):
    children = graphene.List(
        lambda: MenuItem, required=True,
        description='List of menu item children items')
    items = gql_optimizer.field(
        graphene.List(lambda: MenuItem),
        prefetch_related=prefetch_menus)

    class Meta:
        description = dedent("""Represents a single menu - an object that is used
        to help navigate through the store.""")
        interfaces = [relay.Node]
        only_fields = ['id', 'name']
        model = models.Menu

    def resolve_items(self, info, **kwargs):
        if hasattr(self, 'prefetched_items'):
            return self.prefetched_items
        return self.items.filter(level=0)


class MenuItem(CountableDjangoObjectType):
    children = gql_optimizer.field(
        graphene.List(lambda: MenuItem), model_field='children')
    url = graphene.String(description='URL to the menu item.')
    translation = graphene.Field(
        MenuItemTranslation,
        language_code=graphene.Argument(
            LanguageCodeEnum,
            description='A language code to return the translation for.',
            required=True),
        description=(
            'Returns translated Menu item fields '
            'for the given language code.'),
        resolver=resolve_translation)

    class Meta:
        description = dedent("""Represents a single item of the related menu.
        Can store categories, collection or pages.""")
        interfaces = [relay.Node]
        only_fields = [
            'category', 'collection', 'id', 'level', 'menu', 'name', 'page',
            'parent']
        model = models.MenuItem

    def resolve_children(self, info, **kwargs):
        return self.children.all()
