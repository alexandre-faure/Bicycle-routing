# Dossier analysis

## Description

Le dossier `analysis` centralise l'ensemble des codes pythons permettant le traitement des données d'entrée.

On prendra bien soin de donner des noms explicites aux fichiers `.py` en évitant d'y mettre trop de fonctions en les séparant par exemple dans différents fichiers selon leur utilité.

On pourra ainsi librement importer d'autres fichiers python en temps que module pour alléger les fichiers de code.

## Exemple

Pour les fichiers servant au map-matching, on crée ainsi un sous-dossier `map_matching` dans lequel seront déposés les codes pythons relatifs au map-matching.

## Formalisme pour les fonctions

Afin que les fonctions soient facilement utilisées d'une année sur l'autre et entre les membres de l'équipe projet, les fonctions doivent toutes être décrites de la façon suivante :

```python

def my_function(param1:type1, param2:type2) -> type_result:
    '''
    Description of the main aim of the function

    Input :
        - param1 (type1) : Description of the first input
        - param2 (type2) : Description of the second input
  
    Output :
        - output (type_result) : Description of the output
    '''

    # Content of the function

    return output
```
