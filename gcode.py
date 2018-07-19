#!/usr/bin/python
# -*- coding: utf-8 -*-
#######################################################
import wiringpi as gpio
from wiringpi import GPIO
import math



X_STEPS_PER_INCH=4800####根据指令修改，steps每INCH，steps每mm
X_STEPS_PER_MM=188.97
X_MOTOR_STEPS=200
Y_STEPS_PER_INCH=4800
Y_STEPS_PER_MM=188.97
Y_MOTOR_STEPS=200
Z_STEPS_PER_INCH=4800
Z_STEPS_PER_MM=188.97
Z_MOTOR_STEPS=200

#our maximum feedrates，默认值，最大进给速度
FAST_XY_FEEDRATE=100
FAST_Z_FEEDRATE=100

#Units in curve section
CURVE_SECTION_INCHES=0.019685
CURVE_SECTION_MM=0.5

#Set to one if sensor outputs inverting (ie: 1 means open, 0 means closed)
#RepRap opto endstops are *not* inverting.
SENSORS_INVERTING=0 ##传感器


X_STEP_PIN=8
X_DIR_PIN=9
X_MIN_PIN=4
X_MAX_PIN=1
X_ENABLE_PIN=15


Y_STEP_PIN=0
Y_DIR_PIN=2
Y_MIN_PIN=3
Y_MAX_PIN=5
Y_ENABLE_PIN=15

Z_STEP_PIN=21
Z_DIR_PIN=22
Z_MIN_PIN=7
Z_MAX_PIN=6
Z_ENABLE_PIN=15

x_units = float(X_STEPS_PER_INCH)
y_units = float(Y_STEPS_PER_INCH)
z_units = float(Z_STEPS_PER_INCH)
curve_section = CURVE_SECTION_INCHES

#x_direction = 0
#y_direction = 0
#z_direction = 0

feedrate = 0.0#梯形变速的匀速阶段进给速度
feedrate_micros = 0#每一个脉冲间隔时间
serial_count=0#数组

fpx=0
fpy=0
fpz=0


#---------定义结构体---------#

class directions:
	def __init__(self, xpart0,ypart0,zpart0):
		self.x = xpart0
		self.y = ypart0
		self.z = zpart0

direction = directions(0,0,0)

class currentunits:
	def __init__(self, xpart1,ypart1,zpart1):
		self.x = xpart1
		self.y = ypart1
		self.z = zpart1

current_units = currentunits(0.0,0.0,0.0)

class targetunits:
	def __init__(self, xpart2,ypart2,zpart2):
		self.x = xpart2
		self.y = ypart2
		self.z = zpart2

target_units = targetunits(0.0,0.0,0.0)

class deltaunits:
	def __init__(self, xpart3,ypart3,zpart3):
		self.x = xpart3
		self.y = ypart3
		self.z = zpart3

delta_units = deltaunits(0.0,0.0,0.0)

class currentsteps:
	def __init__(self, xpart4,ypart4,zpart4):
		self.x = xpart4
		self.y = ypart4
		self.z = zpart4

current_steps = currentsteps(0.0,0.0,0.0)

class targetsteps:
	def __init__(self, xpart5,ypart5,zpart5):
		self.x = xpart5
		self.y = ypart5
		self.z = zpart5

target_steps = targetsteps(0.0,0.0,0.0)

class deltasteps:
	def __init__(self, xpart6,ypart6,zpart6):
		self.x = xpart6
		self.y = ypart6
		self.z = zpart6

delta_steps = deltasteps(0.0,0.0,0.0)



#class fps:
#	def __init__(self, xpart4,ypart4,zpart4):
#		self.x = xpart4
#		self.y = ypart4
#		self.z = zpart4

#fp = fps(0.0,0.0,0.0)



