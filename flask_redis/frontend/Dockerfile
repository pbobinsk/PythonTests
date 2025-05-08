# Użyj oficjalnego obrazu Nginx
FROM nginx:alpine

# Usuń domyślną konfigurację Nginx (opcjonalne, ale dobra praktyka, jeśli nie używasz default.conf)
# RUN rm /etc/nginx/conf.d/default.conf

# Skopiuj pliki HTML i JS do katalogu serwowanego przez Nginx
# Kontekstem budowania jest katalog ./frontend, więc ścieżki są relatywne do niego.
COPY index.html /usr/share/nginx/html/
COPY app.js /usr/share/nginx/html/

# Nginx domyślnie nasłuchuje na porcie 80 i serwuje index.html z /usr/share/nginx/html
EXPOSE 80

# Uruchom Nginx w trybie foreground
CMD ["nginx", "-g", "daemon off;"]