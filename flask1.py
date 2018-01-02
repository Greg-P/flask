from flask import Flask, request, jsonify 
import json 
import recastai
import sqlite3
#import os
#import config

app = Flask(__name__) 
port = '5000' 
dbflask=sqlite3.connect('../DJANGOchat/db.sqlite3', check_same_thread = False)
cursorflask = dbflask.cursor()

@app.route('/', methods=['POST']) 
def index(): 
	
	mes_donnees = json.loads(request.get_data())
	ma_conversation = mes_donnees['conversation']['id']
	mon_intent = mes_donnees['nlp']['intents'][0]['slug']
	print(ma_conversation, mon_intent)
	
	contenu = ''
	cursorflask.execute('''SELECT compteclient FROM Accueil_lesclient WHERE channelclient LIKE ?''', ('%'+ma_conversation+'%',))
	rows = cursorflask.fetchall()
	if len(rows) == 1:
		if mon_intent == "solde-compte":
			cursorflask.execute('''SELECT montantcompte FROM Accueil_lesposition WHERE compteposition = ?''', ( rows[0][0],))
			rowsbis = cursorflask.fetchall()
			if len(rowsbis) == 1:
				contenu = 'Le solde de votre compte courant est '+ "{0:.2f}".format(rowsbis[0][0]) + ' euros'
			else:
				contenu = 'je ne comprends pas la question '
		elif mon_intent == "operations":
			monnombre = 1
			try:
				if 'number' in mes_donnees['nlp']['entities']:
					monnombre = int(mes_donnees['nlp']['entities']['number'][0]['raw'])
			except:
				pass
			if monnombre == 1:
				contenu = 'Votre opération est '
			else:
				contenu = 'Vos opérations sont '
			print("nombre", monnombre)
			if 'debit' in mes_donnees['nlp']['entities']:
				cursorflask.execute('''SELECT dateoperation, montantoperation, libelleoperation, typeoperation 
				FROM Accueil_LesOperationscompte WHERE numerocompte = ? AND montantoperation < 0 ORDER BY dateoperation DESC LIMIT ?''', ( rows[0][0], monnombre,))
			elif 'credit' in mes_donnees['nlp']['entities']:
				cursorflask.execute('''SELECT dateoperation, montantoperation, libelleoperation, typeoperation 
				FROM Accueil_LesOperationscompte WHERE numerocompte = ? AND montantoperation > 0 ORDER BY dateoperation DESC LIMIT ?''', ( rows[0][0], monnombre,))
			else:
				cursorflask.execute('''SELECT dateoperation, montantoperation, libelleoperation, typeoperation 
				FROM Accueil_LesOperationscompte WHERE numerocompte = ? ORDER BY dateoperation DESC LIMIT ?''', ( rows[0][0], monnombre,))
			rowsbis = cursorflask.fetchall()
			if len(rowsbis) >= 1:
				for rowbis in rowsbis:
					contenu += rowbis[0] + '  ' + "{0:.2f}".format(rowbis[1]) + '  ' + rowbis[2].rstrip() + '  ' + rowbis[3].rstrip() + ' // '
			else:
				contenu = 'Aucune opération'
			
			# print(mes_donnees)

	else:
		contenu = 'merci de vous connecter'
			

	return jsonify( 
		status=200, 
		replies=[{ 
			'type': 'text', 
			'content': contenu, 
		}], 
		conversation={ 
			'memory': { 'key': 'value' } 
		} 
	) 
 
 
 
 
@app.route('/errors', methods=['POST']) 
def errors(): 
  print(json.loads(request.get_data())) 
  return jsonify(status=200) 

if __name__ == "__main__":
	app.run()
