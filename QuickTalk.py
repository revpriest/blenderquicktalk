# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
#
# "Quicktalk" is a plugin for Blender which tries to do most of
# the dull boring work for lip-synch for a character.
#
# First, make shape keys for the mouth shapes.
# You'll need: AI, O, E, U, ETC, L, WQ, MBP, FV and the Basis should be a rest shape.
# You can add a "TH" if you think that shape is important,
# but if it's not there we'll just assume ETC when it comes up.
#
# Give it an armature if you don't already have one. It needs an armature to
# attach to the shape keys.
#
# Put the 3d cursor near the object's face. It's where we'll 
# create the panel of bones to control the shape-keys.
# Click the "Build Shape-Key Panel Armature" button.
# That'll build a panel of bones that control the shape-keys
# Each bone can be rotated from 0 to 90 degrees like
# a lever to control the expression. It'll build a lever
# for EVERY shape key so you can include blinks or
# smiles or whatever to get a lever for them too.
#
# Select a script file.
# Script files contain the dialogue the charters
# in the scene speak. Lines with a single word
# followed by a : mark changes in which character
# is speaking. The armatures attached to the
# character should be named the same as the
# name in the script. Well, first few chars
# have to match anyway.
# Lines which aren't a single word followed by
# a character are spoken by that character.
# Example (Obviously cut the #s off)
#
# ------------------
# Monkey:
# Hello I'm a monkey
# Welcome to my cartoon
# 
# Dog:
# Yes, and I'm a dog.
# 
# Monkey:
# Welcome to my cartoon dog.
# ------------------
#
# Click the "Guess Dialogue Markers" button.
# This will try to guess where in the timeline
# there's a change in who speaks and put markers
# there. It will be wrong, so adjust them so 
# they are right. You can make them yourself
# if you need to for some reason, they are just 
# normal markers but with names ending in "!D"
#
# When they're right click the "Guess Line Markers"
# which will add markers for each line that each
# character speaks. Again they'll be wrong and
# you'll have to adjust them. They end in "!L"
#
# When they're right click the "Guess Word Markers"
# button. It'll put markers for every spoken word.
# There's more chance this will be more or less
# right but still not much chance so fix 'em.
# Word markers end in "!W"
#
# Select an armature and click "QuickTalk Plot"
# This will create f-curves for the scene which
# change the x-rotation of the bones created in
# the panel. There's a pretty good chance this
# will look all right, but especially long words
# or where there's pauses in speech it'll still
# be wrong and you'll need to squash and scale
# the f-curve to match.
#
# If all that sounds long-winded, you do not understand
# how damn tedious lip-synching is when you have
# to do it literally frame by frame. 


bl_info = {
    "name": "QuickTalk Lipsyncher",
    "author": "Adam Priest - tentacles.org.uk ;)",
    "version": (0, 0, 2),
    "blender": (2, 7, 1),
    "location": "Object Panel",
    "description": "A system for speeding up lip synch stuff by using markers and a phoneme dictionary",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object",
}
import bpy
import math
import re
import string

###
# Register the button-panel, the functions we'll use and the
# user-editable variables like 'script location'.
#
def register():
    bpy.utils.register_class(QuickTalk_AddQuicktalkPanel)
    bpy.utils.register_class(QuickTalk_BuildShapeKeyPanel)
    bpy.utils.register_class(QuickTalk_GuessDialogue)
    bpy.utils.register_class(QuickTalk_GuessLines)
    bpy.utils.register_class(QuickTalk_GuessWords)
    bpy.utils.register_class(QuickTalk_QuicktalkPlot)
    bpy.types.Scene.quicktalk_script_file = bpy.props.StringProperty (
      name = "Script File",
      default = "",
      description = "Where is the file defining the script?",
      subtype = 'FILE_PATH'
    )
    bpy.types.Scene.quicktalk_dict_file = bpy.props.StringProperty (
      name = "Dictionary File",
      default = "",
      description = "Where is the file defining the phoneme dictionary?",
      subtype = 'FILE_PATH'
    )
    bpy.types.Scene.quicktalk_bone_option = bpy.props.EnumProperty (
      items = (('0', 'X-Rotation', 'Create and move bones for X-Rotation'),    
               ('1', 'X-Translation', 'Create and move bones for X-Translation'),
               ('2', 'MHX2 Visemes', 'Plot curves using MHX2 visemes for MHX2 imported models')),
      name = "Bone Option",
      default = "0",
      description = "Move/Make bones with rotation or translation?"
    )


