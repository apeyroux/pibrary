import json
import sys

from amazon.api import AmazonAPI
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Livre(Base):
    __tablename__ = 'livres'

    id = Column(Integer, primary_key=True)
    isbn = Column(String)
    titre = Column(String)
    auteur = Column(String)
    prix = Column(Float)

if __name__ == "__main__":

    with open('aws.id.json', 'r') as cfg:
        config = json.loads(cfg.read())

    db = create_engine('sqlite:///livres.db')
    Base.metadata.create_all(db)
    Session = sessionmaker(bind=db)
    session = Session()

    amazon = AmazonAPI(config['AMAZON_ACCESS_KEY'], config['AMAZON_SECRET_KEY'], config['AMAZON_ASSOC_TAG'], region="FR")
    amout = 0
    print("Entrer le livre à ajouter (ISBN ou champ libre): ")
    while True:
        try:
            recherche = sys.stdin.readline()
            products = amazon.search(Keywords=recherche.strip(), SearchIndex='All')
            for _, product in enumerate(products):
                if product.price_and_currency[0] :
                    prix = product.price_and_currency[0]
                else:
                    prix = 0
                print("{} de {} au prix de {}€".format(product.title, ', '.join(product.authors), prix))
                sys.stdout.write("Ajouter ?: [Y/n]")
                reponse = input().lower()
                if reponse == 'n':
                    print("Insertion annulée.")
                elif reponse == 'y' or reponse == '':
                    if not session.query(Livre).filter_by(isbn=product.isbn).first() :
                        l = Livre(isbn=product.isbn, titre=product.title, auteur=', '.join(product.authors), prix=prix)
                        session.add(l)
                        session.commit()
                        amout = amout + prix
                        print("Dépense de {}€".format(amout))
                    else:
                        print("Déjà en db")
                else:
                    print("Je ne comprend pas la réponse.")
        except Exception as ex:
            print(ex)

    atexit.register(lambda : print("Exit"))