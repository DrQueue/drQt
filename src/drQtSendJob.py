#!/usr/bin/env python

import os, sys
import getpass

import PyQt4.QtGui as QtGui
import PyQt4.QtCore as QtCore
import PyQt4.QtWebKit as QtWebKit

from lib.utils import KojsConfigParser


os.environ["DEBUG"]="1"

try:
    # https://github.com/hdd/hlog
    import hlog as log
except:
    import logging as log

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
        #self._widgets = {}
        #self._current_active_widget = None
        #self._options_group = None
        #self.openFileChooser = None
        #self.connect(self, QtCore.SIGNAL("openFileChooser"), QtGui.QFileDialog())
        self.setupUi(self)
        self.setWindowTitle("drQt - Create New Job")
        # fill form with default values
        self.set_default_values()
        #self.LB_header.setPixmap(QtGui.QPixmap(os.path.join(icons_path, "drQHeader.png")))
        self.setWindowIcon(QtGui.QIcon(os.path.join(icons_path, "main.svg")))
        #self._job_ = drqueue.job()
        #self._kojs = KojsConfigParser(os.path.join(local_path, "kojs.json"))
        #self.fill_job_types()
        #self.add_about_widget()
        #self.connect(self.CB_job_type, QtCore.SIGNAL("highlighted(QString)"), self.enable_engine)
        #self.connect(self.PB_submit, QtCore.SIGNAL("clicked()"), self.process)
        # create client connection
        self.client = DrQueueClient()

    def set_default_values(self):
        """Set default values on form elements"""
        url = QtCore.QUrl("lib/ui/about.html")
        self.webView.load(url)
        self.owner_box.setText(getpass.getuser())
        self.startframe_box.setText("1")
        self.endframe_box.setText("1")
        self.blocksize_box.setText("1")
        self.retries_box.setText("1")
        self.renderer_box.insertItem (0, "Choose renderer")
        self.renderer_box.insertItem (1, "blender")
        self.renderer_box.insertItem (2, "maya")
        self.renderer_box.insertItem (3, "cinema4d")
        self.pool_box.insertItem (0, "Choose pool")
        pools = DrQueueComputerPool.query_poolnames()
        i = 1
        for pool in pools:
            self.pool_box.insertItem (i, pool)
            i += 1

    def openFileChooser(self):
        """Open file chooser widget."""
        fileName = QtGui.QFileDialog.getOpenFileName(self)
        print(fileName)
        self.scenefile_box.setText(fileName)
        self.show()
        self.raise_()
    
    def rendererChanged(self):
        """Change extra options when another renderer is selected."""
        active = str(self.renderer_box.currentText())
        if active == "blender":
            self.options_box.setText("{'rendertype':'animation'}")
        else:
            self.options_box.setText("None")
        print(active)

    def accept(self):
        """Take all form values, create job and send it to IPython."""
        print("creating job ...")
        # fetch values from form elements
        name = str(self.name_box.text())
        startframe = int(str(self.startframe_box.text()))
        endframe = int(str(self.endframe_box.text()))
        blocksize = int(str(self.blocksize_box.text()))
        renderer = str(self.renderer_box.currentText())
        scenefile = str(self.scenefile_box.text())
        retries = str(self.retries_box.text())
        owner = str(self.owner_box.text())
        pool = str(self.pool_box.currentText())
        # pool needs to have a real value
        if pool == "Choose pool":
            pool = None
        # options need to come in form of a Python dict
        options = eval(str(self.options_box.text()))
        # create job object
        try:
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

        