import math;
import numpy;
import FreeCAD;
import Draft;
import Part;
class InvoluteProfile():
    def calculateRange(radiusRatio):
        PRECISION=0.0000001;
        xMean=0;
        xUpper=1;
        xLower=0;
        if((InvoluteProfile.evalInv(radiusRatio,xUpper)*InvoluteProfile.evalInv(radiusRatio,xLower))<0):
            xMean=(xUpper+xLower)/2;
            while(abs(InvoluteProfile.evalInv(radiusRatio,xMean))>=PRECISION):
                xMean=(xUpper+xLower)/2;
                if ((InvoluteProfile.evalInv(radiusRatio,xLower)*\
                    InvoluteProfile.evalInv(radiusRatio,xMean))<=0):
                    xUpper=xMean;
                else:
                    xLower=xMean;
        return xMean;
    def evalInv(radiusRatio,x):
        return eval("radiusRatio-math.cos(x)-x*math.sin(x)");
    def generateHob(baseRadius,addendumRadius,dedendumRadius,angularSeperation,clearance,filletRadius,sign):
        CLOSED=True;
        OPEN=False;
        FACE=True;
        WIRE_FRAME=False;
        PLACEMENT=None
        DELETE=True;
        PRECISION=0.001;
        ratioAddendum=addendumRadius/baseRadius;
        ratioDedendum=dedendumRadius/baseRadius;
        t=numpy.arange(InvoluteProfile.calculateRange(ratioDedendum),\
                        InvoluteProfile.calculateRange(ratioAddendum),PRECISION);
        xInvLeft=baseRadius*(numpy.cos(-t-angularSeperation)-t*numpy.sin(-t-angularSeperation));
        yInvLeft=baseRadius*(numpy.sin(-t-angularSeperation)+t*numpy.cos(-t-angularSeperation));
        xInvRight=baseRadius*(numpy.cos(t+angularSeperation)+t*numpy.sin(t+angularSeperation));
        yInvRight=baseRadius*(numpy.sin(t+angularSeperation)-t*numpy.cos(t+angularSeperation));
        InvLeftVector=[];
        InvRightVector=[];
        for i in range(len(t)):
            InvLeftVector.append(FreeCAD.Vector(xInvLeft[i],yInvLeft[i],0));
            InvRightVector.append(FreeCAD.Vector(xInvRight[i],yInvRight[i],0));
        InvLeft=Draft.makeBSpline(Part.makePolygon(InvLeftVector),OPEN,WIRE_FRAME);
        InvRight=Draft.makeBSpline(Part.makePolygon(InvRightVector),OPEN,WIRE_FRAME);
        clearanceLeftX=FreeCAD.Vector(xInvLeft[0]-clearance+filletRadius,yInvLeft[0],0);
        clearanceRightX=FreeCAD.Vector(xInvRight[0]-clearance+filletRadius,yInvRight[0],0);
        lineLeft=Draft.makeLine(InvLeftVector[0],clearanceLeftX);
        lineRight=Draft.makeLine(InvRightVector[0],clearanceRightX);
        clearanceLeftY=FreeCAD.Vector(xInvLeft[0]-clearance,yInvLeft[0]+filletRadius,0);
        clearanceRightY=FreeCAD.Vector(xInvRight[0]-clearance,yInvRight[0]-filletRadius,0);
        lineClearance=Draft.makeLine(clearanceLeftY,clearanceRightY);
        filletLeftCenter=FreeCAD.Placement();
        filletRightCenter=FreeCAD.Placement();
        filletLeftCenter.move(FreeCAD.Vector(xInvLeft[0]-clearance+filletRadius,\
                                yInvLeft[0]+filletRadius,0));
        filletRightCenter.move(FreeCAD.Vector(xInvRight[0]-clearance+filletRadius,\
                                yInvRight[0]-filletRadius,0));
        startangle=180;
        endangle=270;
        filletLeft=Draft.makeCircle(filletRadius,filletLeftCenter,WIRE_FRAME,startangle,endangle);
        startangle=90;
        endangle=180;
        filletRight=Draft.makeCircle(filletRadius,filletRightCenter,WIRE_FRAME,startangle,endangle);
        radius=math.sqrt(xInvLeft[len(xInvLeft)-1]**2+yInvLeft[len(xInvLeft)-1]**2);
        arcAngle=sign*(math.atan(yInvLeft[len(xInvLeft)-1]/xInvLeft[len(xInvLeft)-1])*180/math.pi);
        startangle=arcAngle;
        endangle=-arcAngle;
        arc=Draft.makeCircle(radius,PLACEMENT,WIRE_FRAME,startangle,endangle);
        hobWire, deletedFeatures=Draft.upgrade([arc,lineRight,lineLeft,lineClearance,\
                                                InvRight,InvLeft,filletRight,filletLeft],DELETE);
        hobFace, deletedFeatures=Draft.upgrade(hobWire,DELETE);
        return hobFace[0];
    def generateTooth(pressureAngle,module,teeth,clearance,fillet):
        SIGN=-1;
        pressureAngle=math.radians(pressureAngle);
        baseRadius=module*teeth*math.cos(pressureAngle)/2;
        addendumRadius=(module*teeth+2*module)/2;
        dedendumRadius=(module*teeth-2.5*module)/2;
        angularSeperation=SIGN*(math.pi/(2*teeth)+(math.tan(pressureAngle)-pressureAngle));
        clearance=clearance*module;
        filletRadius=fillet*module;
        toothFace=InvoluteProfile.generateHob(baseRadius,addendumRadius,\
                                            dedendumRadius,angularSeperation,\
                                            clearance,filletRadius,SIGN);
        return toothFace;
    def generateProfile(pressureAngle,module,teeth,faceWidth,clearance,fillet):
        ORIGIN=FreeCAD.Vector(0,0,0);
        ZAXIS=FreeCAD.Vector(0,0,1);
        COPY=True;
        SIGN=+1;
        pressureAngle=math.radians(pressureAngle);
        baseRadius=module*teeth*math.cos(pressureAngle)/2;
        addendumRadius=(module*teeth+2*module)/2;
        dedendumRadius=(module*teeth-2.5*module)/2;
        angularSeperation=SIGN*(math.pi/(2*teeth)-(math.tan(pressureAngle)-pressureAngle));
        faceWidth=faceWidth*module;
        clearance=clearance*module;
        filletRadius=fillet*module;
        addendumCirle=Draft.makeCircle(addendumRadius);
        hobFace=InvoluteProfile.generateHob(baseRadius,addendumRadius,\
                                            dedendumRadius,angularSeperation,\
                                            clearance,filletRadius,SIGN);
        hobFaces=[]
        hobFaces.append(hobFace);
        angle=360/teeth;
        while(angle<360):
            hobFaces.append(Draft.rotate(hobFaces[0],angle,ORIGIN,ZAXIS,COPY));
            angle+=360/teeth;
        profile=addendumCirle;
        for i in range(len(hobFaces)):
            profile=Draft.cut(profile,hobFaces[i]);
        height=FreeCAD.Vector(0,0,faceWidth);
        return profile, height;
