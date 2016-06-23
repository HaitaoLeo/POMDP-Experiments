'''
****************************************************
File: discretePolicyTranslator.py
Written By: Luke Burks
May 2016
****************************************************
'''


__author__ = "Luke Burks"
__copyright__ = "Copyright 2016, Cohrint"
__license__ = "GPL"
__version__ = "0.8"
__maintainer__ = "Luke Burks"
__email__ = "clburks9@gmail.com"
__status__ = "Development"



import numpy as np
from discretePolicyTranslator import discretePolicyTranslator
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import matplotlib.animation as animation



#TODO: Make robber in random scenario actually move randomly
#TODO: Make robber acknowledge walls
#TODO: Run a RandomEmpty policy
#TODO: Set up visual simulate
#TODO: Alter the getPose functions to work on .5m grids for robots

class tagAvoidPolicyTranslator(discretePolicyTranslator):


	def __init__(self,fileName = None,hardware = False):
		if(fileName == None):
			self.alphas = self.readAlphas("fakealphas1.txt");
		else:
			self.alphas = self.readAlphas(fileName);
		if(isinstance(self.alphas[0],float)):
			self.numStates = len(self.alphas)-1;
		else:
			self.numStates = len(self.alphas[0])-1;
		self.goalX= 0;
		self.goalY = 0;
		self.hardware = hardware;


	def normalize(self,a):

		Suma = sum(a);
		for i in range(0,len(a)):
			a[i] = float(a[i])/Suma;
		return a;

	def aToxy(self,a):
		x1 = int(a/1000);
		y1 = int((a-x1*1000)/100);
		x2 = int((a-x1*1000-y1*100)/10);
		y2 = int((a-x1*1000 - y1*100 - x2*10));

		return [x1,y1,x2,y2];

	def xyToa(self,x1,y1,x2,y2):
		return x1*1000+y1*100+x2*10+y2

	def xyToa(self,c):
		return c[0]*1000+c[1]*100+c[2]*10+c[3];


	def distance(self,x1,y1,x2,y2):
		a = (x1-x2)*(x1-x2);
		b = (y1-y2)*(y1-y2);
		return sqrt(a+b);

	def fakeBelief(self,x1,y1,x2,y2):
		arr = [0]*self.numStates;
		a = self.xyToa([x1,y1,x2,y2]);
		arr[a] = 1;
		return arr;


	def printMap(self,cx,cy,rx,ry):
		map1 = "";
		for i in range(9,-1,-1):
			for j in range(0,10):
				if(j == cx and i == cy):
					map1 = map1+'O';
				elif(j==rx and i == ry):
					map1 = map1+'X';
				else:
					map1 = map1+"-";
			map1 = map1+"\n";
		print(map1);


	def getNextCopPose(self,copPose,robberPose,secondary=False):
		print('getting next cop pose...')

		if(self.hardware):
			cx = int(round(copPose[0]*2));
			cy = int(round(copPose[1]*2));
			rx = int(round(robberPose[0]*2));
			ry = int(round(robberPose[1]*2));
		else:
			cx = int(copPose[0]);
			cy = int(copPose[1]);
			rx = int(robberPose[0]);
			ry = int(robberPose[1]);

		a = [cx,cy,rx,ry];

		belief = self.fakeBelief(cx,cy,rx,ry);


		if(secondary == False):
			action = self.getAction(self.alphas,belief);
		else:
			action = self.getSecondaryAction(self.alphas,belief);



		orient = 0.0;

		#TODO: The up and down are switched. Maybe change that back?

		if(action == 0):
			destX = cx-1;
			destY = cy;
			actVerb = "Left";
			orient = 180.0;
		elif(action == 1):
			destX = cx+1;
			destY = cy;
			actVerb = "Right";
			orient = 0.0;
		elif(action == 3):
			destX = cx;
			destY = cy+1;
			actVerb = "Up";
			orient = 90.0;
		elif(action == 2):
			destX = cx;
			destY = cy-1;
			actVerb = "Down";
			orient = -90.0;
		else:
			destX = cx;
			destY = cy;
			actVerb = "Wait";


		if(self.hardware):
			return [float(destX)/2,float(destY)/2,0.0,orient];
		else:
			return [destX,destY,0,orient];


	def getNextRobberPose(self,copPose,robberPose):
		print('getting next robber pose...')
		if(self.hardware):
			cx = int(round(copPose[0]*2));
			cy = int(round(copPose[1]*2));
			rx = int(round(robberPose[0]*2));
			ry = int(round(robberPose[1]*2)); 
		else:
			cx = int(copPose[0]);
			cy = int(copPose[1]);
			rx = int(robberPose[0]);
			ry = int(robberPose[1]);

		weights = [];
		dests = [];
		holds = [];

		if(cx-rx <= 0 and rx < 9):
			dests += [[rx+1,ry,1]];
			weights += [.4];
			holds += [1];
		elif(cx-rx>=0 and rx > 0):
			dests += [[rx-1,ry,0]]
			weights += [.4];
			holds +=[0];
		if(cy-ry <= 0 and ry < 9):
			dests += [[rx,ry+1,2]];
			weights += [.4];
			holds+=[2];
		elif(cy-ry >= 0 and ry > 0):
			dests += [[rx,ry-1,3]];
			weights += [.4];
			holds +=[3]

		dests += [[rx,ry,4]];
		weights += [.2];
		holds += [4];


		weights = self.normalize(weights);

		tmp = np.random.choice(holds,p=weights);
		dest = dests[holds.index(tmp)];
		orient = 0.0;
		if(dest[2] == 0):
			orient = 180.0;
		elif(dest[2] == 1):
			orient == 0.0;
		elif(dest[2] == 2):
			orient = 90.0;
		elif(dest[2] == 3):
			orient = -90.0;
		else:
			orient = 0.0;

		if(self.hardware):
			return [float(dest[0])/2,float(dest[1])/2,0.0,orient];
		else:
			return [dest[0],dest[1],0,orient];


	def simulate(self):
		cx = 1;
		cy = 1;
		rx = 5;
		ry = 5;

		self.copsx = [];
		self.copsy = [];
		self.robsx = [];
		self.robsy = [];


		action = 0;

		flag = False;
		count = 0;
		while(cx != rx or cy != ry):
			a = self.getNextRobberPose([cx,cy],[rx,ry]);
			b = self.getNextCopPose([cx,cy],[rx,ry]);

			count+=1;

			rx = a[0];
			ry = a[1];
			cx = b[0];
			cy = b[1];

			if(cx < 0 or cy < 0 or ry < 0 or rx < 0 or cx > 9 or cy > 9 or rx > 9 or ry > 9):
				print("Error: Robot out of bounds");
				flag = True;
				break;

			self.copsx += [cx];
			self.copsy += [cy];
			self.robsx += [rx];
			self.robsy += [ry];

			print("Cop position: ");
			print(cx,cy);
			print("Robber position: ");
			print(rx,ry);
			self.printMap(cx,cy,rx,ry);
			print("");
			#plt.scatter([cx,rx],[cy,ry]);
			#plt.axis([-.5,9.5,-.5,9.5])
			#plt.show();


		print("Congratulations!! The cop caught the robber in: " + str(count) + " moves.")


'''
def init():
	line.set_data([], [])
	return line


def animate(i):
	global copsx;
	global copsy;
	global robsx;
	global robsy;

	#x = cops[0][0];
	#y = cops[0][1];
	if(len(copsx) > 1):
		line.set_data(copsx,copsy)

		copsx = copsx[1:];
		copsy = copsy[1:];
		return line,
'''



if __name__ == "__main__":

	#file = "../policies/tagAvoidEmpty100.txt";
	file = "../policies/tagAvoidWalls100.txt";
	#file = "../policies/tagRandomWalls100.txt";
	t = tagAvoidPolicyTranslator(file);
	t.simulate()


	copsx = t.copsx;
	copsy = t.copsy;
	robsx = t.robsx;
	robsy = t.robsy;




	fig = plt.figure()
	ax = plt.axes(xlim=(-.5, 9.5), ylim=(-.5, 9.5))
	line, = ax.plot([], [], lw=2)




	#anim = animation.FuncAnimation(fig, animate, init_func=init,frames=100, interval=500,save_count = 100, blit=False)
	#plt.show();
