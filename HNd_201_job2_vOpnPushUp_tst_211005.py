#!/usr/bin/env python3
# -*- coding: utf-8 -*-"
""" HNGN001 Created on Tue Jun 11 08:34:11 2019
(two days before 190613) (1month before 190711)"""

s2="""
{210909}
[Title]
Valve Open and Push up the water/molten_salt to upper_overflow_tank
"""

s2="""
{210916B}
ピコテクノロジーをつかまない。
「圧力計測」だけで動かすバージョンを用意する
（ヒータ、クーラー、ではピコテクノロジ＝温度計測をつかうので）

{210916}
（温度計測）
トップタンクの温度をみて、トップタンクに到達したかを
判断する


{210909}
(0)（考え方）複数のプロセスを起動するスクリプトをPythonで起動させる。
(1)JOB1, ドレンタンク加熱を独立のプロセスで起動する
(2)JOB2, 水を上部タンクに上げる。（ピコテクノロジーの温度計測で）バルブを開いて、上部まで上がったことを確認する。
　　　1)圧力計測の大気圧を（できれば）しらべて、ゼロ点調節をする。
(3)JOB3, 自然循環（fast scanの温度計測で）垂直ヒータの電源を入れ、しばらくしてクーラーの電源を入れ、温度雑音計測する。
　　　1)fast_scanの開始
　　　2)垂直ヒータの電源
　　　3)ブロウアーの電源

"""

s2="""
{210908}
バルブの開時間を
インプットで与えたい（Ajiさんの要請）
UI（ユーザインターフェィス）が要求されている。
＞＞
開発が一段落して、モードが、きまったら
パラメータをユーザインターフェース、
＞＞
Prof. Indra Wahyudin Fatonah
広島大学を卒業した
Telcom University = (like UEC)

"""
s2="""
{210908}
運転と計測とはRasPiを別にしたほうがよい。運転のデバッグ中に、計測が止まってしまう。
安全なシャットダウンのため RasPiを一つ、複製（本体RasPiのバックアップ）としてもつべき。
"""
s2="""
{210903}
まずはバルブを開けてループの中に入れて圧力を上げるのと
温度を見るの道を繰り返しやっていこうと思う。
＞＞
変に自動化しない方が安全性はあると思う。圧力は目で見ながら動かしたほうが安全だと思う。
（重要）計測値の信頼性がいまいちなので計測値を信頼して（プログラム自動で）何か動かすとえらいことになる（重要）
"""

s2="""
{210827}
HNGM184b_210719.py に picotech の温度計測があるので、これでパイプの温度をとる
"""

s2="""
{HNGN186c_210721.py}
安全に、吹き出さないようにアルゴン・ボンベの圧力を使って溶融塩を上部タンクまで上げる。
（ボンベの圧力は、レギュレータを使っても5気圧までしか下がらないので、なかなか難しい）
＞＞
(プランA) {210720}
（積分型のやり方）
ループシステムの手前に補助タンクを1つ設けて容積を準備し、
そのガス圧力で水位を上げる。
アルゴン・ボンベとループシステムの間を切り離して
補助タンクの圧力だけで駆動するのが安全だと思う。

（プランB）
（微分型のやり方）
開放弁を開けてガスを逃がすようにしておいてから、
ボンベ側の電磁弁（レギュレーターから出ている）を開ける。
2つの弁の開け閉めのタイミングを合わせながら圧力を調整する
（この方式をとる前に、まずガスがたまる自由体積がどれくらいの大きさか推定したほうがいい）

（プランC） 
圧力は５気圧まで測れるのだから、
ボンベ側の弁を短時間開けて
時間と圧力上昇から（VV=自由体積／流れの速さ）に相当する量Wを計測する。
圧力計の時間変化、圧力が下がるトレンドと、水位の上昇を観察する。
逃がし弁の方をいつでも開けるようにしておく。
{210720}
動作する、方程式、をつかう、良い例題になると思う。
微分で制御する
状態量（自由体積、流れ速度、圧力（ガスのポテンシャル））をモデルから推定し、
それをもとに次のステップを決める。
"""

