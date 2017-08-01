# Infoskjerm-værvarsel

Webside for bruk på https://infoskjerm.smint.no for å vise værinformasjon, med
hjelp av [yr.no](https://yr.no).

## Installasjon

1. Installer følgende pakker:

    * python3-dev

3. [Bruk virtuelt miljø (virtualenv)!](https://iamzed.com/2009/05/07/a-primer-on-virtualenv/)

   ```bash
   virtualenv -p python3.4 venv
   . venv/bin/activate
   ```

4. Installer avhengigheter:
        
   <code>pip install -r requirements.txt</code>

### Deploye til Apache

Denne guiden antar du allerede bruker Apache på webserveren. Derfor brukes Apache
som en revers-proxy mot Gunicorn, som fungerer som limet mellom Python og HTTP.
Hvis du ikke allerede bruker Apache bør du heller vurdere Nginx og uWSGI.

1. Lag en ny bruker. I denne guiden kaller vi den `infoskjerm-vervarsel`.

    ```
    sudo useradd infoskjerm-vervarsel
    ```

2. Følg instruksene ovenfor, og installer applikasjonen i `/srv/infoskjerm-vervarsel`,
   og med en annen bruker enn `infoskjerm-vervarsel`. På den måten kan ikke skriptet
   endre seg selv. Du kan endre eieren i etterkant ved å kjøre:

   ```sh
   sudo chown -R <user>: .
   ```

5. Sørg for at Gunicorn-serveren for infoskjerm-vervarsel starter automatisk ved oppstart:

   1. Kopier `start_server_template.sh` til `start_server.sh` og fyll inn variablene i toppen av skriptet.

   1. Kopier `systemd/infoskjerm-vervarsel.template.service` og lagre som `/etc/systemd/system/infoskjerm-vervarsel.service`.
   2. Fyll inn manglende felter i den fila.
   3. Kjør `sudo systemctl enable infoskjerm-vervarsel.service`

7. Kopier Apache-konfigurasjonen under og plasser den der du ønsker å gjøre
   værvarselet tilgjengelig. For eksempel i en &lt;Location&gt;-blokk.

8. Kjør:

    ```sh
    # If the following fails, you know you have a configuration error (but the server is still up)
    apache2ctl configtest
    # Start actually using the new configuration
    apache2ctl graceful
    ```

10. Sjekk om det funker. Hvis ikke, kan det hende du må endre hvordan SELinux håndterer
    porten du bruker for infoskjerm-vervarsel. Apache får ikke lov til å sende og lytte
    til alle portene i systemet by default. Sjekk loggene først, og hvis
    dette viser seg å være problemet kan du fikse det ved å kjøre:

    ```sh
    sudo semanage port -a -t http_port_t -p tcp <port>
    ```
    
    Da forteller du SELinux at Apache skal ha tilgang til den porten.

12. Ferdig!

## Apache-konfigurasjon

Du bruker basically Apache som en proxy som gjør tilgjengelig innhold fra
Python-serveren.

```apache
# Replace <port> with the port specified in start_server.sh (that is, the port infoskjerm-vervarsel actually runs at)
# Remove the "/" part if this is placed inside a <Location> or <LocationMatch>,
# otherwise write the path where you want to place this instead of /.
ProxyPass "/" "http://localhost:<port>/"
ProxyPassReverse "/" "http://localhost:<port>/"
```
