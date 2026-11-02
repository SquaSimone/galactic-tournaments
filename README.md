# \# Galactic Tournaments

# 

# A full stack web app to archive and analyze the seasons of the Galactic tournament: 36 teams, 7 competitions (Galactic League, Galactic Cup, Kings League, Galactic Champions Cup, Intergalactic SuperCup, Cup of 8/10 and a Ranking).

# 

# I built it as a personal project to practice a complete stack, from data extraction to API to UI, with everything running in containers.

# 

# \## What it does

# 

# \- Imports a season from an Excel workbook and extracts every match with a custom parser

# \- Stores the matches in PostgreSQL, tagged by season and competition

# \- Exposes the data through a REST API built with FastAPI

# \- Shows it in a React interface

# \- Exports and imports the archive as JSON, so a database can be backed up and restored

# 

# The archive currently holds 12 seasons and more than 7,000 matches.

# 

# \## Tech stack

# 

# | Layer | Tools |

# |---|---|

# | Backend | Python 3.12, FastAPI, pandas, SQLAlchemy |

# | Frontend | React 18, TypeScript, Vite, Tailwind CSS |

# | Database | PostgreSQL 16 |

# | Infrastructure | Docker Compose |

# 

# \## Quick start

# 

# You need Docker and Docker Compose.

# 

# ```bash

# git clone <this-repo-url>

# cd galactic-tournaments

# 

# \# the database volume is declared as external, so create it once

# docker volume create prova1\_pgdata

# 

# \# create your local environment file from the template

# cp .env.example .env          # on PowerShell: Copy-Item .env.example .env

# 

# docker compose up --build

# ```

# 

# Then open:

# 

# \- Frontend: http://localhost:8083

# \- Backend API: http://localhost:3004/api

# \- PostgreSQL: localhost:5435 (user `galactic`, database `galactic\_tournaments`)

# 

# The password in `.env.example` is a placeholder. Change it if you expose the database outside your machine.

# 

# \## Try it with sample data

# 

# The folder `sample-data/` contains a JSON file with the matches of one season (`sample-season-1.json`).

# Load it with the import function of the app to see the interface with real content, without needing the original Excel files.

# 

# \## Project structure

# 

# ```

# backend/        FastAPI app and the extraction and ranking logic (estrattore.py)

# db/             Database init script and migrations

# src/            React frontend

# public/         Static assets

# sample-data/    Example season in JSON format

# ```

# 

# \## How it works

# 

# 1\. In the "Import season" tab you upload a season workbook (`Stagione X.xlsm`).

# 2\. The extractor reads all the matches and saves them in the database with `season = X`.

# 3\. The API serves matches and competitions to the frontend.

# 

# \## Roadmap

# 

# \- Tabs for matches, standings, rankings and team history

# \- Automatic tests for the extraction logic

# \- Simple statistics per team and per competition

# 

# \## Screenshots

# 

# (add 2 or 3 screenshots here, for example `!\[Home](docs/home.png)`)

