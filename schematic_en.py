#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Schematic.py: Loads an schematic in a Minecraft Pi world"""

import Tkinter as tk
from Tkinter      import *
from ttk          import *
from tkFileDialog import askopenfilename
from socket       import error as socket_error
from subprocess   import Popen
import mcpi.minecraft as minecraft
import nbt, time, sys, errno, os
import Image, ImageTk, ttk

class App:
   def __init__(self, master):
      """Handles all GUI related things"""
      frame = Frame(master)
      frame.pack()

      master.wm_title('Schematic loader')

      img = ImageTk.PhotoImage(Image.open(os.path.dirname(os.path.realpath(__file__)) + '/vermislablogo.png'))
      logo = ttk.Label(frame, image = img)
      logo.image = img
      logo.grid(row = 0, column = 0, columnspan = 3)

      separator = ttk.Separator(frame, orient = HORIZONTAL)
      separator.grid(row = 1, column = 0, columnspan = 3, sticky = 'we')

      self.button = ttk.Button(frame, text = 'Load schematic', command = self.openfile)
      self.button.grid(row = 2, column = 2, padx = 5, pady = 5)

      self.button = ttk.Button(frame, text = 'Flat map', command = self.flatland)
      self.button.grid(row = 2, column = 1, padx = 5, pady = 5)

      self.button = tk.Button(frame, text = 'Delete schematic', command = self.delete, fg = 'red')
      self.button.grid(row = 2, column = 0, padx = 5, pady = 5)

      self.button = ttk.Button(frame, text = 'Teleport to 0,0,0', command = self.teletozero)
      self.button.grid(row = 3, column = 0, padx = 5, pady = 5, columnspan = 3)



   def openfile(self):
      """Displays the schematic chooser dialog and loads it into the game"""
      global file
      file = askopenfilename()
      loadSchematic(file)

   def delete(self):
      """Deletes an already loaded schematic"""
      global file, playerX, playerY, playerZ
      loadSchematic(file, 1, playerX, playerY, playerZ)

   def flatland(self):
      """Flatens the world to simplify construction, or just for cleanup"""
      mc.setBlocks(-128, -10, -128, 128, 64, 128, 0)
      mc.setBlocks(-128, -10, -128, 128, -64, 128, 24)
      mc.postToChat('Map flattened!')

   def teletozero(self):
      """Teleports player to coordinate origin"""
      mc.player.setPos(0, 0, 0)

def loadSchematic(schematicToImport, deleteSchematic = 0, delX = 0, delY = 0, delZ = 0):
   """
   Loads schematic into the game.

   Parameters:
   ----------
   schematicToImport : string
      A string that represents the absolute or relative filepath of the schematic
   deleteSchematic : int
      Set to 1 to delete instead of loading. Defaults to 0
   delX : int
      Only used if deleteSchematic is set. Defines the x coordinate of the schematic to be deleted. Defaults to 0
   delY : int
      Only used if deleteSchematic is set. Defines the y coordinate of the schematic to be deleted. Defaults to 0
   delZ : int
      Only used if deleteSchematic is set. Defines the z coordinate of the schematic to be deleted. Defaults to 0
   """
   delete = True if (deleteSchematic == 1) else 0
   infile = nbt.nbt.NBTFile(schematicToImport, 'rb')

   if(infile['Width'] == "Classic"):
      raise ImportError('This schematic format is not supported')

   width = infile['Width'].value
   length = infile['Length'].value
   height = infile['Height'].value

   global playerX, playerY, playerZ

   if(delete == False):
      playerX = playerY = playerZ = 0
      playerX, playerY, playerZ = mc.player.getPos()
      mc.postToChat('Loading {}...'.format(schematicToImport))
      mc.setBlocks(playerX,
		   playerY,
		   playerZ,
		   playerX + width,
		   playerY + height,
		   playerZ + length,
		   0)

      index = 0

      for x in range(width):
         for y in range(height):
            for z in range(length):
               arrayPos = (y * length + z) * width + x
               id = infile['Blocks'][arrayPos]
               data = infile['Data'][arrayPos]
               mc.setBlock(playerX + x,
			   playerY + y,
			   playerZ + z,
			   0 if delete else id,
			   data)
               index += 1
               if(id != 0):
                  time.sleep(0.0001)
               try:
                  if(((float(index) / len(infile['Blocks'])) * 100) % 10 == 0):
                     mc.postToChat('{}% loaded...'.format(str(index * 100 / len(infile['Blocks']))))
               except ZeroDivisionError:
                  continue

      mc.postToChat('Schematic loaded!')
   else:
      mc.postToChat('Deleting {}...'.format(schematicToImport))
      mc.setBlocks(delX,
		   delY,
		   delZ,
		   delX + width,
		   delY + height,
		   delZ + length,
		   0)
      mc.postToChat('Modelo borrado!')

#minecraftProcess = Popen([]) TODO: replace with minecraft pi absolute path

print('Waiting for Minecraft to start...')
while 1:
   try:
      mc = minecraft.Minecraft.create()
      try:
         mc
         break
      except NameError:
         continue
   except socket_error as serr:
      continue

root = Tk()
root.style = Style()
root.style.theme_use('clam')

app = App(root)
root.mainloop()