s3="""
HNGN186の結果（パルス1回の応答）を受けて、
3秒以上開くと、上部タンクまで上がってしまうように思われる。
短いパルスを多数回出してみる。それにより、
圧力ショックを与えないようにし、すこしづつ液位を上げることができる
"""




import time
import sys
import serial
import numpy as np
import RPi.GPIO as GPIO
import datetime

#// 時刻、時間のセットアップ
# date time is here, second of unix time of time.time() is in the code. 
def time_stamp():
  dt_now = datetime.datetime.now()
  time_stamp_out=dt_now.strftime('%Y-%m-%d %H:%M:%S')
  return time_stamp_out

timetime0=time.time() #unix-time

#// データを記録する。圧力の変化の保存の前設定
# data-recording, to set preparation
file1 = "HN_pressure_and_valve-211003A.txt"
f=open(file1,"a+")
f.write("pressure & temperature at each cycle of valve_on/off  \n") 


#// SSR/バルブのカチカチ・・Lチカ(GPIOの3, 5)

GPIO.cleanup()

SSR1_GPIO_n = 2   #valve_1 4charge
SSR2_GPIO_n = 3   #valve_2 4release
SSR3_GPIO_n = 4   #heating drain_tank
SSR4_GPIO_n = 17  #heating_pip2
SSR5_GPIO_n = 27  #blower_cooling

GPIO.setmode(GPIO.BCM)
GPIO.setup(SSR1_GPIO_n, GPIO.OUT)
GPIO.setup(SSR2_GPIO_n, GPIO.OUT)
GPIO.setup(SSR3_GPIO_n, GPIO.OUT)
GPIO.setup(SSR4_GPIO_n, GPIO.OUT)
GPIO.setup(SSR5_GPIO_n, GPIO.OUT)

"""
{210827}
（重要）（重要）（重要）
ボンベから、システムの間に溜まっている、ガスを逃した。
データとして4気圧から、１気圧に戻すまで、60sec、では足りなかった。
（溜まっている体積が不明）
それをやらないと、大きな圧力がかかってしまう。
"""

"""
{210901}
はじめに、ドレンタンクの温度を上げる
５分くらいで十分だと思う
（温度が高くなったら＝たとえば 45C を超えていたら、SSRでのヒーター・スイッチが入らないようにしたい）
＞＞
"""


def SSR1_valve_4charge(Open_time_sec):
	# Ar supply valve
	ots=Open_time_sec
	GPIO.output(SSR1_GPIO_n, True)
	time.sleep(ots)
	GPIO.output(SSR1_GPIO_n, False)
	return

def SSR2_valve_4release(Open_time_sec):
	# relief valve
	ots=Open_time_sec
	GPIO.output(SSR2_GPIO_n, True)
	time.sleep(ots)
	GPIO.output(SSR2_GPIO_n, False)
	return

def SSR3_bottom_tank_heating(On_time_sec):
	# relief valve
	ots=On_time_sec
	GPIO.output(SSR3_GPIO_n, True)
	time.sleep(ots)
	GPIO.output(SSR3_GPIO_n, False)
	return

def SSR4_heating_pipe(On_time_sec):
	# relief valve
	ots=On_time_sec
	GPIO.output(SSR4_GPIO_n, True)
	time.sleep(ots)
	GPIO.output(SSR4_GPIO_n, False)
	return

def SSR5_cooling_blower(On_time_sec):
	# relief valve
	ots=On_time_sec
	GPIO.output(SSR5_GPIO_n, True)
	time.sleep(ots)
	GPIO.output(SSR5_GPIO_n, False)
	return

def Interupt_shutdown():
	#{210908}
	""" All actuater_valve and heater and cooler shut down =close="""
	GPIO.output(SSR1_GPIO_n, False)
	GPIO.output(SSR2_GPIO_n, False)
	GPIO.output(SSR3_GPIO_n, False)
	GPIO.output(SSR4_GPIO_n, False)
	GPIO.output(SSR5_GPIO_n, False)
	return

def All_shutdown():
	#{210908}
	""" All actuater_valve shut down =close="""
	GPIO.output(SSR1_GPIO_n, False)
	GPIO.output(SSR2_GPIO_n, False)
	GPIO.output(SSR3_GPIO_n, False)
	GPIO.output(SSR4_GPIO_n, False)
	GPIO.output(SSR5_GPIO_n, False)
	return

