from __future__ import absolute_import

import ast
import importlib
import json
import os
import logging
import time
import abc

import pyzmp

from .exceptions import PyrosException
from .baseinterface import BaseInterface

from pyros_setup import ConfigHandler


class PyrosBase(pyzmp.Node):
    """
    Base Interface in pure python ( No ROS needed ).
    Encapsulate another process for isolated execution
    Also handles a package bound configuration (since the child process might want to reload it in its own memory space)
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self,
                 name=None,
                 interface_class=None,
                 context_manager=None,
                 args=None,
                 kwargs=None,
                 instance_path=None,
                 instance_relative_config=True,
                 root_path=None,
                 default_config=None):
        """
        :param name: name of the node
        :param interface_class: the class of the interface to instantiate (in child process)
                OR a tuple (module_name, class_name), useful if the module should be imported only in child process
                OR a tuple (package_name, module_name, class_name), usseful if the module name is relative
                The interface class should be a child of BaseInterface.
        :param context_manager: a context manager to enter when starting, and exit when the node stops
        :param args: the args to pass to the setup function (that instantiate the interface class)
        :param kwargs: the kwargs to pass to the setup function (that instantiate the interface class)
        :param instance_path: the path to the running instance of the running app. configurations and resources will be expected there.
                By default it will automatically use a suitable 'instance/' folder.
                The configuration strategy follows flask configuration strategy.
                More information there : http://flask.pocoo.org/docs/0.10/config/#instance-folders
        :param instance_relative_config: whether the configuration is relative to the instance_path (if not it will be relative to the root_path)
        :param root_path: the root_path. by default the package location.
        :param default_config: a dict containing the values to use as default configuration values
        :return:
        """
        super(PyrosBase, self).__init__(name or 'pyros', context_manager=context_manager, args=args or (), kwargs=kwargs or {})

        self.last_update = 0
        self.update_interval = 1  # seconds to wait between each update

        # we delegate config related behavior (including defaults)
        self.config_handler = ConfigHandler(
            name or 'pyros',
            instance_path=instance_path,
            instance_relative_config=instance_relative_config,
            root_path=root_path,
            default_config=default_config,
        )

        self.provides(self.msg_build)
        self.provides(self.topic)
        self.provides(self.topics)
        self.provides(self.service)
        self.provides(self.services)
        self.provides(self.param)
        self.provides(self.params)
        self.provides(self.setup)

        if not isinstance(interface_class, tuple) and not issubclass(interface_class, BaseInterface):
            raise PyrosException("The interface passed to the Node is neither a tuple nor a subclass of BaseInterface")
        else:
            self.interface_class = interface_class
        self.interface = None  # delayed interface creation
        # interface should be created in child process only to maintain isolation.

    #
    # Delegating configuration management
    #

    @property
    def import_name(self):
        return self.config_handler.import_name

    @property
    def config(self):
        return self.config_handler.config

    @property
    def instance_path(self):
        return self.config_handler.instance_path

    @property
    def instance_relative_config(self):
        return self.config_handler.instance_relative_config

    @property
    def root_path(self):
        return self.config_handler.root_path

    def configure(self, config=None):
        # We default to using a config file named after the import_name:
        config = config or self.name + '.cfg'
        self.config_handler.configure(config)
        return self

    #
    # These should match the design of PyrosClient and Protocol so we are consistent between pipe and python API
    #
    @abc.abstractmethod
    def msg_build(self, name):
        return

    @abc.abstractmethod
    def topic(self, name, msg_content=None):
        return

    @abc.abstractmethod
    def topics(self):
        return

    # a simple string echo service
    @abc.abstractmethod
    def service(self, name, rqst_content=None):
        return

    @abc.abstractmethod
    def services(self):
        return

    @abc.abstractmethod
    def param(self, name, value=None):
        return

    @abc.abstractmethod
    def params(self):
        return

    @abc.abstractmethod
    def setup(self, *args, **kwargs):
        """
        Dynamically reset the interface to expose the services / topics / params whose names are passed as args
        The interface class can be specified with a module to be dynamically imported
        :param services:
        :param topics:
        :param params:
        :return:
        """

        # We can now import RosInterface and setup will be done ( we re in another process ).
        # TODO : context to make it cleaner (maybe use zmp.Node context ?)
        if isinstance(self.interface_class, tuple):
            m = None
            class_name = self.interface_class[-1]  # last element is always the class_name
            if len(self.interface_class) >= 3:
                # load the relative module, will raise ImportError if module cannot be loaded
                m = importlib.import_module(self.interface_class[1], self.interface_class[0])
            elif len(self.interface_class) == 2:
                # load the relative module, will raise ImportError if module cannot be loaded
                m = importlib.import_module(self.interface_class[1])
            # get the class, will raise AttributeError if class cannot be found
            self.interface_class = getattr(m, class_name)

        if not issubclass(self.interface_class, BaseInterface):
            raise PyrosException("The interface class is not a subclass of BaseInterface. Aborting Setup.")

        self.interface = self.interface_class(*args, **kwargs)

    # TODO : change this running interface to have a delegate zmp node ( instead of motherclass )
    # Maybe this will help when passing custom argument from child classes to child processes...
    def run(self):
        """
        Running in a zmp.Node process, providing zmp.services
        """

        logging.debug("pyros node running, zmp[{name}] pid[{pid}]".format(name=self.name, pid=os.getpid()))

        # Initialization ( here in child )
        # None passed in argument means empty list ( different than reinit meaning )

        # getting preset params from parent process memory
        self.setup(*self._args, **self._kwargs)

        super(PyrosBase, self).run()

        logging.debug("pyros node shutdown, zmp[{name}] pid[{pid}]".format(name=self.name, pid=os.getpid()))

    def shutdown(self, join=True):
        """
        Clean shutdown of the node.
        :param join: optionally wait for the process to end (default : True)
        :return: None
        """

        super(PyrosBase, self).shutdown(join)

    def update(self, timedelta):
        """
        Update function to call from a looping thread.
        :param timedelta: the time past since the last update call
        """
        self.last_update += timedelta
        if self.last_update > self.update_interval:
            self.last_update = 0
            self.update_throttled()

    def update_throttled(self):
        """
        An update method that is only run every self.update_interval
        It updates the interface state
        :return:
        """
        self.interface.update()