def  init_steppers():

	#current_units.x = 0.0;
	#current_units.y = 0.0;
	#current_units.z = 0.0;
	#target_units.x = 0.0;
	#target_units.y = 0.0;
	#target_units.z = 0.0;

	#-----------引脚初始化--------#
	gpio.wiringPiSetup()  #初始化

	gpio.pinMode(X_STEP_PIN,GPIO.OUTPUT) # 把pin25设置为输出模式
	gpio.pinMode(X_DIR_PIN,GPIO.OUTPUT) # 把pin25设置为输出模式
	gpio.pinMode(X_ENABLE_PIN,GPIO.OUTPUT) # 把pin25设置为输出模式
	gpio.pinMode(X_MIN_PIN,GPIO.INPUT) # 把pin25设置为输入模式
	gpio.pinMode(X_MAX_PIN,GPIO.INPUT) # 把pin25设置为输入模式

	gpio.pinMode(Y_STEP_PIN,GPIO.OUTPUT) # 把pin25设置为输出模式
	gpio.pinMode(Y_DIR_PIN,GPIO.OUTPUT) # 把pin25设置为输出模式
	gpio.pinMode(Y_ENABLE_PIN,GPIO.OUTPUT) # 把pin25设置为输出模式
	gpio.pinMode(Y_MIN_PIN,GPIO.INPUT) # 把pin25设置为输入模式
	gpio.pinMode(Y_MAX_PIN,GPIO.INPUT) # 把pin25设置为输入模式

	gpio.pinMode(Z_STEP_PIN,GPIO.OUTPUT) # 把pin25设置为输出模式
	gpio.pinMode(Z_DIR_PIN,GPIO.OUTPUT) # 把pin25设置为输出模式
	gpio.pinMode(Z_ENABLE_PIN,GPIO.OUTPUT) # 把pin25设置为输出模式
	gpio.pinMode(Z_MIN_PIN,GPIO.INPUT) # 把pin25设置为输入模式
	gpio.pinMode(Z_MAX_PIN,GPIO.INPUT) # 把pin25设置为输入模式 

	gpio.digitalWrite(X_ENABLE_PIN,GPIO.LOW) #pin25输出为高电平
	gpio.digitalWrite(Y_ENABLE_PIN,GPIO.LOW) #pin25输出为高电平
	gpio.digitalWrite(Z_ENABLE_PIN,GPIO.LOW) #pin25输出为高电平


def set_target(x,y,z):
	target_units.x = x
	target_units.y = y
	target_units.z = z
	calculate_deltas()


def set_position(x,y,z):
	current_units.x = x
	current_units.y = y
	current_units.z = z
	calculate_deltas()


def calculate_deltas():

	delta_units.x = long(abs(target_units.x - current_units.x))
	delta_units.y = long(abs(target_units.y - current_units.y))
	delta_units.z = long(abs(target_units.z - current_units.z))
				
	####set our steps current, target, and delta
	current_steps.x = long(to_steps(x_units, current_units.x))
	current_steps.y = long(to_steps(y_units, current_units.y))
	current_steps.z = long(to_steps(z_units, current_units.z))

	target_steps.x = long(to_steps(x_units, target_units.x))
	target_steps.y = long(to_steps(y_units, target_units.y))
	target_steps.z = long(to_steps(z_units, target_units.z))

	delta_steps.x = long(abs(target_steps.x - current_steps.x))
	delta_steps.y = long(abs(target_steps.y - current_steps.y))
	delta_steps.z = long(abs(target_steps.z - current_steps.z))
	
	#what is our direction
	direction.x = int(target_units.x >= current_units.x)
	direction.y = int(target_units.y >= current_units.y)
	direction.z = int(target_units.z >= current_units.z)

	#set our direction pins as well
	gpio.digitalWrite(X_DIR_PIN,direction.x)
	gpio.digitalWrite(Y_DIR_PIN,direction.y)
	gpio.digitalWrite(Z_DIR_PIN,direction.z)


def to_steps(steps_per_unit,units):
	return steps_per_unit * units


def getcode(key,lines):  #search_string  未经测试函数
	length=len(lines)
	i=lines.find(key)
	i=i+1
	a=''
	while (lines[i]!=' '):
		a=a+lines[i]
		i=i+1
		if i==length:
			number=float(a)
			return number
	number=float(a)
	return number


def getMaxSpeed():
	if delta_steps.z > 0:
		return calculate_feedrate_delay(FAST_Z_FEEDRATE)
	else:
		return calculate_feedrate_delay(FAST_XY_FEEDRATE)


def calculate_feedrate_delay(feedrate):#####我们只要做xy的时间就行了，注意函数的return，已修改
	##how long is our line length?
	###distance = math.sqrt(delta_units.x*delta_units.x + delta_units.y*delta_units.y + delta_units.z*delta_units.z)
	distance = math.sqrt(delta_units.x*delta_units.x + delta_units.y*delta_units.y)
	global master_steps
	master_steps = 0
	
	##find the dominant axis
