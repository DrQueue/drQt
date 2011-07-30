import sys
import os

from pprint import pformat

os.environ["DEBUG"]="1"

try:
    # https://github.com/hdd/hlog
    import hlog as log
except:
    import logging as log

import PyQt4.QtGui as QtGui
import PyQt4.QtCore as QtCore

try:
    import DrQueue
    from DrQueue import Job as DrQueueJob
    from DrQueue import Client as DrQueueClient
except:
    raise "DrQueue module not found! Please check DrQueueIPython installation."

# initialize DrQueue client
client = DrQueueClient()

from utils import icons_path
from utils import tooltips_path
from lib.nodeViewer import NodeViewer
import utils

class JobTab(QtGui.QWidget):
    
    def __init__(self,drq_job_object=None,parent=None):
        super(JobTab,self).__init__(parent=parent)
        self._drq_job_object = drq_job_object
                
        self.columns=[]
        
        self._tab_id=QtGui.QLabel()
        self._tab_id.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.columns.append(self._tab_id)
        
        self._tab_name=QtGui.QLabel()
        self._tab_name.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.columns.append(self._tab_name)
        
        self._tab_owner=QtGui.QLabel()
        self._tab_owner.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.columns.append(self._tab_owner)
        
        self._tab_status=QtGui.QLabel()
        self._tab_status.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.columns.append(self._tab_status)
        
        # currently not supported
        #self._tab_procs=QtGui.QLabel()
        #self._tab_procs.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        #self.columns.append(self._tab_procs)
        
        # currently not supported
        #self._tab_priority=QtGui.QSpinBox()
        #self._tab_priority.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        #self._tab_priority.setMaximum(5000)
        #self.columns.append(self._tab_priority)

        self._tab_tasks_total=QtGui.QLabel()
        self._tab_tasks_total.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.columns.append(self._tab_tasks_total)

        self._tab_tasks_left=QtGui.QLabel()
        self._tab_tasks_left.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.columns.append(self._tab_tasks_left)

        self._tab_tasks_done=QtGui.QProgressBar()
        self._tab_tasks_done.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.columns.append(self._tab_tasks_done)

        self._tab_pool=QtGui.QLabel()
        self._tab_pool.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.columns.append(self._tab_pool)
        
        self._set_values()
        self._set_context()
        self._set_tooltip()
     
           
    def _node_view_show(self):
        log.debug("starting node view")
        NW_widget=NodeViewer(self)
        NW_widget.show()
                
        jobs=utils.get_all_jobs()
        depend_id=self._drq_job_object.dependid
        NW_widget.add_node(self._drq_job_object)
        
        log.debug("id depend: %d"%depend_id)
        
        if self._drq_job_object.id == depend_id:
            return 
        
        for job in jobs:
            jd = job.id
            
            log.debug("current id : %d \tdepend : %d"%(jd,depend_id))

            if jd == depend_id:
                log.debug("Adding node %s to the network"%job.name)
                NW_widget.add_node(job)
      
    
    def _set_values(self):        
        """
        set tab values using the drq job object 
        """
        self._tab_id.setText("%s"%self._drq_job_object['_id'])        
        self._tab_name.setText("%s"%self._drq_job_object['name'])
        self._tab_owner.setText("%s"%self._drq_job_object['owner'])

        pic = ""
        status = client.job_status(self._drq_job_object['_id'])
        if status == None:
            pic = QtGui.QPixmap(os.path.join(icons_path,"help-browser.png"))
        if status == "ok":
            pic = QtGui.QPixmap(os.path.join(icons_path,"ok.png"))
        if status == "pending":
            pic = QtGui.QPixmap(os.path.join(icons_path,"running.png"))
        if status == "error":
            pic = QtGui.QPixmap(os.path.join(icons_path,"dialog-warning.png"))
        if status == "aborted":
            pic = QtGui.QPixmap(os.path.join(icons_path,"stop.png"))
        print(status)
        self._tab_status.setPixmap(pic.scaled(25,25))

        tot_frames=self._drq_job_object['endframe']-self._drq_job_object['startframe']
        left = client.query_job_frames_left(self._drq_job_object['_id'])
        if left > 0:
            difframes = float(left / tot_frames)
        else:
            difframes = 0
        done = 100-(difframes*100)

        self._tab_tasks_total.setText(str(tot_frames))
        self._tab_tasks_left.setText(str(left))
        self._tab_tasks_done.setValue(int(done))

        # currently not supported
        #self._tab_priority.setValue(int(self._drq_job_object.priority))

        self._tab_pool.setText("%s" % str(self._drq_job_object['pool']))

#        id = self._drq_job_object.id
#        print self._drq_job_object.name
#                
#        for i in range(self._drq_job_object.envvars.nvariables):
#            env_id= drqueue.request_job_envvars(id,self._drq_job_object.envvars,i)
#            print self._drq_job_object.envvars_dump_info
            
