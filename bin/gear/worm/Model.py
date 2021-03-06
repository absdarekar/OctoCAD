import os;
import sys;
import math;
from PyQt5 import QtCore, QtGui, QtWidgets;
import FreeCAD;
import FreeCADGui;
import Draft;
import Part;
OCTOCAD_FILES_PATH=os.path.join(os.path.expanduser('~'),'OctoCAD');
sys.path.insert(1,OCTOCAD_FILES_PATH);
# from gui.gear.worm.ModelGui import ModelGui;
from bin.Utility import Utility;
from bin.gear.DesignData import DesignData;
from bin.gear.InvoluteProfile import InvoluteProfile;
class Model():
    # def setupUi(self):
        # self.dialog=QtWidgets.QDialog();
        # Utility.alignToCenter(self.dialog);
        # self.modelGui=ModelGui();
        # self.modelGui.setupUi(self.dialog);
        # self.dialog.show();
        # self.modelGui.buttonBox.accepted.connect(self.getData);
    def generateModel(self):
        XAXIS=FreeCAD.Vector(1,0,0);
        INTERFERANCE=0.1;
        ORIGIN=FreeCAD.Vector(0,0,0);
        COPY=True;
        # doc=FreeCAD.newDocument(self.fileName);
        doc=FreeCAD.newDocument("Worm Gear"); #temporary file name for testing
        # tooth=InvoluteProfile.generateTooth(self.pressureAngle,self.module,\
        #                                     self.teeth,self.clearance,\
        #                                     self.fillet);
        ###
        #temporary variables for testing
        MODULE=4;
        TEETH=18;
        PRESSURE_ANGLE=20;
        CLEARANCE=0.5;
        FILLET=0.25;
        clearance=CLEARANCE*MODULE;
        ###
        tooth=InvoluteProfile.generateTooth(PRESSURE_ANGLE,MODULE,TEETH,CLEARANCE,FILLET);
        tooth=Draft.rotate(tooth,90,ORIGIN,XAXIS,not(COPY));
        pitch=math.pi*MODULE;
        helixRadius=MODULE*TEETH*math.cos(math.radians(PRESSURE_ANGLE))/2-clearance;
        helix=Part.makeHelix(pitch,MODULE*20,helixRadius);
        doc.addObject("Part::Feature","helix");
        doc.helix.Shape=helix;
        doc.addObject("Part::Sweep","threads");
        doc.threads.Sections=doc.findObjects("Part::Feature",tooth.Name);
        doc.threads.Spine=doc.helix;
        doc.threads.Solid=True;
        doc.threads.Frenet=True;
        worm=Part.makeCylinder(tooth.Shape.BoundBox.XMin+INTERFERANCE,MODULE*20);
        doc.addObject("Part::Feature","worm");
        doc.worm.Shape=worm;
        doc.addObject("Part::MultiFuse","wormGear");
        doc.wormGear.Shapes=[doc.threads,doc.worm,];
        FreeCADGui.ActiveDocument.getObject(tooth.Name).Visibility=False;
        FreeCADGui.ActiveDocument.getObject("helix").Visibility=False;
        FreeCADGui.ActiveDocument.getObject("threads").Visibility=False;
        FreeCADGui.ActiveDocument.getObject("worm").Visibility=False;
        doc.recompute();
    # def getData(self):
    #     self.gear="Worm";
    #     self.profileType=self.modelGui.profile.currentText();
    #     profile=DesignData.evalProfile(self.profileType);
    #     self.pressureAngle=float(profile["pressureAngle"]);
    #     self.module=float(self.modelGui.module.text());
    #     self.teeth=float(self.modelGui.teeth.text());
    #     self.gearing=self.modelGui.gearing.currentText();
    #     self.faceWidth=float(self.modelGui.faceWidth.text());
    #     self.clearance=float(self.modelGui.clearance.text());
    #     self.fillet=float(self.modelGui.fillet.text());
    #     self.fileName=self.gear+" "+self.profileType+" "+str(self.module)+"x"+\
    #                     str(self.teeth)+" "+self.gearing+" "+str(self.faceWidth)+\
    #                     " "+str(self.clearance)+" "+str(self.fillet);
    #     self.generateModel();
if __name__=="__main__":
    qApplication=QtWidgets.QApplication(sys.argv);
    model=Model();
    # model.setupUi();
    model.generateModel();