#	if delta_steps.x > delta_steps.y:##取最大的变化步数
#		if delta_steps.z > delta_steps.x:
#			master_steps = delta_steps.z
#		else:
#			master_steps = delta_steps.x
#	else:
#		if delta_steps.z > delta_steps.y:
#			master_steps = delta_steps.z
#		else:
#			master_steps = delta_steps.y
	if delta_steps.x > delta_steps.y:##取最大的变化步数
		master_steps = delta_steps.x
	elif delta_steps.x < delta_steps.y:
		master_steps = delta_steps.y
	elif (delta_steps.x == delta_steps.y) and (delta_steps.z!=0):
		distance = delta_units.z
		master_steps = delta_steps.z

	if master_steps!=0:
		return ((distance * 600000000.0) / float(feedrate)) / master_steps
	else:
		return ((distance * 600000000.0) / float(feedrate)) / 50

	##calculate delay between steps in microseconds.  this is sort of tricky, but not too bad.
	##the formula has been condensed to save space.  here it is in english:
	##distance / feedrate * 60000000.0 = move duration in microseconds
	##move duration / master_steps = time between steps for master axis.

def dda_move(micro_delay):###micro_delay脉冲之间的间隔时间
	gpio.digitalWrite(X_ENABLE_PIN,GPIO.HIGH) #pin25输出为高电平
	gpio.digitalWrite(Y_ENABLE_PIN,GPIO.HIGH) #pin25输出为高电平
	gpio.digitalWrite(Z_ENABLE_PIN,GPIO.HIGH) #pin25输出为高电平

	calculate_deltas()

	gpio.digitalWrite(X_DIR_PIN,direction.x) #pin25输出为高电平
	gpio.digitalWrite(Y_DIR_PIN,direction.y) #pin25输出为高电平
	gpio.digitalWrite(Z_DIR_PIN,direction.z) #pin25输出为高电平

	max_delta = max(delta_steps.x, delta_steps.y)##max_delta是需要走的最多步数，delta_steps需要走的步数
	max_delta = max(delta_steps.z, max_delta)
	
	print 'max_delta'
	print max_delta

#	x_counter = -max_delta/2
#	y_counter = -max_delta/2
#	z_counter = -max_delta/2

	x_can_step = False#########此处该为布尔型变量
	y_can_step = False
	z_can_step = False


	if micro_delay >= 16383:##micro_delay就是feedrate_micros，脉冲间隔时间，用来调节速度
		milli_delay = long(micro_delay)/ 1000
	else:
		milli_delay = 0

	x_start=0
	y_start=0
	z_start=0

	x_target = abs(target_steps.x-current_steps.x)
	y_target = abs(target_steps.y-current_steps.y)
	z_target = abs(target_steps.z-current_steps.z)

	if (x_start!=x_target) and (y_start!=y_target):
		print 'XY均有移动'

		##插补算法，k为斜率
		k = float(y_target)/float(x_target)
		#k=1
		while True:
			###x_can_step = can_step(X_MIN_PIN, X_MAX_PIN, current_steps.x, target_steps.x, direction.x)
			x_can_step = can_step(0, 0, x_start, x_target, direction.x)
			y_can_step = can_step(0, 0, y_start, y_target, direction.y)
				
			if (y_start >= float(x_start*k)) and x_can_step:
				gpio.digitalWrite(X_DIR_PIN,direction.x)
				print '插补direction.x=',direction.x
				do_step(X_STEP_PIN)
				x_start = x_start + 1

				if x_start-x_target==0:
					x_start = x_target
					y_start = y_target
				print '插补x'

			elif (y_start < float(x_start*k)) and y_can_step:
				gpio.digitalWrite(Y_DIR_PIN,direction.y)
				print '插补direction.y=',direction.y
				do_step(Y_STEP_PIN)
				y_start = y_start + 1

				if y_start-y_target==0:
					x_start = x_target
					y_start = y_target
				print '插补y'

			if milli_delay > 0:
				gpio.delay(int(milli_delay))###毫秒
			else:
				gpio.delayMicroseconds(int(micro_delay))###微秒

			if not (x_can_step or y_can_step):
				print '跳出插补'
				break


	elif (current_steps.x!=target_steps.x) and (current_steps.y==target_steps.y):
		print '仅X有移动'
		x_target=abs(target_steps.x-current_steps.x)
		x_start=0
		while True:
			gpio.digitalWrite(X_DIR_PIN,direction.x)
			do_step(X_STEP_PIN)
			x_start = x_start + 1
			if abs(x_start-x_target)<1:
					x_start = x_target
			x_can_step = can_step(0, 0, x_start, x_target, direction.x)

			if milli_delay > 0:
				gpio.delay(int(milli_delay))###毫秒
			else:
				gpio.delayMicroseconds(int(micro_delay))###微秒

			if not x_can_step:
				break


	elif (current_steps.x==target_steps.x) and (current_steps.y!=target_steps.y):
		print '仅Y有移动'
		y_target=abs(target_steps.y-current_steps.y)
		y_start=0
		while True:
			gpio.digitalWrite(Y_DIR_PIN,direction.y)
			do_step(Y_STEP_PIN)
			y_start = y_start + 1
			if abs(y_start-y_target)<1:
					y_start = y_target
			y_can_step = can_step(Y_MIN_PIN, Y_MAX_PIN, y_start, y_target, direction.y)

			if milli_delay > 0:
				gpio.delay(int(milli_delay))###毫秒
			else:
				gpio.delayMicroseconds(int(micro_delay))###微秒

			if not y_can_step:
				break


	elif current_steps.z!=target_steps.z:
		print '仅Z有移动'
		z_target=abs(target_steps.z-current_steps.z)
		z_start=0
		while True:
			gpio.digitalWrite(Z_DIR_PIN,direction.z)
			do_step(Z_STEP_PIN)
			z_start = z_start + 1
			if abs(z_start-z_target)<1:
					z_start = z_target
			z_can_step = can_step(Z_MIN_PIN, Z_MAX_PIN, z_start, z_target, direction.z)

			if milli_delay > 0:
				gpio.delay(int(milli_delay))###毫秒
			else:
				gpio.delayMicroseconds(int(micro_delay))###微秒

			if not z_can_step:
				break

	current_units.x = target_units.x
	current_units.y = target_units.y
	current_units.z = target_units.z
	print 'current_units.x'
	print current_units.x

