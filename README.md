# Preuzimanje, setup & pokretanje projekta/programa

### Postavljanje venv virtualne mašine

Ovo je postavljanje za specificiranu verziju Pythona
```
py -3.14 -m venv venv
```

Ovo je postavljanje za verziju Pythona koji je skinut na PC

```
py -m venv venv
```

Za prekidanje rada virtualne mašine dovoljno je upisivanje komande '$ deactivate'


### Skidanje svih potrebnih stvari (requirements)

```
pip install -r requirements.txt
```

Za prikaz svih trenutnih paketa koji su aktivni u virtualnom okruženju da se zapišu u 'requirements.txt' koristimo ovu naredbu:

```
pip freeze > requirements.txt
```


### Pokretanje virtualnig okruženja venv

```
venv\Scripts\activate
```


### Pokretanje aplikacije

```
streamlit run main.py
```