###
# Unregister it all when we're uninstalled
#
def unregister():
    bpy.utils.unregister_class(QuickTalk_AddQuicktalkPanel)
    bpy.utils.unregister_class(QuickTalk_BuildShapeKeyPanel)
    bpy.utils.unregister_class(QuickTalk_GuessDialogue)
    bpy.utils.unregister_class(QuickTalk_GuessLines)
    bpy.utils.unregister_class(QuickTalk_GuessWords)
    bpy.utils.unregister_class(QuickTalk_QuicktalkPlot)
    del bpy.types.Scene.quicktalk_script_file
    del bpy.types.Scene.quicktalk_dict_file 
    del bpy.types.Scene.quicktalk_bone_option


###
# Our button's panel in the object pane.
#
class QuickTalk_AddQuicktalkPanel(bpy.types.Panel):
    """QuickTalk"""
    bl_idname = "OBJECT_PT_thing"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_label = "QuickTalk"
 
    def draw(self, context):
        TheCol = self.layout.column(align=True)
        TheCol.prop(context.scene, "quicktalk_bone_option")
        TheCol.operator("object.quicktalk_addpanel", text="Build Shape-Key Panel Armature")
        TheCol.prop(context.scene, "quicktalk_script_file")
        TheCol.operator("object.quicktalk_guess_dialogue", text="Guess Dialogue Markers")
        TheCol.operator("object.quicktalk_guess_lines", text="Guess Line Markers")
        TheCol.operator("object.quicktalk_guess_words", text="Guess Word Markers")
        TheCol.prop(context.scene, "quicktalk_dict_file")
        TheCol.operator("object.quicktalk_plot_timeline", text="Quicktalk Plot")


