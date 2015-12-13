# aid to smi-automatically fly & grade HW4a
# copy with ClassCode into directory to be graded
# import grd4a [starts]; SET w/ AC/HC module (w/ def PC(sf,fDat...)
# type in parameters to the args window and see if 'OK' is returned

# Simple FG PID flight control for throttle/speed, elev/pitch angle, aileron/roll angle
# access to online PID parameters if desired
# import grd4a; a=grd4a.grd4a(); a.start()
# zero will hold 78 degree bank pretty well at 210 KIAS and 1.5 pitch

# copy grd4a and ClassCode/ into target directory; target class w/ AC/HC to text box, press HC
# enter dialog for PC

import Ckpt as Ckpt
import tkinter as tk
from tkinter import ttk
import importlib

import imp, sys
def rel():
	imp.reload(sys.modules['grd4a'])

import Utilities

class PID:
	'''PID from flightgear; if built w/ pnl=True, bldPanel constructs a window shared among PIDs where their individual parameters can be changed while running by setting tk.Text values and pushing UPLOAD'''

	pidWin = 'notSet'		# shared parameter window
	nxtRow = 1
	prmDescs = ['Kp', 'Ti', 'Td', 'Beta', 'Gamma', 'Alpha']
	dspPIDs = []				# list of PID objects included in the display

	@classmethod
	def upldPrms(cls):
		'''service UPLOAD button, copying all six parameters as currently displayed to each of the displayed PID objects'''
		for pid in cls.dspPIDs:
			pid.kp 	 = float(pid.prmTxts[0].get(1.0, tk.END))
			pid.ti 	 = float(pid.prmTxts[1].get(1.0, tk.END))
			pid.td 	 = float(pid.prmTxts[2].get(1.0, tk.END))
			pid.bet 	 = float(pid.prmTxts[3].get(1.0, tk.END))
			pid.gam = float(pid.prmTxts[4].get(1.0, tk.END))
			pid.alph = float(pid.prmTxts[5].get(1.0, tk.END))

	def __init__(sf,nm,imn,imx,ikp,iu,iti=5.,itd=2.,ibt=0.9,igm=0.1,ial=0.1,pnl=False):
		'''PID with output u for name=nm, min/max u=imn/imx, prop coef ikp, initial control value=iu, integrator time period=iti, derivator time period=itd, beta=ibt, gamma=igm, alpha=ial)
		based on www.flightgear.org/Docs/XMLAutopilot/node3.html'''
		sf.nam = nm;	sf.mnu = imn;		sf.mxu = imx		# control output desc
		sf.bet = ibt;		sf.gam = igm;		sf.alph = ial		# internal parameters
		sf.kp = ikp;		sf.ti = iti;				sf.td = itd			# control parameters
		sf.tf = sf.alph * sf.td
		sf.uOld = iu			# initial control output value
		sf.tim = 'notSet'		# current time
		if pnl: sf.bldPanel()

	def ctl(sf,ref,cur,tm):
		'''compute a new u output for plant reference ref, current plant value cur, time tm'''
		if sf.tim == 'notSet':	# initialize on first call
			sf.tim = tm
			sf.edfn0 = sf.edfn1 = sf.edfn2 = 0.	# all derivatives zero
			sf.ep1 = 0.
			return sf.uOld
		if tm == sf.tim: return sf.uOld		# same time point, N/C & avoids zero divide
		ts = tm - sf.tim			# delta time
		en = ref - cur				# Error	in plant output
		ep = sf.bet * en			# Proportional error w/ reference weighting
		ed = sf.gam * en
		ratTsf = ts / sf.tf
		ratTsf1 = ratTsf + 1.0
		edfn0 = sf.edfn1 / ratTsf1 + ed * ratTsf / ratTsf1
		edfnBar = edfn0 - 2. * sf.edfn1 + sf.edfn2
		du = sf.kp * ((ep - sf.ep1) + (en * ts / sf.ti) + (sf.td / ts) * edfnBar)
		sf.edfn2 = sf.edfn1;		sf.edfn1 = edfn0		# upgrade / save for next call
		sf.ep1 = ep;					sf.tim = tm
		sf.uOld += du			# upgrade full control value
		if sf.uOld < sf.mnu: sf.uOld = sf.mnu			# chk min/max values
		elif sf.uOld > sf.mxu: sf.uOld = sf.mxu
		return sf.uOld

	def bldPanel(sf):
		'''construct the shared PID display window'''
		PID.dspPIDs.append(sf)				# list of all PIDs w/ parameters displayed
		nPrms = len(PID.prmDescs)
		if PID.pidWin == 'notSet': 			# first: window does not yet exist
			PID.pidWin= tk.Toplevel()
			PID.pidWin.grid()
			PID.pidWin.title('PID Parameters'.format(sf.nam))
			# upload button to call (shared) class method upldPrms
			upldB = tk.Button(PID.pidWin, text='UPLOAD', command=PID.upldPrms)
			upldB.grid(row=0, column=0) # , sticky='EW')
			for i in range(len(PID.prmDescs)):	# parameter labels, top line
				ttk.Label(PID.pidWin, text=PID.prmDescs[i], relief=tk.FLAT).grid(row=0, column=i+1)
		# each displayed PID has a line: PID name, six tk.Text's for its parameters
		ttk.Label(PID.pidWin, text=sf.nam, relief=tk.FLAT).grid(row=PID.nxtRow, column=0)
		sf.prmTxts = []
		prms = (sf.kp, sf.ti, sf.td, sf.bet, sf.gam, sf.alph)
		for i in range(nPrms):		# insert the initial parameter values
			ptxt = tk.Text(PID.pidWin, width=10, height=1)
			ptxt.grid(row=PID.nxtRow, column=i+1)
			ptxt.insert('1.0', '{}'.format(prms[i]))
			sf.prmTxts.append(ptxt)
		PID.nxtRow += 1		# get ready for the next one


