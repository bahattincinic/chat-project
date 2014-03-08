from haystack import indexes
from network.models import Network


class NetworkSearchIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')
    
    def get_model(self):
        return Network

    def index_queryset(self, using=None):
        return Network.objects.all()

