# WhereTo
Website for indecisive explorers in London!

Development in CICD  -> deployed in Vercel
                     -> https://where2.vercel.app

Backend:    Python-Flask framework

Frontend:   Bootstrap-JS

Database:   PostgreSQL  -> Imperial College DocSoc (vnp23)
                        -> Manual data entry

APIs:       TFL    -> cached calls
            Geofy  -> convert London postcode to geographic co-ordinates


New feature!
Endpoint -> /change
          -> use any of parameters default/bgcolor/fontcolor
          -> bgcolor and fontcolor accepts colours in both plain text and hex values and changes the website settings
          -> whenever default is mentioned, the website goes back to the default colour scheme.
