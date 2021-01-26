#!/usr/bin/python

import rospy
#from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from std_msgs.msg import String
from std_msgs.msg import Float32

import math
import numpy as np
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
import math
import time

class LegL():
	def __init__(self):
		self.rospy = rospy
		self.rospy.init_node('formationControl', anonymous = True)
		self.rospy.loginfo("Starting Formation Control")
		self.initParameters()
		self.initSubscribers()
		self.initPublishers()
		self.initVariables()
		self.mainControl()

	def initParameters(self):
		self.velTopic = self.rospy.get_param("~vel_topic","/turtle1/cmd_vel")
		self.legLaserTopic = self.rospy.get_param("~legLaser_topic","/distance")
		self.posHeadTopic = self.rospy.get_param("pH_topic", "/pos_head_topic")
		self.controlRate = self.rospy.get_param("~control_rate", 100)
		self.dist_Thresh = self.rospy.get_param("~dist_Thresh", 0.5)

		return

	def initPublishers(self):
		self.pubVel = self.rospy.Publisher(self.velTopic, Twist, queue_size = 10)

		return

	def initSubscribers(self):
		self.distanceMean = self.rospy.Subscriber(self.legLaserTopic, Float32, self.callbackPos)
		self.subPosHead = self.rospy.Subscriber(self.posHeadTopic, String, self.callbackPosHead)

		return

	def initVariables(self):
		self.rate = self.rospy.Rate(self.controlRate)
		self.angle_min = 0
		self.angle_max = 0
		self.scan_time = 0
		self.ranges = 0
		self.angle_increment = 0
		self.time_increment = 0
		self.range_min = 0
		self.range_max = 0
		self.change = False
		self.font = {'family': 'serif',
					'color':  'darkred',
					'weight': 'normal',
					'size': 9,
					}
		self.amostras = [[0,0],[0,0]]
		self.distAnt = 0
		self.distAtual = 0
		self.VelX = [0,0]
		self.veloc = [0]
		self.vel = []
		self.applied = []
		self.mediaG = []
		self.mediaX = 0.0
		self.mediaY = 0.0
		self.k = 0.0
		self.posicaoX1 = 0.0
		self.posicaoX2 = 0.0
		self.posicaoY1 = 0.0
		self.posicaoY2 = 0.0
		"""----------------------------------  """

		#vetor com os parametros da formacao.
		#posicao 1 - a distancia entre os robos
		self.qDes = np.array([0.7, 0, 0, 0])

		""" ---------------------------------- """

		#ganhos - Responsavel pelo tempo de resposta
		self.L = 0.8*np.eye(4)
		self.kp = 0.8*np.eye(4)

		""" ---------------------------------- """
		self.qTil = 0
		self.qRefPonto = 0
		self.data = ["Start"]
		self.angle = 0.0
		self.action = 0
		self.velAngular = 0
		self.ang_count = 0

		return
	def forma(self):
		self.posicaoX2 = self.mediaX

		self.q = np.array([self.posicaoX2/2, 0, (math.atan2(((self.posicaoY2-self.posicaoY1)),
				(self.posicaoX2-self.posicaoX1))), (np.sqrt(np.power(self.posicaoY2-self.posicaoY1,2)+np.power(self.posicaoX2-self.posicaoX1,2)))])
		self.qTil = self.qDes - self.q

		self.qRefPonto = np.matmul(self.L,np.tanh(np.matmul(np.matmul(np.linalg.inv(self.L),self.kp),self.qTil)))

		self.jacob = np.array([[1, 0, self.q[3]*math.sin(self.q[2])/2, -math.cos(self.q[2])/2],
							[0, 1, -self.q[3]*math.cos(self.q[2])/2, -math.sin(self.q[2])/2],
							[1, 0, -self.q[3]*math.sin(self.q[2])/2, math.cos(self.q[2])/2],
							[0, 1, self.q[3]*math.cos(self.q[2])/2, math.sin(self.q[2])/2]])

		self.xRefPonto = np.matmul(self.jacob, self.qRefPonto)

		self.K = np.array([[math.cos(0), math.sin(0), 0, 0],
							[(-math.sin(0)/.2), (math.cos(0)/.2), 0, 0],
							[0, 0, math.cos(0), math.sin(0)],
							[0, 0, (-math.sin(0)/.2), (math.cos(0)/.2)]])

		self.v = np.matmul(self.K,self.xRefPonto)


		if self.v[2] > 0:
			self.VelX[1] = self.v[2]
		else:
			if self.posicaoX2 > self.qDes[0]:
				self.VelX[1] = 0.0
			else:
				self.VelX[1] = -self.v[2]

	def makeVelMsg(self):
		msg = Twist()

		if(self.mediaX < self.dist_Thresh):
			msg.angular.z = self.velAngular
			msg.linear.x = self.VelX[1]
			self.pubVel.publish(msg)
		else:
			msg.linear.x = 0.0
			msg.angular.z = 0.0
			self.pubVel.publish(msg)
		return
	
	def callbackPos(self, msg):

		self.mediaX = msg.data
		self.change = True
		


	#gera o controle das velocidades - Angular em exponencial
	def getControl(self,angle=0,action=0):
		if (action == -1): # Turn Left
			self.ang_count +=0.015
			self.velAngular = 3.5*(math.exp(self.ang_count))/10
		elif (action == 1): # Turn Right
			self.ang_count +=0.015
			self.velAngular = 3.5*(-math.exp(self.ang_count))/10
		else: # Go Forward
			self.ang_count = 0
			self.velAngular = 0
		return
	""" ---------------------------------- """
	def callbackPosHead(self, msg):
		self.data.append(msg.data)


		"""
		Atraso do tempo de resposta na mudanca da velocidade angular para zero
		Dependendo da velocidade de processamento o numero deve ser mudado
		Na rasp o valor de 20 ficou bom, mas no computador teve que ser > 100

		"""
		if len(self.data) > 100 and msg.data == 'Start':
			if all(x == self.data[-1] for x in self.data[-20:-1]):
				self.data = []
				self.data.append('Start')
				self.angle = 0.0
				self.action = 0
		
	""" ---------------------------------- """

	def mainControl(self):
		plt.ion()
		while not self.rospy.is_shutdown():
			self.msg = Float32()
			# Se o Laser nao identifica, ele retorna 0
			if self.change:	
				# Se o Laser identificou alguma coisa	
				if self.mediaX != 0:
					# velocidade linear 
					self.forma()
					# Velocidade angular
					if self.data[-1] != "Start":
						self.angle,self.action = self.data[-1].split(":")
						self.angle = float(self.angle)
						self.action = int(self.action)

					self.getControl(self.angle, self.action)
					self.amostras[0] = self.amostras[1]
				
				else:
					self.VelX[1] = 0
					self.velAngular = 0
					self.action = 0

				self.makeVelMsg()


				self.change = False
			
			self.rate.sleep()

if __name__ == '__main__':
	try:
		legL = LegL()
	except rospy.ROSInterruptException:
		pass
