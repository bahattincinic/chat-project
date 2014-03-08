from haystack import signals


class QueuedSignalProcessor(signals.RealtimeSignalProcessor):
    def handle_save(self, sender, instance, **kwargs):
        print 'handles save'

    def handle_delete(self, sender, instance, **kwargs):
        print 'handles delete'

