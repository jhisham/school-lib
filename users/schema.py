import graphene
import django_filters
from graphql_jwt.decorators import login_required, permission_required, staff_member_required, superuser_required, user_passes_test
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _


# get the user model
User = get_user_model()

class UserFilter(django_filters.FilterSet):
    """
    Relay allows filtering of data by using filters.
    The fields defined are the filter sets which can be used as arguments when querying the data.
    """
    class Meta:
        model = User
        fields = "__all__"
        
        
class UserNode(DjangoObjectType):
    """
    The Node class exposes data in a Relay framework.
    The data structure is a bit different from the normal GraphQL data structure.
    The data is exposed through Edges and Nodes.
    Edges: Represents a collection of nodes, which has pagination properties.
    Node: Are the final object or and edge for a new list of objects.
    """
    class Meta:
        model = User
        interfaces = (graphene.relay.Node,)
        exclude = ('password',)
        
        
class UserFilterConnectionField(DjangoFilterConnectionField):
    """
    Subclass of DjangoFilterConnectionField.
    Defines the connection field, which implements the pagination structure.
    """
    
    class Meta:
        model = User
        filter_class = UserFilter
        
        
class UserQuery(graphene.ObjectType):
    me = graphene.Field(UserNode)
    user = graphene.relay.Node.Field(UserNode)
    users = UserFilterConnectionField(UserNode, filterset_class=UserFilter)
    
    def resolve_me(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception(_('You have to be logged in to do that'))
        return user
    