#            if ptr:
#                print ">>",id,self._drq_job_object.envvars.variables.ptr[i].name
#            var= drqueue.request_job_envvars(id,self._drq_job_object.envvars,i)
#            print var, type(var)

    def _set_context(self):
        """
        bind the context menu to all the columns
        """
        for column in self.columns:
            column.setContextMenuPolicy(QtCore.Qt.CustomContextMenu) 
            self.connect(column, QtCore.SIGNAL("customContextMenuRequested(QPoint)"), self._create_context)
                        
    def _set_tooltip(self):
        """
        build up the tooltip using the drq job object
        bind the tooltip to all the columns
        """
        html_tooltip=open(os.path.join(tooltips_path,"job_info.html"),"r")
        tooltipData ={}
        #tooltipData["cmd"]=self._drq_job_object.cmd
        #tooltipData["envvars"]=self._drq_job_object.envvars
        #tooltipData["dependid"]=self._drq_job_object.dependid
        
        #formattedTolltip=str(html_tooltip.read()).format(**tooltipData)
        #for column in self.columns:
        #    column.setToolTip(formattedTolltip)
                
    def _emit_uptdate(self):
        log.debug("emit update")
        self.emit(QtCore.SIGNAL("update"))
                    
    def _stop_job(self):
        self._drq_job_object.request_stop(drqueue.CLIENT)
        self._emit_uptdate()
    
    def _hardstop_job(self):
        self._drq_job_object.request_hard_stop(drqueue.CLIENT)     
        self._emit_uptdate()
            
    def _rerun_job(self):
        self._drq_job_object.request_rerun(drqueue.CLIENT)     
        self._emit_uptdate()
    
    def _delete_job(self):       
        self._drq_job_object.request_delete(drqueue.CLIENT)   
        self._emit_uptdate()    
    
    def _continue_job(self):       
        self._drq_job_object.request_continue(drqueue.CLIENT)              
        self._emit_uptdate() 
           
    def _create_context(self,QPoint):
        """
        create the context menu
        """
        #print currentItem._tab_id
        #newAct =QtGui.QAction("&New Job",self)
        #newAct.setToolTip("createa new job")
        #self.connect(newAct, QtCore.SIGNAL('triggered()'), self._new_job_show)  
                
        copyAct = QtGui.QAction("&Copy Job",self)
        copyAct.setToolTip("copy the job")
        
        rerunAct = QtGui.QAction("&Re Run",self)
        rerunAct.setToolTip("Re run the job")
        self.connect(rerunAct, QtCore.SIGNAL('triggered()'), self._rerun_job)
        
        stopAct = QtGui.QAction("&Stop",self)
        stopAct.setToolTip("stop the running job")
        self.connect(stopAct, QtCore.SIGNAL('triggered()'), self._stop_job)
                
        hstopAct = QtGui.QAction("&Hard Stop",self)
        hstopAct.setToolTip("hard stop the running job")
        self.connect(hstopAct, QtCore.SIGNAL('triggered()'), self._hardstop_job)
        
        continueAct = QtGui.QAction("&Continue",self)
        continueAct.setToolTip("Continue the stop job")
        self.connect(continueAct, QtCore.SIGNAL('triggered()'), self._continue_job)
        
        deleteAct = QtGui.QAction("&Delete",self)
        deleteAct.setToolTip("delete the job")
        self.connect(deleteAct, QtCore.SIGNAL('triggered()'), self._delete_job)

        nodedAct = QtGui.QAction("Node &View",self)
        nodedAct.setToolTip("view job dependencies")
        self.connect(nodedAct, QtCore.SIGNAL('triggered()'), self._node_view_show)
        
        # Create a menu
        menu = QtGui.QMenu("Menu", self)
        #menu.addAction(newAct)
        menu.addAction(copyAct) 
        menu.addSeparator()
        menu.addAction(rerunAct)
        menu.addAction(stopAct) 
        menu.addAction(hstopAct)
        
        menu.addAction(continueAct)
        
        menu.addAction(deleteAct)
        menu.addSeparator()
        menu.addAction(nodedAct) 
        # Show the context menu in the mouse position 
        menu.exec_(QtGui.QCursor.pos())         

                
    def add_to_table(self,table,index):
        """
        bind the job row data to the job table
        """
        table.setCellWidget(index,0,self._tab_id)
        table.setCellWidget(index,1,self._tab_name)
        table.setCellWidget(index,2,self._tab_owner)
        table.setCellWidget(index,3,self._tab_status) 
        table.setCellWidget(index,4,self._tab_tasks_total)
        table.setCellWidget(index,5,self._tab_tasks_left)
        table.setCellWidget(index,6,self._tab_tasks_done)
        # currently not supported
        #table.setCellWidget(index,6,self._tab_priority)
        table.setCellWidget(index,7,self._tab_pool) 
        