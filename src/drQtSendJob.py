#!/usr/bin/env python

import os, sys
import getpass

import PyQt4.QtGui as QtGui
import PyQt4.QtCore as QtCore
import PyQt4.QtWebKit as QtWebKit


try:
    import DrQueue
    from DrQueue import Job as DrQueueJob
    from DrQueue import Client as DrQueueClient
    from DrQueue import ComputerPool as DrQueueComputerPool
except:
    raise "DrQueue module not found! Please check DrQueueIPython installation."


from lib.utils import sendJob_widget_class
from lib.utils import sendJob_base_class
from lib.utils import icons_path

local_path = os.path.dirname(__file__)


class SendJob(sendJob_widget_class, sendJob_base_class):
    def __init__(self, parent = None):
        """Initialize window."""
        super(SendJob, self).__init__(parent)
        # setup user interface
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(os.path.join(icons_path, "main.svg")))
        self.setWindowTitle("drQt - Create New Job")
        # create client connection
        self.client = DrQueueClient()
        # fill form with default values
        self.set_default_values()


    def set_default_values(self):
        """Set default values on form elements"""
        url = QtCore.QUrl("lib/ui/about.html")
        self.webView.load(url)
        self.owner_box.setText(getpass.getuser())
        # load list of supported renderers from DrQueue module
        self.renderer_box.insertItem (0, "Choose renderer")
        renderers = DrQueue.supported_renderers
        i = 1
        for renderer in renderers:
            self.renderer_box.insertItem (i, renderer)
            i += 1
        # load list of available pools
        self.pool_box.insertItem (0, "Choose pool")
        pools = DrQueueComputerPool.query_poolnames()
        i = 1
        for pool in pools:
            self.pool_box.insertItem (i, pool)
            i += 1
        # load list of supported os from DrQueue module
        self.os_box.insertItem (0, "Choose OS")
        supported_os = DrQueue.supported_os
        i = 1
        for os in supported_os:
            self.os_box.insertItem (i, os)
            i += 1
        # load list of running jobs
        self.depend_box.insertItem (0, "Choose running job")
        running_jobs = self.client.query_running_job_list()
        i = 1
        for job in running_jobs:
            self.depend_box.insertItem (i, job)
            i += 1
        # filter for file chooser
        self.scenefile_filter = "*"


    def openFileChooser(self):
        """Open file chooser widget."""
        fileName = QtGui.QFileDialog.getOpenFileName(self, "Choose scenefile", self.scenefile_box.text(), self.scenefile_filter)
        print(fileName)
        self.scenefile_box.setText(fileName)
        self.show()
        self.raise_()


    def rendererChanged(self):
        """Change extra options when another renderer is selected."""
        active = str(self.renderer_box.currentText())
        if active == "3delight":
            self.options_box.setText("None")
            self.scenefile_filter = "*.rib"
        elif active == "3dsmax":
            self.options_box.setText("None")
            self.scenefile_filter = "*.max"
        elif active == "blender":
            self.options_box.setText("{'rendertype':'animation'}")
            self.scenefile_filter = "*.blend"
        elif active == "maya":
            self.options_box.setText("None")
            self.scenefile_filter = "*.ma *.mb"
        elif active == "mentalray":
            self.options_box.setText("None")
            self.scenefile_filter = "*.mi"
        else:
            self.options_box.setText("None")
            self.scenefile_filter = "*"
        print(active)


    def accept(self):
        """Take all form values, create job and send it to IPython."""
        print("creating job ...")
        # fetch values from form elements
        name = str(self.name_box.text())
        startframe = int(self.startframe_box.value())
        endframe = int(self.endframe_box.value())
        blocksize = int(self.blocksize_box.value())
        renderer = str(self.renderer_box.currentText())
        scenefile = str(self.scenefile_box.text())
        retries = int(self.retries_box.value())
        owner = str(self.owner_box.text())
        pool = str(self.pool_box.currentText())
        # pool needs to have a real value
        if pool == "Choose pool":
            pool = None
        os = str(self.os_box.currentText())
        # os needs to have a real value
        if os == "Choose OS":
            os = None
        depend = str(self.depend_box.currentText())
        # depend needs to have a real value
        if depend == "Choose running job":
            depend = None
        minram = int(self.minram_box.value())
        mincores = int(self.mincores_box.value())
        # options need to come in form of a Python dict
        options = eval(str(self.options_box.text()))
        # create job object
        try:
            # TODO: add os, email, min ram, min cores, depend on job
            job = DrQueueJob(name, startframe, endframe, blocksize, renderer, scenefile, retries, owner, pool, options)
        except ValueError as strerror:
            message = str(strerror)
            print(message)
            self.status_red(message)
            return False
        # run job with client
        try:
            print(job)
            status = self.client.job_run(job)
        except ValueError as strerror:
            message = str(strerror)
            print(message)
            self.status_red(message)
            return False
        if status == True:
            message = "Job successfully sent to IPython."
            print(message)
            self.status_green(message)
            return True


    def status_green(self, text):
        pal = QtGui.QPalette()
        bgc = QtGui.QColor(152, 229, 134)
        pal.setColor(QtGui.QPalette.Base, bgc)
        textc = QtGui.QColor(0, 0, 0)
        pal.setColor(QtGui.QPalette.Text, textc)
        self.status_box.setPalette(pal)
        self.status_box.setText(text)


    def status_red(self, text):
        pal = QtGui.QPalette()
        bgc = QtGui.QColor(229, 91, 91)
        pal.setColor(QtGui.QPalette.Base, bgc)
        textc = QtGui.QColor(0, 0, 0)
        pal.setColor(QtGui.QPalette.Text, textc)
        self.status_box.setPalette(pal)
        self.status_box.setText(text)


def main():
    """Initialize application."""
    app = QtGui.QApplication(sys.argv)
    dialog = SendJob()
    dialog.show()
    dialog.raise_()
    return app.exec_()


if __name__ == "__main__":
    main()

        