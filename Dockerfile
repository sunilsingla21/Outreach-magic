FROM node:20.9.0-slim as frontend-build
WORKDIR /usr/src

COPY . .

RUN npm install
RUN npm run build

FROM python:3.10
WORKDIR /usr/src

COPY ./requirements.txt ./.env ./
RUN pip install -r ./requirements.txt

COPY --from=frontend-build /usr/src/app ./app
COPY --from=frontend-build /usr/src/app/static/dist ./app/static
COPY --from=frontend-build /usr/src/app/static/css/tailwind-output.css ./app/static/css

ENV FLASK_ENV production

EXPOSE 5000
CMD ["gunicorn", "-b", ":5000", "app.wsgi:wsgi_app"]