###
# The function to build the shape keys panel
# in the selected object's armature.
#
class QuickTalk_BuildShapeKeyPanel(bpy.types.Operator):
    """Build Shape Key Panel In Armature"""    # tooltip
    bl_idname = "object.quicktalk_addpanel"
    bl_label = "Add QuickTalk Synch Panel to Armature"  # display name in the search-menu.
    bl_options = {'REGISTER', 'UNDO'} 



    ###
    # We arrange the levers in the panel in a spiral
    # so that we can add more at any point and still
    # have close-as-possible to a square
    # Mat Taylor found a better way than my first 
    # effort.....
    #
    def getXYSpiral(self,i):
        n = math.floor(math.sqrt(i))
        d = i - n*n
        if(n & 1):
          x = (n+1)/2
          y = (n+1)/2
          if(d<n):
            y=y+d-n
          elif(d>n):
            x=x-d+n
        else:
          x = n/2-n
          y = n/2-n
          if(d<n):
            y=y-d+n
          elif(d>n):
            x=x+d-n
        return (x*1.2,y*1.2)


    ###
    # Function to add a driver to a shapekey and attach to a bone.
    #
    def addDriver(self,shapekey,name,destObj,bone):
        driver = shapekey.driver_add("value") 
        driver.driver.type = "SCRIPTED"
        if(bpy.context.scene.quicktalk_bone_option == "0"):
          driver.driver.expression = "val/1.571"  #90 degrees is 1.571 radians
        else:
          driver.driver.expression = "val"
        
        val = driver.driver.variables.new()
        val.name = "val" 
        val.type = 'TRANSFORMS'
        val.targets[0].id = destObj
        val.targets[0].bone_target = name
        val.targets[0].transform_space = 'LOCAL_SPACE'
        if(bpy.context.scene.quicktalk_bone_option == "0"):
          val.targets[0].transform_type = 'ROT_X'
        else:
          val.targets[0].transform_type = 'LOC_X'
        

    ###
    # Function to add a bone to the armature's control panel
    #
    def addPanelBone(self, arm, parent, name, num):
        (x,z) = self.getXYSpiral(num)
        editbone = arm.edit_bones.new(name)
        editbone.parent = parent
        editbone.head = (parent.head[0]+x,    parent.head[1],parent.head[2]+z)
        if(bpy.context.scene.quicktalk_bone_option == "0"):
          editbone.tail = (parent.head[0]+x+0.9,parent.head[1],parent.head[2]+z)
        else:
          editbone.tail = (parent.head[0]+x,parent.head[1],parent.head[2]+z-0.8)
        
        return editbone


    ###
    # Function to set a bone's constraints
    # to limit it's rotation.
    #
    def setBoneLimits(self,bone):
        bone.rotation_mode = "XYZ"
        bone.lock_rotation = (True , True, True)
        bone.lock_location = (True , True, True)
        if(bpy.context.scene.quicktalk_bone_option == "0"):
          bone.lock_rotation = (False, True, True)
          con = bone.constraints.new("LIMIT_ROTATION");
          con.use_limit_x = True
          con.use_limit_y = True
          con.use_limit_z = True
          con.min_x = 0
          con.max_x = 1.571
          con.min_y = 0
          con.max_y = 0
          con.min_z = 0
          con.max_z = 0
        else:
          bone.lock_location = (False, True, True)
          con = bone.constraints.new("LIMIT_LOCATION");
          con.min_z = 0
          con.max_z = 0
          con.max_x = 1
          con.use_min_x = True
          con.use_max_x = True
          con.use_min_y = True
          con.use_max_y = True
          con.use_min_z = True
          con.use_max_z = True
          con.min_x = 0
          con.min_y = 0
          con.max_y = 0
        con.owner_space= "LOCAL"


    ###
    # Execute the "Build Shape-Key Panel in armature" function
    #
    def execute(self, context): 
        scene = bpy.context.scene;

        # Get active object
        shapeObj = scene.objects.active 

        #Get armature for that object, should be it's parent.
        armObj = scene.objects.active.parent
        if(not armObj):
          self.report({"ERROR"},"Can't find parent armature to add bones");
          return {"CANCELLED"}
        if(armObj.type!="ARMATURE"):
          self.report({"ERROR"},"Parent isn't an armature");
          return {"CANCELLED"}

        #Get cursor location, relative to armature object
        #This is where we want the control panel rig to go.
        x = scene.cursor_location[0]; 
        y = scene.cursor_location[1]; 
        z = scene.cursor_location[2]; 
        x = (x-armObj.location[0])/armObj.scale[0];
        y = (y-armObj.location[1])/armObj.scale[1];
        z = (z-armObj.location[2])/armObj.scale[2];

        #Select the armature, go to edit mode
        scene.objects.active = armObj
        bpy.ops.object.mode_set(mode='EDIT')

        #Create the panel root bone.
        arm = armObj.data
        panelroot = arm.edit_bones.new("Shapes Panel")
        panelroot.head = (x,y,z)
        panelroot.tail = (x,y+1,z)

        #Add bone for every shape-key, except those starting with !
        shapeKeys = shapeObj.data.shape_keys.key_blocks
        num = 0;
        for key in shapeKeys:
            if((key.name[0:3]=="qt_") or (key.name in ["AI","O","E","U","ETC","L","WQ","MBP","M","FV","TH"])):
              self.addPanelBone(arm,panelroot,key.name,num)
              num=num+1

        #Select pose mode to edit the rig to set limits
        bpy.ops.object.mode_set(mode='POSE') 
        pose = armObj.pose
        for key in shapeKeys:
            if((key.name[0:3]=="qt_") or (key.name in ["AI","O","E","U","ETC","L","WQ","MBP","M","FV","TH"])):
              self.setBoneLimits(pose.bones[key.name])

        #Add drivers to the all the shape keys
        for key in shapeKeys:
            if((key.name[0:3]=="qt_") or (key.name in ["AI","O","E","U","ETC","L","WQ","MBP","M","FV","TH"])):
              self.addDriver(key,key.name,armObj,pose.bones[key.name])
        
        #Restore the mode to how it was when we started.
        bpy.ops.object.mode_set(mode='OBJECT')
        scene.objects.active = shapeObj
        return {'FINISHED'}



