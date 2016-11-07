from __future__ import absolute_import


# TODO Entity Component System design for interface loop. cf https://pypi.python.org/pypi/esper (py3 + py2 in fork)
# Entities are transients (ex : for ROS : pubs, subs, svcs, params, and more can be added),
# Systems store logic about when/how a transient should be represented in the interface.
# GOALS : clarity, testability and flexibility
class BaseInterface(object):

    """
    BaseInterface.
    Assumption : we only deal with absolute names here. The users should resolve them
    """

    # Abstract methods to override for topics ("pub/sub type" communication channel)
    def get_publisher_list(self):  # function returning all topics available on the system
        return self.publishers_pool.get_transients_available()

    def publisher_type_resolver(self, topic_name):  # function resolving the type of a topic
        """
        :param topic_name: the name of the topic
        :return: returns None if the topic cannot be found. Properly except in all other unexpected events.
        """
        return self.publishers_pool.transient_type_resolver(topic_name)

    def PublisherMaker(self, topic_name, topic_type, *args, **kwargs):  # the topic class implementation
        return self.publishers_pool.TransientMaker(topic_name, topic_type, *args, **kwargs)

    def PublisherCleaner(self, topic):  # the topic class implementation
        return self.publishers_pool.TransientCleaner(topic)

    # Abstract methods to override for topics ("pub/sub type" communication channel)
    def get_subscriber_list(self):  # function returning all topics available on the system
        return self.subscribers_pool.get_transients_available()

    def subscriber_type_resolver(self, topic_name):  # function resolving the type of a topic
        """
        :param topic_name: the name of the topic
        :return: returns None if the topic cannot be found. Properly except in all other unexpected events.
        """
        return self.subscribers_pool.transient_type_resolver(topic_name)

    def SubscriberMaker(self, topic_name, topic_type, *args, **kwargs):  # the topic class implementation
        return self.subscribers_pool.TransientMaker(topic_name, topic_type, *args, **kwargs)

    def SubscriberCleaner(self, topic):  # the topic class implementation
        return self.subscribers_pool.TransientCleaner(topic)

    def get_svc_list(self):  # function returning all services available on the system
        return self.services_pool.get_transients_available()

    def service_type_resolver(self, service_name):  # function resolving the type of a service
        """
        :param service_name: the name of the service
        :return: returns None if the type cannot be found. Properly except in all other unexpected events.
        """
        return self.services_pool.transient_type_resolver(service_name)

    def ServiceMaker(self, service_name, service_type, *args, **kwargs):  # the service class implementation
        return self.services_pool.TransientMaker(service_name, service_type, *args, **kwargs)

    def ServiceCleaner(self, service):  # the service class implementation
        return self.services_pool.TransientCleaner(service)

    # Abstract methods to override for topics ("pub/sub type" communication channel)
    def get_topic_list(self):  # function returning all topics available on the system
        return self.topics_pool.get_transients_available()

    def topic_type_resolver(self, topic_name):  # function resolving the type of a topic
        """
        :param topic_name: the name of the topic
        :return: returns None if the topic cannot be found. Properly except in all other unexpected events.
        """
        return self.topics_pool.transient_type_resolver(topic_name)

    def TopicMaker(self, topic_name, topic_type, *args, **kwargs):  # the topic class implementation
        return self.topics_pool.TransientMaker(topic_name, topic_type, *args, **kwargs)

    def TopicCleaner(self, topic):  # the topic class implementation
        return self.topics_pool.TransientCleaner(topic)

    # Abstract methods to override for params ( "global" get/set objects )
    def get_param_list(self):  # function returning all topics available on the system
        return self.params_pool.get_transients_available()

    def param_type_resolver(self, param_name):  # function resolving the type of a topic
        return self.params_pool.transient_type_resolver(param_name)

    def ParamMaker(self, param_name, param_type, *args, **kwargs):  # the param class implementation
        return self.params_pool.TransientMaker(param_name, param_type, *args, **kwargs)

    def ParamCleaner(self, param):  # the param class implementation
        return self.params_pool.TransientCleaner(param)

    def __init__(self, publishers_pool, subscribers_pool, services_pool, params_pool):
        """
        Initializes the interface instance, to expose services, topics, and params
        """
        # Current transients exposed, i.e. those which are
        # active in the system.

        self.params_pool = params_pool
        self.services_pool = services_pool
        self.subscribers_pool = subscribers_pool
        self.publishers_pool = publishers_pool

    # REQUESTED
    @property
    def publishers_args(self):
        return self.publishers_pool.transients_args

    @property
    def subscribers_args(self):
        return self.subscribers_pool.transients_args

    @property
    def services_args(self):
        return self.services_pool.transients_args

    @property
    def params_args(self):
        return self.params_pool.transients_args

    # AVAILABLE
    @property
    def publishers_available(self):
        return self.publishers_pool.available

    @property
    def subscribers_available(self):
        return self.subscribers_pool.available

    @property
    def services_available(self):
        return self.services_pool.available

    @property
    def params_available(self):
        return self.params_pool.available

    # INTERFACED
    @property
    def publishers(self):
        return self.publishers_pool.transients

    @property
    def subscribers(self):
        return self.subscribers_pool.transients

    @property
    def services(self):
        return self.services_pool.transients

    @property
    def params(self):
        return self.params_pool.transients

    # EXPOSE
    def expose_publishers(self, tpc_regex):
        return self.publishers_pool.expose_transients_regex(tpc_regex)

    def expose_subscribers(self, tpc_regex):
        return self.subscribers_pool.expose_transients_regex(tpc_regex)

    def expose_services(self, svc_regex):
        return self.services_pool.expose_transients_regex(svc_regex)

    def expose_params(self, prm_regex):
        return self.params_pool.expose_transients_regex(prm_regex)

    #CHANGE DIFF
    def publishers_change_diff(self, appeared, gone):
        return self.publishers_pool.transient_change_diff(appeared, gone)

    def subscribers_change_diff(self, appeared, gone):
        return self.subscribers_pool.transient_change_diff(appeared, gone)

    def services_change_diff(self, appeared, gone):
        return self.services_pool.transient_change_diff(appeared, gone)

    def params_change_diff(self, appeared, gone):
        return self.params_pool.transient_change_diff(appeared, gone)

    #CHANGE DETECT
    def publishers_change_detect(self):
        return self.publishers_pool.transient_change_detect()

    def subscribers_change_detect(self):
        return self.subscribers_pool.transient_change_detect()

    def services_change_detect(self):
        return self.services_pool.transient_change_detect()

    def param_change_detect(self):
        return self.params_pool.transient_change_detect()

    #UPDATE
    def update_publishers(self, add_names, remove_names):
        return self.publishers_pool.update_transients(add_names, remove_names)

    def update_subscribers(self, add_names, remove_names):
        return self.subscribers_pool.update_transients(add_names, remove_names)

    def update_services(self, add_names, remove_names):
        return self.services_pool.update_transients(add_names, remove_names)

    def update_params(self, add_names, remove_names):
        return self.params_pool.update_transients(add_names, remove_names)

    # TODO : "wait_for_it" methods that waits for hte detection of a topic/service on the system
    # TODO : Should return a future so use can decide to wait on it or not
    # TODO : Maybe similar to a async_detect ( hooked up to the detected transient, not the exposed ones )
    # TODO : Exposed interface is for direct control flow => async not really needed
    # TODO : Detect/Update interface is inversed control flow ( from update loop ) => Needed
