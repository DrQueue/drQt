import sys
import os

import logging
from pprint import pformat

import PyQt4.QtGui as QtGui
import PyQt4.QtCore as QtCore

try:
    import DrQueue
    from DrQueue import Job as DrQueueJob
    from DrQueue import Client as DrQueueClient
    from DrQueue import Computer as DrQueueComputer
except:
    raise "DrQueue module not found! Please check DrQueueIPython installation."

# initialize DrQueue client
client = DrQueueClient()

from utils import icons_path
from utils import tooltips_path

logging.basicConfig()
log = logging.getLogger("slave_tab")
log.setLevel(logging.DEBUG)

class SlaveNodeTab(QtGui.QWidget):
    
    def __init__(self, drq_node_object=None, parent=None):
        super(SlaveNodeTab, self).__init__(parent=parent)
        self._drq_node_object = drq_node_object

        self.columns = [] 
               
        self.icons=[]       
        self.icons.append(QtGui.QPixmap(os.path.join(icons_path, "stop.png")))
        self.icons.append(QtGui.QPixmap(os.path.join(icons_path, "ok.png")))       

        self._tab_id = QtGui.QLabel()
        self._tab_id.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter) 
        self.columns.append(self._tab_id)

        #self._tab_enabled = QtGui.QLabel()
        #self._tab_enabled.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        #self.columns.append(self._tab_enabled)
        
        self._tab_hostname = QtGui.QLabel()
        self._tab_hostname.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.columns.append(self._tab_hostname)
        
        self._tab_arch = QtGui.QLabel()
        self._tab_arch.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.columns.append(self._tab_arch)

        self._tab_os = QtGui.QLabel()
        self._tab_os.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.columns.append(self._tab_os)

        self._tab_nbits = QtGui.QLabel()
        self._tab_nbits.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.columns.append(self._tab_nbits)

        self._tab_procspeed = QtGui.QLabel()
        self._tab_procspeed.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.columns.append(self._tab_procspeed)

        self._tab_ncpus = QtGui.QLabel()
        self._tab_ncpus.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.columns.append(self._tab_ncpus)

        self._tab_ncorescpu = QtGui.QLabel()
        self._tab_ncorescpu.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.columns.append(self._tab_ncorescpu)
        
        self._tab_memory = QtGui.QLabel()
        self._tab_memory.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.columns.append(self._tab_memory)

        #self._tab_running = QtGui.QLabel()
        #self._tab_running.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        #self.columns.append(self._tab_running)

        self._tab_loadavg = QtGui.QLabel()
        self._tab_loadavg.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.columns.append(self._tab_loadavg)
        
        self._tab_pools = QtGui.QLabel()
        self._tab_pools.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.columns.append(self._tab_pools)
        
        self._set_values()
        self._set_context()
        self._set_tooltip()
        
    def _set_values(self):
        comp = client.identify_computer(self._drq_node_object)

        self._tab_id.setText("%d" % self._drq_node_object)
        self._tab_hostname.setText("%s" % comp['hostname'])
        self._tab_arch.setText("%s" % comp['arch'])
        #self._tab_enabled.setPixmap( self.icons[self._drq_node_object.limits.enabled].scaled(25,25))
        self._tab_os.setText("%s" % comp['os'])
        self._tab_nbits.setText("%d" % comp['nbits'])
        self._tab_procspeed.setText("%s" % comp['procspeed'])
        self._tab_ncpus.setText("%d" % comp['ncpus'])
        self._tab_ncorescpu.setText("%d" % comp['ncorescpu'])
        self._tab_memory.setText("%s" % comp['memory'])
        #self._tab_running.setText("%s" % "TODO")
        
        #self._tab_loadavg.setText("%d:%d:%d"%(self._drq_node_object.status.get_loadavg(0),
        #                                      self._drq_node_object.status.get_loadavg(1),
        #                                      self._drq_node_object.status.get_loadavg(2)))
        load = comp['load'].split(" ")
        load_0 = int(float(load[0].replace(',', '.'))*100)
        load_1 = int(float(load[1].replace(',', '.'))*100)
        load_2 = int(float(load[2].replace(',', '.'))*100)
        self._tab_loadavg.setText("%d : %d : %d" % (load_0, load_1, load_2))

        #self._tab_running.setText("")
        self._tab_pools.setText(", ".join(DrQueueComputer.get_pools(self._drq_node_object)))
                
    def _set_context(self):
        for column in self.columns:
            column.setContextMenuPolicy(QtCore.Qt.CustomContextMenu) 
            self.connect(column, QtCore.SIGNAL("customContextMenuRequested(QPoint)"), self._create_context)            

    def _set_tooltip(self):
        html_tooltip = open(os.path.join(tooltips_path,"node_info.html"), "r")
        tooltipData = {}
        comp = client.identify_computer(self._drq_node_object)
        tooltipData["id"] = self._drq_node_object
        tooltipData["arch"] = comp['arch']
        tooltipData["memory"] = comp['memory']
        tooltipData["name"] = comp['hostname']
        tooltipData["ncpus"] = str(comp['ncpus'])
        tooltipData["nnbits"] = str(comp['nbits'])
        tooltipData["os"] = comp['os']
        tooltipData["procspeed"] = comp['procspeed']
        tooltipData["proctype"] = comp['proctype']
        tooltipData["speedindex"] = comp['procspeed']
        
        formattedTolltip=str(html_tooltip.read()).format(**tooltipData)
        
        for column in self.columns:
            column.setToolTip(formattedTolltip)
            
    def _create_context(self,QPoint):

        #enableAct = QtGui.QAction("&Enable", self)
        #self.connect(enableAct, QtCore.SIGNAL('triggered()'), self._enable_slave)

        #disableAct = QtGui.QAction("&Disable", self)
        #self.connect(disableAct, QtCore.SIGNAL('triggered()'), self._disable_slave)

        shutdownAct = QtGui.QAction("&Shutdown", self)
        self.connect(shutdownAct, QtCore.SIGNAL('triggered()'), self._shutdown_slave)

        menu = QtGui.QMenu("Menu", self) 
        #menu.addAction(enableAct)
        #menu.addAction(disableAct)
        menu.addAction(shutdownAct)
        menu.exec_(QtGui.QCursor.pos())           

    def _enable_slave(self):
        self._drq_node_object.request_enable(drqueue.CLIENT)
        self._emit_uptdate()

    def _disable_slave(self):
        self._drq_node_object.request_disable(drqueue.CLIENT)
        self._emit_uptdate()

    def _shutdown_slave(self):
        client.ip_client.shutdown(self._drq_node_object)
        self._emit_uptdate()

    def _emit_uptdate(self):
        log.debug("emit update")
        self.emit(QtCore.SIGNAL("update"))  
                        
    def add_to_table(self, table, index):
            table.setCellWidget(index,0, self._tab_id)
            table.setCellWidget(index,1, self._tab_hostname)
            #table.setCellWidget(index,1, self._tab_enabled)
            table.setCellWidget(index,2, self._tab_arch)
            table.setCellWidget(index,3, self._tab_os)
            table.setCellWidget(index,4, self._tab_nbits)
            table.setCellWidget(index,5, self._tab_procspeed)
            table.setCellWidget(index,6, self._tab_ncpus)
            table.setCellWidget(index,7, self._tab_ncorescpu)
            table.setCellWidget(index,8, self._tab_memory)
            #table.setCellWidget(index,9, self._tab_running)
            table.setCellWidget(index,9, self._tab_loadavg)
            table.setCellWidget(index,10, self._tab_pools)