###
# Class for script-manipulating functions
#
class QuickTalk_Script:

  phoneme_dictionary = {}

  ###
  # Load the script at init
  #
  def __init__(self,filename):
      file = open(bpy.path.abspath(filename),"r")
      self.lines = file.readlines()
      file.close()

      #Parse it
      self.parsed = "okay"
      self.voices = {}
      self.dialogues = []
      currentVoice = "narator"
      currentDialogue = {}
      currentDialogue['voice'] = currentVoice;
      currentDialogue['lines'] = []
      currentDialogue['totalwords'] = 0
      numWords=0
      for l in self.lines:
        match = re.search("^([A-Za-z]*):",l)
        if(match):
          #Change voice
          currentVoice = match.group(1).lower()
          self.voices[currentVoice] = True
          if(len(currentDialogue['lines'])>0):
            self.dialogues.append(currentDialogue)
          currentDialogue = {}
          currentDialogue['voice'] = currentVoice;
          currentDialogue['lines'] = []
          currentDialogue['totalwords'] = 0
          numWords=0
        else:
          #Dialogue line
          words = l.split()
          currentLine = []
          if(len(words)>0):
            for w in words:
              w = re.sub('[\W_]+', '', w).lower()     #Remove non alphanumerics
              currentLine.append(w)
              currentDialogue['totalwords'] = currentDialogue['totalwords'] + 1
            currentDialogue['lines'].append(currentLine)

      if(len(currentDialogue['lines'])>0):
        self.dialogues.append(currentDialogue)
      self.dumpScript()
  ###
  # Get total number of words in this script
  # 
  def getTotalWords(self):
      total = 0
      for d in self.dialogues:
        total = total + d['totalwords']
      return total

  ###
  # Add the dialogue markers
  #
  def addDialogueMarkers(self):
      numFrames = bpy.context.scene.frame_end - bpy.context.scene.frame_start + 1
      numWords = self.getTotalWords()
      framesPerWord = numFrames/numWords

      #Switch to a timeline
      default_frame = bpy.context.scene.frame_current
      default_area = bpy.context.area.type
      bpy.context.area.type = ('TIMELINE')

      #Add some markers
      frame = bpy.context.scene.frame_start
      for d in self.dialogues:
        bpy.context.scene.frame_current = frame
        marker = bpy.ops.marker.add()
        bpy.ops.marker.rename(name=d['voice']+"!D")
        frame = frame + framesPerWord*d['totalwords']

      bpy.context.scene.frame_current = default_frame
      bpy.context.area.type = default_area


  ###
  # Add the line markers
  # Note: We can only have one marker per frame, so
  # we can't add in the first line from each dialogue.
  #
  def addLineMarkers(self):
      #Switch to a timeline
      default_frame = bpy.context.scene.frame_current
      default_area = bpy.context.area.type
      bpy.context.area.type = ('TIMELINE')

      #Find the dialogue markers
      dialogueStarts = []
      for m in bpy.context.scene.timeline_markers:
        if(m.name[-2:]=="!D"):
          frame = m.frame
          dialogueStarts.append(frame)
      dialogueStarts.append(bpy.context.scene.frame_end)  #Fake one at the end of the scene
      dialogueStarts = sorted(dialogueStarts)

      #Add line markers for each dialogue
      n=0;
      for d in self.dialogues:
        frame = dialogueStarts[n];
        start = dialogueStarts[n]
        n+=1
        end = dialogueStarts[n]
        framesPerWord = (end-start) / d['totalwords']

        ln = 0
        for l in d['lines']:
            ln=ln+1
            if(ln>1):
              bpy.context.scene.frame_current = frame
              marker = bpy.ops.marker.add()
              name=l[0][0:10]+"!L"
              bpy.ops.marker.rename(name=name)
            frame = frame + framesPerWord*len(l)
           
     

      bpy.context.scene.frame_current = default_frame
      bpy.context.area.type = default_area

    
  ###
  # Add the word markers
  # Note: We can only have one marker per frame, so
  # we can't add in the first word from each line.
  #
  def addWordMarkers(self):
      #Switch to a timeline
      default_frame = bpy.context.scene.frame_current
      default_area = bpy.context.area.type
      bpy.context.area.type = ('TIMELINE')

      #Find the existing markers
      lineStarts = []
      for m in bpy.context.scene.timeline_markers:
        if((m.name[-2:]=="!D") or (m.name[-2:]=="!L")):
          frame = m.frame
          lineStarts.append(frame)
      lineStarts.append(bpy.context.scene.frame_end)  #Fake one at the end of the scene
      lineStarts = sorted(lineStarts)

      #Add word markers for each line
      n=0;
      for d in self.dialogues:
        for l in d['lines']:
          frame = lineStarts[n];
          start = lineStarts[n]
          n+=1
          end = lineStarts[n]
          framesPerWord = (end-start) / len(l)

          wn = 0
          for w in l:
            wn=wn+1
            if(wn>1):
              bpy.context.scene.frame_current = frame
              marker = bpy.ops.marker.add()
              name=w[0:10]+"!W"
              bpy.ops.marker.rename(name=name)
            frame = frame + framesPerWord

      bpy.context.scene.frame_current = default_frame
      bpy.context.area.type = default_area


  ###
  # Load Dictionary Function is mostly ripped out
  # of the Papagayo source code
  def LoadDictionary(self):
      mappings = {
        "AA0":"AI",
        "AA1":"AI",
        "AA2":"AI",
        "AE0":"AI",
        "AE1":"AI",
        "AE2":"AI",
        "AH0":"AI",
        "AH1":"AI",
        "AH2":"AI",
        "AO0":"O",
        "AO1":"O",
        "AO2":"O",
        "AW0":"O",
        "AW1":"O",
        "AW2":"O",
        "AY0":"AI",
        "AY1":"AI",
        "AY2":"AI",
        "B":"MBP",
        "CH":"ETC",
        "D":"ETC",
        "DH":"ETC",
        "EH0":"E",
        "EH1":"E",
        "EH2":"E",
        "ER0":"E",
        "ER1":"E",
        "ER2":"E",
        "EY0":"E",
        "EY1":"E",
        "EY2":"E",
        "F":"FV",
        "G":"ETC",
        "HH":"ETC",
        "IH0":"AI",
        "IH1":"AI",
        "IH2":"AI",
        "IY0":"E",
        "IY1":"E",
        "IY2":"E",
        "JH":"ETC",
        "K":"ETC",
        "L":"L",
        "M":"MBP",
        "N":"ETC",
        "NG":"ETC",
        "OW0":"O",
        "OW1":"O",
        "OW2":"O",
        "OY0":"WQ",
        "OY1":"WQ",
        "OY2":"WQ",
        "P":"MBP",
        "R":"ETC",
        "S":"ETC",
        "SH":"ETC",
        "T":"ETC",
        "TH":"TH",
        "UH0":"U",
        "UH1":"U",
        "UH2":"U",
        "UW0":"U",
        "UW1":"U",
        "UW2":"U",
        "V":"FV",
        "W":"WQ",
        "Y":"ETC",
        "Z":"ETC",
        "ZH":"ETC",
        "E21":"E",
      }
      #Alternate mappings for MHX2 import
      if(bpy.context.scene.quicktalk_bone_option == "2"):
        mappings = {
          "AA0":"AH",
          "AA1":"AH",
          "AA2":"AH",
          "AE0":"AH",
          "AE1":"AH",
          "AE2":"AH",
          "AH0":"AH",
          "AH1":"AH",
          "AH2":"AH",
          "AO0":"O",
          "AO1":"O",
          "AO2":"O",
          "AW0":"O",
          "AW1":"O",
          "AW2":"O",
          "AY0":"AH",
          "AY1":"AH",
          "AY2":"AH",
          "B":"MBP",
          "CH":"Etc",
          "D":"Etc",
          "DH":"Etc",
          "EH0":"EH",
          "EH1":"EH",
          "EH2":"EH",
          "ER0":"EH",
          "ER1":"EH",
          "ER2":"EH",
          "EY0":"EE",
          "EY1":"EE",
          "EY2":"EE",
          "F":"FV",
          "G":"G",
          "HH":"Etc",
          "IH0":"AH",
          "IH1":"AH",
          "IH2":"AH",
          "IY0":"EE",
          "IY1":"EE",
          "IY2":"EE",
          "JH":"Etc",
          "K":"Etc",
          "L":"L",
          "M":"MBP",
          "N":"Etc",
          "NG":"Etc",
          "OW0":"O",
          "OW1":"O",
          "OW2":"O",
          "OY0":"OO",
          "OY1":"OO",
          "OY2":"OO",
          "P":"MBP",
          "R":"R",
          "S":"S",
          "SH":"SH",
          "T":"Etc",
          "TH":"TH",
          "UH0":"OO",
          "UH1":"OO",
          "UH2":"OO",
          "UW0":"OO",
          "UW1":"OO",
          "UW2":"OO",
          "V":"FV",
          "W":"OO",
          "Y":"Etc",
          "Z":"Etc",
          "ZH":"Etc",
          "E21":"EE",
        }


      inFile = open(bpy.path.abspath(bpy.context.scene.quicktalk_dict_file), 'r')

      for line in inFile.readlines():
        if line[0] == '#':
          continue # skip comments in the dictionary
        # strip out leading/trailing whitespace
        line.strip()
        line = line.rstrip('\r\n')

        # split into components
        entry = line.split()
        if len(entry) == 0:
          continue
        # Ditch dules that have (xx) after 'en
        if entry[0].endswith(')'):
          continue
        # add this entry to the in-memory dictionary
        for i in range(len(entry)):
          name = entry[0]
          name = re.sub('[\W_]+', '', name).lower()     #Remove non alphanumerics
          if i == 0:
            self.phoneme_dictionary[name] = []
          else:
            rawentry = entry[i]
            try:
              entry[i] = entry[i]
            except:
              print("Unknown phoneme:", entry[i], "in word:", entry[0])
            self.phoneme_dictionary[name].append(mappings[entry[i]])
      inFile.close()
      inFile = None


  ###
  # Plot a single dot on a timeline
  #
  def plotDot(self,name,value,frame):
    if((name=="MBP") and (not "MBP" in bpy.context.active_object.pose.bones)):
        name="M"
    if name in bpy.context.active_object.pose.bones:
      bone = bpy.context.active_object.pose.bones[name]
      if(bpy.context.scene.quicktalk_bone_option == "0"):
        #X-Rotation
        bone.rotation_euler = (value,0,0)
        bone.keyframe_insert("rotation_euler",0,frame,"QuickTalk")        #0=x, 1=y, 2=z
      elif(bpy.context.scene.quicktalk_bone_option == "1"):
        #X-Translation
        bone.location = (value,0,0)
        bone.keyframe_insert("location",0,frame,"QuickTalk")        #0=x, 1=y, 2=z
    else:
        print("Can't find bone to plot "+name+" at "+str(value)+" to "+str(frame))

  ###
  # Plot a single phoneme to the timeline
  #
  def plotPhoneme(self,p,last,start,step):
    if(bpy.context.scene.quicktalk_bone_option == "2"):
      #MHX2-Imported Viseme buttons.
      bpy.context.scene.frame_current = start;
      t = bpy.context.scene.tool_settings.use_keyframe_insert_auto;
      bpy.context.scene.tool_settings.use_keyframe_insert_auto=True;
      bpy.ops.mhx2.set_viseme(viseme=p);
      bpy.context.scene.tool_settings.use_keyframe_insert_auto=t;
      return;
    else:
      #Rotate or Translate, plot actual timeline points...
      if(p!=last):
        ##Only turn it down if it wasn't the last phoneme
        self.plotDot(p,0,int(start))
      self.plotDot(p,1.571,int(start+step))
      self.plotDot(p,0,int(start+step+step))

  ###
  # Plot a specific word at a specific place
  #
  def plotWordToTimeline(self,w,frame,length):
      phonemes = self.phoneme_dictionary[w.lower()] 
      if(length > len(phonemes) * 5):
        #Obviously this word has a gap after it, fix the length lower
        length = len(phonemes) * 4;
   
      step = length/len(phonemes)
      current = frame-step/2
      lastPhoneme = "non"
      for p in phonemes:
        self.plotPhoneme(p,lastPhoneme,current,step)
        lastPhoneme = p
        current = current+step
      if(bpy.context.scene.quicktalk_bone_option == "2"):
        #Return to 'Rest' at the end of the word.
        self.plotPhoneme("Rest",lastPhoneme,current,step);
            

  ###
  # Plot the phonemes to the timeline.
  #
  def plotTimelines(self):
      #Switch to a timeline
      default_frame = bpy.context.scene.frame_current
      default_area = bpy.context.area.type
      bpy.context.area.type = ('TIMELINE')

      #Find the word-start markers
      wordStarts = []
      for m in bpy.context.scene.timeline_markers:
        if((m.name[-2:]=="!D") or (m.name[-2:]=="!L") or (m.name[-2:]=="!W")):
          frame = m.frame
          wordStarts.append(frame)
      wordStarts.append(bpy.context.scene.frame_end)  #Fake one at the end of the scene
      wordStarts = sorted(wordStarts)

      #Add the actual plots
      selectedobjectname = bpy.context.active_object.name.lower()
      n=0;
      for d in self.dialogues:
          for l in d['lines']:
            if(bpy.context.scene.quicktalk_bone_option == "2"):
              #Start with a "Rest" if we're MXH2 import.
              self.plotPhoneme("Rest","non",wordStarts[n]-3,3);
            for w in l:
              startFrame = wordStarts[n]
              n=n+1
              endFrame = wordStarts[n]
              if selectedobjectname[0:len(d['voice'])] == d['voice']:
                self.plotWordToTimeline(w,startFrame,endFrame-startFrame)
              else:
                print("Non-Matching speaker: "+selectedobjectname[0:len(d['voice'])]+":"+d['voice'])

      bpy.context.scene.frame_current = default_frame
      bpy.context.area.type = default_area



  ###
  # Debug function to dump script to stdout
  # 
  def dumpScript(self):
      for d in self.dialogues:
        print("Dialogue - "+d['voice']+" - "+str(d['totalwords'])+" words:")
        for l in d['lines']:
          print("     ",end="")
          for w in l:
            print(w,end=" ")
          print()
          
