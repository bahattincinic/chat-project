from haystack import indexes
from account.models import User


class UserSearchIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    username = indexes.EdgeNgramField(model_attr='username', boost=1.125)
    bio = indexes.EdgeNgramField(model_attr='bio', null=True)

    def get_model(self):
        return User

    def index_queryset(self, using=None):
        return self.get_model().actives.all()