#???????????????????????检查注意这里函数的入口参数????????????????????????###########

####def can_step(byte min_pin, byte max_pin, long current, long target, byte direction)

def can_step(min_pin,max_pin,current,target,direction):###can_step是重要的，要修改符合实际的反馈
	##stop us if we're on target
	if target == current:
		return False
	##stop us if we're at home and still going 
	elif gpio.digitalRead(min_pin) and (not direction):
		return False
	##stop us if we're at max and still going
	elif gpio.digitalRead(max_pin) and direction:
		return False

	##default to being able to step
	return True

def do_step(step_pin):######步进电机走一步
	gpio.digitalWrite(step_pin,GPIO.HIGH)
	gpio.delayMicroseconds(5)
	gpio.digitalWrite(step_pin,GPIO.LOW)###发一个脉冲
	gpio.delayMicroseconds(5)

def return_home():
	gpio.digitalWrite(X_ENABLE_PIN,GPIO.HIGH) #pin25输出为高电平
	gpio.digitalWrite(Y_ENABLE_PIN,GPIO.HIGH) #pin25输出为高电平
	gpio.digitalWrite(Z_ENABLE_PIN,GPIO.HIGH) #pin25输出为高电平

	gpio.digitalWrite(X_DIR_PIN,GPIO.HIGH)##方向
	gpio.digitalWrite(Y_DIR_PIN,GPIO.HIGH)
	gpio.digitalWrite(Z_DIR_PIN,GPIO.HIGH)

	tx=int((30000*X_STEPS_PER_MM)/FAST_XY_FEEDRATE)
	ty=int((30000*X_STEPS_PER_MM)/FAST_XY_FEEDRATE)
	tz=int((30000*Z_STEPS_PER_MM)/FAST_Z_FEEDRATE)

	while gpio.digitalRead(X_MIN_PIN):####如果限位反馈是高电平，则
		
		gpio.digitalWrite(X_STEP_PIN,GPIO.HIGH)
		gpio.delayMicroseconds(tx)
		gpio.digitalWrite(X_STEP_PIN,GPIO.LOW)###发一个脉冲
		gpio.delayMicroseconds(tx)

	while gpio.digitalRead(Y_MIN_PIN):
		
		gpio.digitalWrite(Y_STEP_PIN,GPIO.HIGH)
		gpio.delayMicroseconds(ty)
		gpio.digitalWrite(Y_STEP_PIN,GPIO.LOW)###发一个脉冲
		gpio.delayMicroseconds(ty)

	while gpio.digitalRead(Z_MIN_PIN):
		
		gpio.digitalWrite(Z_STEP_PIN,GPIO.HIGH)
		gpio.delayMicroseconds(tz)
		gpio.digitalWrite(Z_STEP_PIN,GPIO.LOW)###发一个脉冲
		gpio.delayMicroseconds(tz)

	


