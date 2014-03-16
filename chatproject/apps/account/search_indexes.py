from haystack import indexes
from account.models import User


class UserSearchIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    username = indexes.CharField(model_attr='username')
    bio = indexes.CharField(model_attr='bio', null=True)

    def get_model(self):
        return User

    def index_queryset(self, using=None):
        return self.get_model().actives.all()