#end class script



###
# The Guess Dialogue Markers Function
#
class QuickTalk_GuessDialogue(bpy.types.Operator):
    """Guess Quicktalk Dialogue Markers"""         # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "object.quicktalk_guess_dialogue"   # unique identifier for buttons and menu items to reference.
    bl_label = "Guess Dialogue Start Markers"  # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}          # enable undo for the operator.

    def execute(self, context):
        script = QuickTalk_Script(context.scene.quicktalk_script_file)
        script.addDialogueMarkers()
        
        return {'FINISHED'}

###
# The Guess Line Markers Function
#
class QuickTalk_GuessLines(bpy.types.Operator):
    """Guess Quicktalk Line Markers"""         # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "object.quicktalk_guess_lines" # unique identifier for buttons and menu items to reference.
    bl_label = "Guess Line Start Markers"  # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}          # enable undo for the operator.

    def execute(self, context):
        script = QuickTalk_Script(context.scene.quicktalk_script_file)
        script.addLineMarkers()
        
        return {'FINISHED'}


###
# The Guess Word Markers Function
#
class QuickTalk_GuessWords(bpy.types.Operator):
    """Guess Quicktalk Word Markers"""         # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "object.quicktalk_guess_words" # unique identifier for buttons and menu items to reference.
    bl_label = "Guess Word Start Markers"  # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}          # enable undo for the operator.

    def execute(self, context):
        script = QuickTalk_Script(context.scene.quicktalk_script_file)
        script.addWordMarkers()
        
        return {'FINISHED'}

###
# The Actual Plotting of data to timelines! Finally!
#
class QuickTalk_QuicktalkPlot(bpy.types.Operator):
    """Plot Quicktalk data to timeline"""         # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "object.quicktalk_plot_timeline"   # unique identifier for buttons and menu items to reference.
    bl_label = "Plot Quicktalk Data To Timeline"  # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}          # enable undo for the operator.

    def execute(self, context):
        script = QuickTalk_Script(context.scene.quicktalk_script_file)
        script.LoadDictionary()
        script.plotTimelines()
        
        return {'FINISHED'}