def drain(t_sec):
	#ガスを放出して、水を下部タンクに落とす
	# {210903}
	#圧力解放弁
	print("Release_Valve_Open")
	time_sec_0=time.time()
	# t_sec=valve_opening_time_sec=60*2 #60*n sec opening
	SSR2_valve_4release(t_sec)
	dtime_sec=time.time() - time_sec_0
	print("Release_Valve_Close", "dtime_sec=",f"""{dtime_sec:.3F}""")


#// もろもろのはじまり

#drain(600) #need long time to drain the gas （高さを cmで、制御するなら）
All_shutdown()
#sys.exit()



"""
{210909} taking out
# SSR3 ドレンタンクのヒータを入れて温度を上げる
if Tc1 <0: 
	t=initial_heating_time= (60*5)  # (60sec)*(minutes)
	SSR3_bottom_tank_heating(t)
"""

# record pressure change
#// 圧力の変化をファイルに保存する {210716}
#// プレッシャーゲージのデータを読む
# P_gauge data reading set-up from Arduino 
ser = serial.Serial('/dev/ttyACM0', 9600)




P_drain_cm=0 #global control critical pressure


"""
SSR4_heating_pipe(1000) #同時にできない
SSR5_cooling_blower(1000)
GPIO.output(SSR5_GPIO_n, True)
"""


#OBS!! drain procedure 
#GPIO.output(SSR2_GPIO_n, True)#drain


def get_gas_p():
	"""
	line = ser.readline()、で圧力ゲージを読んでいる
	平均をとって雑音を減らしたいが、
	平均は、Pデータを読んでから、この外で行う。
	＞＞
	温度をみて（トップタンクに届いたか）判断するのは、そのあと。
	"""

	"""
	{210916}
	（方針）
	このプログラム（サブプロセスと言ってよいだろうか・・・）では
	常時、圧力をみて判断し、変化を記録する。そのために
	圧力測定を、関数にして、呼び出すようにする　（＜＝＝これなら分かりやすいだろう）
	＞＞
	（数値を見つける、エンジニアリングかな・・・）
	圧力が上がるのをみて、どの程度の値か＝経験値を、取得する。
	"""

	#pgm=pressure gauge measurement
	line = ser.readline()
	# print("ser.readline line=",line)
	pressures=(line.decode('utf-8')).split(',')
	# print("a.split=",pressures)
	P1=data1=float(pressures[0])
	P2=data2=float(pressures[1])
	#print("pressures P1,P2=", P1, P2)
	#
	#
	vvvvvvv1=5.0*(P1/1023) # 10bit ADC of Arduino
	vvvvvvv2=5.0*(P2/1023) # 10bit ADC of Arduino
	vvv_p0=volt_of_zero_pressure=3.0 #(unit is volt)
	# OBS! ゼロ設定　肝の一つ　OBS!
	vvv_p01= 3.210  #春日 {2100908}の天気（低気圧）のゼロ設定
	vvv_p02= 3.177  #ちょっと、雑音が多すぎるなあ・・・
	#print("vvvvvvv1,vvvvvvv2=",vvvvvvv1,vvvvvvv2)
	pMPa1=0.1*(vvvvvvv1-vvv_p01)/(3.0)   #MPS-C35R（Range: -0.1MPa to +0.1MPa）	 
	pMPa2=0.1*(vvvvvvv2-vvv_p02)/(3.0)   

	#MPS-C35R（Range: -0.1MPa to +0.1MPa）	 
	head_cm_1=pMPa1*(10000/0.98)  #head_of_water(cm), 1MPa=100m=10000cm
	head_cm_2=pMPa2*(10000/0.98)  #head_of_water(cm), 1MPa=100m=10000cm
	
	#print("head_cm_1,head_cm_2=",head_cm_1,head_cm_2)
	time.sleep(0.2)
	return head_cm_1,head_cm_2

# {210916}
# 水頭２＝150cmでほぼサチる。
# 圧力を維持するプログラムを開発する
# 50*10以内にもちあがったとおもう。
# 水頭2 161cm=> 172 コールドで