############主函数###################################################
f=open('gcode.txt','r')
init_steppers()

while True:
	line=f.readline()  #读取一行数据

	if line=='':
		print '退出程序'
		break

	if line.find('X')!=-1:		##找到X则执行
		fpx = getcode('X',line)
		print 'fpx=',fpx
	else:						##没找到则执行
		fpx = current_units.x
	if line.find('Y')!=-1:
		fpy = getcode('Y',line)
		print 'fpy=',fpy
	else:
		fpy = current_units.y
	if line.find('Z')!=-1:
		fpz = getcode('Z',line)
	else:
		fpz = current_units.z

	if line.find('G')==0:##是否是判断?????不知道
		code=getcode('G',line)

		#if code==90:
		#	if line.find('X'):
		#		fpx = getcode('X',line)
		#	else:
		#		fpx = current_unit.x
		#	if line.find('Y'):
		#		fpy = getcode('Y',line)
		#	else:
		#		fpy = current_unit.y
		#	if line.find('Z'):
		#		fpz = getcode('Z',line)
		#	else:
		#		fpz = current_unit.z
		#elif code==91:
		#	fpx = getcode('X',line) + current_units.x
		#	fpy = getcode('Y',line) + current_units.y
		#	fpz = getcode('Z',line) + current_units.z
		print 'start_direction.x=',direction.x,'start_direction.y=',direction.y

		if code==0:
			set_target(fpx,fpy,fpz)
			feedrate_micros = getMaxSpeed()  ##G0默认进给速度
			dda_move(feedrate_micros)

		elif code==1:   ##how fast do we move?
			set_target(fpx,fpy,fpz)
			print 'current_units.x=',current_units.x,'target_units.x=',target_units.x
			print 'current_units.y=',current_units.y,'target_units.y=',target_units.y
			print 'target_direction.x=',direction.x,'targrt_direction.y=',direction.y

			feedrate = getcode('F', line)
			print 'feedrate=',feedrate
					
			feedrate_micros = calculate_feedrate_delay(feedrate)###脉冲之间的间隔时间
			print 'feedrate_micros=',feedrate_micros

#			if feedrate > 0:
#				feedrate_micros = calculate_feedrate_delay(feedrate)
#				print feedrate_micros
#				##nope, no feedrate
#			else:
#				feedrate_micros = getMaxSpeed()
#				print feedrate_micros

			dda_move(feedrate_micros)
			print('G1AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')

		##else:
		##	if feedrate > 0:
		##		feedrate_micros = calculate_feedrate_delay(feedrate)
		##		##nope, no feedrate
		##	else:
		##		feedrate_micros = getMaxSpeed()
		##	dda_move(feedrate_micros)

		##暂停移动
		elif code==4:
			delay(int(getcode('P',line)))

		elif code==11:
			gpio.digitalWrite(X_ENABLE_PIN,GPIO.LOW) #pin25输出为高电平
			gpio.digitalWrite(Y_ENABLE_PIN,GPIO.LOW) #pin25输出为高电平
			gpio.digitalWrite(Z_ENABLE_PIN,GPIO.LOW) #pin25输出为高电平
			print '结束'

		###Inches for Units设置当前距离单位为英寸(G20)
		elif code==20:
			x_units = X_STEPS_PER_INCH
			y_units = Y_STEPS_PER_INCH
			z_units = Z_STEPS_PER_INCH
			##curve_section = CURVE_SECTION_INCHES
			calculate_deltas()
			
		###设置单位为毫米
		elif code==21:
			x_units = X_STEPS_PER_MM
			y_units = Y_STEPS_PER_MM
			z_units = Z_STEPS_PER_MM
			##curve_section = CURVE_SECTION_MM
			calculate_deltas()
			print('G21')

		##归零
		elif code==28:
			#set_target(0.0, 0.0, 0.0)
			#dda_move(getMaxSpeed())
			return_home()
			print('G28')

		elif code==90:##设置绝对坐标值
			current_units = currentunits(0.0,0.0,0.0)
			current_steps = currentsteps(0.0,0.0,0.0)
			print('G90')


        ##设置3D打印机内存中XYZE的位置值，不移动对应的步进电机
		elif code==92:
			set_position(0.0, 0.0, 0.0)


		##都没有，则执行某个响应，等待完善
		##else：


	##if :line.find('M')==0
	##	code=getcode('M',line)

	##	if 



				







