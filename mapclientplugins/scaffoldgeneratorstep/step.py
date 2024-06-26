
"""
MAP Client Plugin Step
"""
import json
import os

from cmlibs.utils.zinc.general import ChangeManager
from cmlibs.zinc.context import Context
from scaffoldmaker import scaffolds
from mapclient.mountpoints.workflowstep import WorkflowStepMountPoint
from mapclientplugins.scaffoldgeneratorstep.configuredialog import ConfigureDialog


class scaffoldgeneratorStep(WorkflowStepMountPoint):
    """
    Skeleton step which is intended to be a helpful starting point
    for new steps.
    """

    def __init__(self, location):
        super(scaffoldgeneratorStep, self).__init__('scaffold generator', location)
        self._configured = False  # A step cannot be executed until it has been configured.
        self._category = 'General'
        # Add any other initialisation code here:
        # Ports:
        self.addPort([('http://physiomeproject.org/workflow/1.0/rdf-schema#port',
                       'http://physiomeproject.org/workflow/1.0/rdf-schema#uses',
                       'http://physiomeproject.org/workflow/1.0/rdf-schema#file_location'),
                      ('http://physiomeproject.org/workflow/1.0/rdf-schema#port',
                       'http://physiomeproject.org/workflow/1.0/rdf-schema#uses-list-of',
                       'http://physiomeproject.org/workflow/1.0/rdf-schema#file_location')
                      ])
        self.addPort(('http://physiomeproject.org/workflow/1.0/rdf-schema#port',
                      'http://physiomeproject.org/workflow/1.0/rdf-schema#provides-list-of',
                      'http://physiomeproject.org/workflow/1.0/rdf-schema#file_location'))
        # Port data:
        self._portData0 = None  # http://physiomeproject.org/workflow/1.0/rdf-schema#file_location
        self._portData1 = None  # http://physiomeproject.org/workflow/1.0/rdf-schema#file_location
        self._context = Context("scaffoldGenerator")
        self._region = self._context.getDefaultRegion()
        # Config:
        self._config = {
            'identifier': '',
        }

    def execute(self):
        """
        Add your code here that will kick off the execution of the step.
        Make sure you call the _doneExecution() method when finished.  This method
        may be connected up to a button in a widget for example.
        """
        # Put your execute step code here before calling the '_doneExecution' method.
        self._portData1 = []

        with ChangeManager(self._region):
            for file in self._portData0:
                with open(file) as f:
                    c = json.load(f)

                if "scaffold_settings" in c and "scaffoldPackage" in c["scaffold_settings"]:
                    sm = scaffolds.Scaffolds_decodeJSON(c["scaffold_settings"]["scaffoldPackage"])
                    region = self._region.createRegion()
                    sm.generate(region)

                    filename = os.path.splitext(file)[0] + '.exf'
                    region.writeFile(filename)
                    self._portData1.append(filename)
                    del region

        self._doneExecution()

    def setPortData(self, index, dataIn):
        """
        Add your code here that will set the appropriate objects for this step.
        The index is the index of the port in the port list.  If there is only one
        uses port for this step then the index can be ignored.

        :param index: Index of the port to return.
        :param dataIn: The data to set for the port at the given index.
        """
        if not isinstance(dataIn, list):
            dataIn = [dataIn]
        self._portData0 = dataIn  # http://physiomeproject.org/workflow/1.0/rdf-schema#file_location

    def getPortData(self, index):
        """
        Add your code here that will return the appropriate objects for this step.
        The index is the index of the port in the port list.  If there is only one
        provides port for this step then the index can be ignored.

        :param index: Index of the port to return.
        """
        return self._portData1  # http://physiomeproject.org/workflow/1.0/rdf-schema#file_location

    def configure(self):
        """
        This function will be called when the configure icon on the step is
        clicked.  It is appropriate to display a configuration dialog at this
        time.  If the conditions for the configuration of this step are complete
        then set:
            self._configured = True
        """
        dlg = ConfigureDialog(self._main_window)
        dlg.identifierOccursCount = self._identifierOccursCount
        dlg.setConfig(self._config)
        dlg.validate()
        dlg.setModal(True)

        if dlg.exec_():
            self._config = dlg.getConfig()

        self._configured = dlg.validate()
        self._configuredObserver()

    def getIdentifier(self):
        """
        The identifier is a string that must be unique within a workflow.
        """
        return self._config['identifier']

    def setIdentifier(self, identifier):
        """
        The framework will set the identifier for this step when it is loaded.
        """
        self._config['identifier'] = identifier

    def serialize(self):
        """
        Add code to serialize this step to string.  This method should
        implement the opposite of 'deserialize'.
        """
        return json.dumps(self._config, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def deserialize(self, string):
        """
        Add code to deserialize this step from string.  This method should
        implement the opposite of 'serialize'.

        :param string: JSON representation of the configuration in a string.
        """
        self._config.update(json.loads(string))

        d = ConfigureDialog()
        d.identifierOccursCount = self._identifierOccursCount
        d.setConfig(self._config)
        self._configured = d.validate()


