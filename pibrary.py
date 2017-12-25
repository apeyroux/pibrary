import json
import sys
import click

from amazon.api import AmazonAPI
from sqlalchemy import create_engine, Column, Integer, String, Float
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

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--depense',
              is_flag=True,
              help='Montant tt des dépenses de livres.')
@click.option('--ls',
              is_flag=True,
              help='Liste des livres.')
@click.option('--repl',
              is_flag=True,
              help='repl pour ajouter des livres')
def main(depense, ls, repl):

    with open('aws.id.json', 'r') as cfg:
        config = json.loads(cfg.read())

    db = create_engine('sqlite:///livres.db')
    Base.metadata.create_all(db)
    Session = sessionmaker(bind=db)
    session = Session()

    amazon = AmazonAPI(config['AMAZON_ACCESS_KEY'],
                       config['AMAZON_SECRET_KEY'],
                       config['AMAZON_ASSOC_TAG'],
                       region="FR",
                       )

    if ls:
        click.echo_via_pager('\n'.join([livre.titre for livre in session.query(Livre).all()]))

    if depense:
        somme = 0
        for livre in session.query(Livre).all():
            somme = somme + livre.prix
        click.secho("Montant de la librairie : {0:.2f}€".format(somme),
                               blink=True,
                               bold=True,
                               bg="red",
                               fg="white")


    if repl:
        while True:
            click.secho("Entrer le livre à ajouter (ISBN ou champ libre):", fg="blue")
            try:
                recherche = sys.stdin.readline()
                products = amazon.search(
                    Keywords=recherche.strip(), SearchIndex='All')
                for _, product in enumerate(products):
                    if product.price_and_currency[0]:
                        prix = product.price_and_currency[0]
                    else:
                        prix = 0
                    if(click.confirm("Voulez-vous ajouter \"{}\" à la librairie ?".format(product.title), default=True)):
                        if not session.query(Livre).filter_by(isbn=product.isbn).first():
                            l = Livre(isbn=product.isbn,
                                      titre=product.title, auteur=', '.join(
                                          product.authors),
                                      prix=prix,
                                      )
                            session.add(l)
                            session.commit()
                            click.secho("Ajout de {}".format(l.titre), fg="green")
                        else:
                            click.secho("{} est déjà en db".format(product.title), fg="red")
            except Exception as ex:
                click.secho("{}".format(ex), fg="red", bg="white")


if __name__ == "__main__":
    main()
