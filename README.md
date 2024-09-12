# keskustelusovellus
Projekti Helsingin yliopiston TKT20019-kurssille

Sovelluksessa käyttäjä voi:
- [X] Rekisteröidä käyttäjän ja kirjautua sisään
- [ ] Luoda uuden alueen (vrt. subreddit)
- [ ] Luoda keskusteluketjun tietylle alueelle
- [ ] Lähettää viestejä keskusteluketjuun
- [ ] Luoda yksityisen keskusteluketjun ja määrittää käyttäjät, joilla on pääsy tähän ketjuun
- [ ] Seurata valitsemiaan ketjuja ja nähdä ne ensimmäisenä etusivulla
- [ ] Poistaa ja muokata viestejä

## Kehitysympäristö

Asenna riippuvuudet komennolla `pip install -r ./requirements.txt`.

Käynnistä tietokanta komennolla `docker compose -f docker-compose.dev.yml up`

Luo tietokantaskeema komennolla `docker exec -i keskustelusovellus-database-1 psql -U postgres < schema.sql`

Luo `.env` tiedosto kopioimalla `.env.example` ja uudelleennimeämällä se. Jos et aja tietokantaa Dockerissa, muista muuttaa `DATABASE_URL` ympäristömuuttujan arvo.

Käynnistä sovellus komennolla `flask run`