class clgrd4a (Ckpt.Ckpt):
	'''like Pilot; subclass of the class Ckpt in the file Ckpt to test low level PIDs for speed, Pitch & Roll'''
	def __init__(sf,tsk='HW4a',rc=False,gui=False):
		super().__init__(tsk, rc, gui)
		sf.strtTime = None
		sf.duration = None
		sf.lstTime = None
		sf.reset = 10
		sf.rpt = 0
		sf.grd4aGui()
		# PID args: name,min,max,ikp,iu,  iti=5.,itd=2.,  ibt=0.9,igm=0.1,ial=0.1
		#~ sf.speedPid = PID('Speed', 0.0, 1.0, 0.01, 0.6, pnl=True)
		#~ sf.pitchPid = PID('Pitch', -1.0, 1.0, -0.05, -0.16, pnl=True)
		#~ sf.rollPid = PID('Roll', -1.0, 1.0, 0.007, 0., itd=3., ibt=0.95, pnl=True)
		sf.speedPid = PID('Speed', 0.0, 1.0, 0.01, 0.6)
		sf.pitchPid = PID('Pitch', -1.0, 1.0, -0.05, -0.16)
		sf.rollPid = PID('Roll', -1.0, 1.0, 0.007, 0., itd=3., ibt=0.95)
		sf.cmdTxts[0].insert('1.0', '210')		# initial speed, pitch & roll targets
		sf.cmdTxts[1].insert('1.0', '1')
		sf.cmdTxts[2].insert('1.0', '0')
		sf.sendCmd()
		sf.inCtl.set(2)
		sf.pltI = 'notSet'
		sf.externalCtl = False		# set to True while AC. or HC.DO is active

	def ai(sf,fDat,fCmd):
		'''Override with the Pilot decision maker, args: fltData and cmdData from Utilities.py'''
		if not sf.strtTime:
			sf.strtTime = fDat.time	# initialize start time
			sf.lstTime = sf.strtTime
		elif sf.lstTime == fDat.time: return	# no time elapsed
		sf.savDat = fDat
		sf.savCmd = fCmd
		if sf.externalCtl:									# under AC or HC control
			try: cont = sf.pltI.DO(fDat, fCmd)	# protect call to DO
			except:
				print(' *** DO Error: ', sys.exc_info()[0])
				sf.externalCtl = False
			else:
				if cont == 'DONE':
					print('DONE', cont)
					sf.externalCtl = False
		else:
			if sf.cmdVals[0] != 10000: fCmd.throttle = sf.speedPid.ctl(sf.cmdVals[0], fDat.kias, fDat.time)
			if sf.cmdVals[1] != 10000: fCmd.elevator = sf.pitchPid.ctl(sf.cmdVals[1], fDat.pitch, fDat.time)
			if sf.cmdVals[2] != 10000: fCmd.aileron = sf.rollPid.ctl(sf.cmdVals[2], fDat.roll, fDat.time)
		# display current state and controls in window
		for fFmt,txtB,fdVal in zip(sf.fltFmts, sf.fltTxts, fDat.getFData()):
			txtB.delete('1.0', tk.END)
			txtB.insert('1.0', fFmt.format(fdVal))
		sf.ctlTxts[0].delete('1.0', tk.END)
		sf.ctlTxts[0].insert('1.0', '{:7.4f}'.format(fCmd.throttle))
		sf.ctlTxts[1].delete('1.0', tk.END)
		sf.ctlTxts[1].insert('1.0', '{:7.4f}'.format(fCmd.elevator))
		sf.ctlTxts[2].delete('1.0', tk.END)
		sf.ctlTxts[2].insert('1.0', '{:7.4f}'.format(fCmd.aileron))
		sf.myWin.update()


		#~ if not sf.strtTime:
			#~ sf.strtTime = fDat.time	# initialize start time
			#~ sf.lstTime = sf.strtTime
		#~ if sf.rpt < sf.reset:	# print every sf.reset iterations
			#~ sf.rpt += 1
		#~ else:
			#~ sf.rpt = 0
			#~ dt = fDat.time - sf.lstTime
			#~ if dt > 0.0:
				#~ print('Ptch/Roll: {:5.1f} / {:5.1f} Thr / Ail / Elev: {:.1f} / {:.1f} / {:.1f} Last/Dur/Time: {:.3f} / {:.3f} / {:.3f}'.format(fDat.pitch, fDat.roll, fCmd.throttle, fCmd.aileron, fCmd.elevator, dt, fDat.time - sf.strtTime, fDat.time))
				#~ sf.lstTime = fDat.time

	def grd4aGui(sf):
		sf.myWin = tk.Toplevel()
		sf.myWin.grid()
		sf.myWin.title('Flight Control Panel')
		fltDesc = ['KIAS', 'Altitude', 'Heading', 'Pitch', 'Roll', 'Latitude', 'Longitude']	# flight info display labels
		sf.fltFmts = ['{:5.1f}     ', '{:7.1f}   ', '{:5.1f}     ',  '{:5.1f}     ',  '{:5.1f}     ',  '{:5.1f}     ',  '{:5.1f}     ']
		cmdAcHc = ['DltAlt', 'DecAng', 'FnSpeed', 'Radius', 'DltAng']
		cmdDesc = ['KIAS', 'Pitch', 'Roll']

		sf.cmdVals = [-1.0 for cd in cmdDesc]
		ctlDesc = ['Throt', 'Elev', 'Ailer']
		col = 0			# make columns more module for easier moving
		# Flight data display
		fltLbls = [ttk.Label(sf.myWin, text=fltDesc[i], relief=tk.FLAT) for i in range(len(fltDesc))]
		sf.fltTxts = [tk.Text(sf.myWin, width = 10, height=1) for fd in fltDesc]
		for i in range(len(fltDesc)):
			fltLbls[i].grid(row=i, column=col, sticky=tk.E)
			sf.fltTxts[i].grid(row=i, column=col+1)
		col += 2
		# AC / HC Command input display
		cmdLbls = [ttk.Label(sf.myWin, text=cmdD, relief=tk.FLAT) for cmdD in cmdAcHc]
		sf.achcTxts = [tk.Text(sf.myWin, width = 10, height=1) for cd in cmdAcHc]
		for i in range(len(cmdAcHc)):
			cmdLbls[i].grid(row=i, column=col, sticky=tk.E)
			sf.achcTxts[i].grid(row=i, column=col+1)
		col += 2

		# PID Command input display
		cmdLbls = [ttk.Label(sf.myWin, text=cmdD, relief=tk.FLAT) for cmdD in cmdDesc]
		sf.cmdTxts = [tk.Text(sf.myWin, width = 10, height=1) for cd in cmdDesc]
		for i in range(len(cmdDesc)):
			cmdLbls[i].grid(row=i, column=col, sticky=tk.E)
			sf.cmdTxts[i].grid(row=i, column=col+1)
		col += 2
		# Control output display
		ctlLbls = [ttk.Label(sf.myWin, text=ctlD, relief=tk.FLAT) for ctlD in ctlDesc]
		sf.ctlTxts = [tk.Text(sf.myWin, width=10, height=1) for cd in ctlDesc]
		for i in range(len(ctlDesc)):
			ctlLbls[i].grid(row=i, column=col, sticky=tk.E)
			sf.ctlTxts[i].grid(row=i, column=col+1)
		col += 2

		# Set module button & Module Name
		modB = tk.Button(sf.myWin, text='SET', command=sf.setMod)
		modB.grid(row=len(cmdAcHc), column=2, sticky='EW')
		sf.modTxt = tk.Text(sf.myWin, width=10, height=1)
		sf.modTxt.grid(row=len(cmdAcHc), column=3, sticky='EW')

		# AC/HC button and Args
		argsB = tk.Button(sf.myWin, text='AC/HC', command=sf.setArgs)
		argsB.grid(row=len(cmdAcHc)+1, column=2, sticky='EW')
		sf.argsTxt = tk.Text(sf.myWin, width=20, height=1)
		sf.argsTxt.grid(row=len(cmdAcHc)+1, column=3, columnspan=4, sticky='EW')

		# Send button
		sndB = tk.Button(sf.myWin, text='Send', command=sf.sendCmd)
		sndB.grid(row=len(cmdAcHc), column=5, sticky='EW')
		# Start button
		strtB = tk.Button(sf.myWin, text='Start', command=sf.start)
		strtB.grid(row=len(cmdAcHc), column=7, sticky='EW')
		# Quit everything button
		sf.quitB = tk.Button(sf.myWin, text='Quit', command=sf.endAll)
		sf.quitB.grid(row=7, column=0, sticky='EW')
		# Keyboard, Cockpit, AI selection radio buttons
		sf.inCtl = tk.IntVar()
		sf.rb1 = ttk.Radiobutton(sf.myWin, text='Kbd', variable=sf.inCtl, value=0, command=sf.selected)
		sf.rb2 = ttk.Radiobutton(sf.myWin, text='AI', variable=sf.inCtl, value=2, command=sf.selected)
		sf.rb1.grid(row=7, column=1)
		sf.rb2.grid(row=7, column=2)

	def sendCmd(sf):
		'''Service the Send buton; copies float values of the command tk.Text's to sf.cmdVals'''
		sf.externalCtl = False		# disengage any current AC / HC control
		for i in range(len(sf.cmdTxts)):
			try: sf.cmdVals[i] = float(sf.cmdTxts[i].get(1.0, tk.END))
			except ValueError: sf.cmdVals[i] = 10000
		print('Send to FG', sf.cmdVals)

	#~ def startCmd(sf):
		#~ '''Start FG'''
		#~ sf.start()

	def setMod(sf):
		'''Service the module set button'''
		#	AC: PC & PLAN	fDat, deltaAltitude, angle, finalSpeed
		#	HC: PC & PLAN	fDat, radius, deltaAngle
		# Build standin FltData and CmdData for AC / HC PC's, PLAN's, & maybe DO's
		sf.fd = Utilities.FltData()
		sf.fd.kias = 210.; sf.fd.altitude=2185.;	sf.fd.head=295.; sf.fd.pitch=2.544; sf.fd.roll=0.0
		sf.fd.latitude=37.623935699;	sf.fd.logitude=-122.385467529;	sf.fd.time=27.225
		sf.cd = Utilities.CmdData()
		sf.cd.aileron=0.0;	sf.cd.elevator=-0.15;	sf.cd.rudder=0.0;	sf.cd.throttle=0.5;	sf.cd.mixture=1.0
		modNam = sf.modTxt.get(1.0, tk.END)[:-1]		# get the module name
		print('Building {}'.format(modNam))
		pltM = importlib.import_module(modNam)		# module
		pltC = getattr(pltM, modNam)						# class
		sf.pltI = pltC()												# instance
		sf.fcn = 'No function'
		if sf.pltI.PC.__code__.co_argcount == 5:
			sf.fcn = 'Altitude Change'
			print('AC: DltAlt ft, angle deg, FinSpd knots')
		elif sf.pltI.PC.__code__.co_argcount == 4:
			sf.fcn = 'Heading Change'
			print('HC: radius ft & angle deg')
		else:
			print('Wrong number of arguments: {} (need 4 or 5)'.format(sf.pltI.PC.__code__.co_argcount))

	def setArgs(sf):
		args = list(map(float, sf.argsTxt.get(1.0, tk.END)[:-1].split()))
		print('PC', sf.fcn, args)
		print(sf.pltI.PC(sf.fd, *args))
		if sf.strtTime:
			print('PLAN', sf.fcn, args)
			print(sf.pltI.PLAN(sf.fd, *args))
			sf.externalCtl = True


 		#~ print('\ndat', end=' ')
		#~ for val in sf.savDat.getFData():
			#~ print('{:.3f}'.format(val), end=', ')
		#~ print('\ncmd', end=' ')
		#~ for val in (sf.savCmd.aileron, sf.savCmd.elevator, sf.savCmd.rudder, sf.savCmd.throttle, sf.savCmd.mixture, sf.savCmd.magnitos):
			#~ print('{:.3f}'.format(val), end=', ')
		#~ print()

	def selected(sf):
		'''service radio buttons for selecting inputs from Kbd, Ckpt, AI; NB: once Kbd is selected, AI can no longer be selected as the window (via sf.ai()) is no longer serviced'''
		if not sf.fg:
			print('Cannot select control input; no FGFS started')
			return
		if sf.inCtl.get()==0:	# keyboard so tell fgfs not to send command packets
			sf.fg.setKbd(True)
		else:
			sf.fg.setKbd(False)
#		print('selected', sf.inCtl.get())

	def endAll(sf):
		'''service the quit button'''
		super().endAll()			# kill FG & free port
		sf.myWin.destroy()			# main data / input window
		if PID.pidWin != 'notSet': PID.pidWin.destroy()		# possible PID display window

a=clgrd4a()