ncycle=60*60  # 60sec*(n minutes)  (10sec)*n   60*30/10
for i in range(ncycle):
	try:
		""" ここで ガス圧力の計測を、callする """
		sum1=0
		sum2=0
		head_cm_1=0
		head_cm_2=0
		n=10 #平均を取ってみる
		for j in range(n): #圧力に雑音が乗っているので、平均を取るためにループを用意してある
			a=get_gas_p()
			print(a)
			s1=f""" head_cm fr get_gas_p= {a[0]}, {a[1]} """
			head_cm_1=a[0]
			head_cm_2=a[1]
			sum1+=head_cm_1
			sum2+=head_cm_2

			#// ファイルへの書き出し 

			""", dt_open={dtime_sec:.2F}, dt_open={dtime_sec:.2F},"""

			s11=""" time_stamp,        UNIX-time(sec)      head(cm)"""
			s12=f""" {time_stamp()}, unix_time={time.time()-timetime0:.2F} , 水頭1={head_cm_1:.1F},   水頭2={head_cm_2:.1F} """
			s11f=""" time_stamp,        UNIX-time(sec,     head(cm),  d_head(cm)\n"""
			s12f=f""" {time_stamp()}, unix_time={time.time()-timetime0:.2F} , 水頭1={head_cm_1:.1F},   水頭2={head_cm_2:.1F} \n"""
			if i==0: print(s11) 
			#print(s12)
			if i==0: f.write(s11f)
			f.write(s12f)

		head_cm_1_av=sum1/(n+1)
		head_cm_2_av=sum2/(n+1)

		iss=interval_sec=1.0
		time.sleep(iss)
		# end of pressure measurement

		""" ここで、バルブを少し開けて（少しづつ）ガスを持ち上げる"""
		thc=target_head_cm=150 #130,  150=>170 {210930}   100cmよりも低かったら、継続してガスをchargeする
		thc2=thc2_bomb=200  #180   drain tank pressure (charge tank) 
		#>>
		s13=f"""thc(cm), thc2=, head_cm_1_av,head_cm_2_av=", {thc},{thc2}, {head_cm_1_av},{head_cm_2_av}"""
		s13f=f"""thc(cm)=, thc2=, head_cm_1_av,head_cm_2_av=", {thc},{thc2}, {head_cm_1_av},{head_cm_2_av} \n"""
		print(s13)
		f.write(s13f)
		if head_cm_1_av < thc and head_cm_2_av < thc2:  # no1 is drain tank {211001}
			print("*** OBS!! *** head_cm__av,head_cm_2_av=",head_cm_1_av,head_cm_2_av)
			try:
				s0=f""" thc=target_head_cm= {thc} """
				if i==0: f.write(s0) 
				#// アルゴン供給弁を開けて圧力の上昇を見る
				#// Ar_supply valve 
				# needle valve open 
				print("Charge_Valve_Open")
				time_sec_0=time.time()
				t=valve_opening_time_sec=1.0  #opening time of charging 
				SSR1_valve_4charge(t)
				dtime_sec=time.time() - time_sec_0
				print("Charge_Valve_Close", "dtime_sec=",f"""{dtime_sec:.3F}""")
			except KeyboardInterrupt:
				All_shutdown()
				print ('\n Interupt_shutdown() \n exiting pressurizing)')
				sys.exit()


	except KeyboardInterrupt:
		Interupt_shutdown()
		print ('\n Interupt_shutdown() \n exiting recording of pressure and temperature change')
		s2="""
		ここで、ガスを逃がすかどうか、オペレータ（開発者）に聞くと良いと思う。
		"""
		print (s2)
		sys.exit()
		#break

#ガスを放出する
"""
なにか、不都合が起きたら、ガスを抜いてドレンさせる。それを第一義にオペレーティング・システムを構築する。
（ループ運転用の言語があってもよいのではないか？）
（循環ループにも、CP/Mに相当する、OS、があっても良いのではないか？）
＞＞
機能としてつけること
(1)オーバーフロータンクに、到達したかどうかを、確認できること

"""
#ガスを逃がすときに以下を使う
#drain()

#アウトプット記録ファイルのクローズ
f.close()

GPIO.cleanup()
