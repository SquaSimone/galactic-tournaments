# \# Galactic Tournaments

# 

# A full stack web app to generate, archive and analyze the seasons of the Galactic tournament: 36 teams competing across several formats (a league phase, knockout cups, a group-stage Kings League and a seeded Champions Cup).

# 

# I built it as a personal project to practice a complete stack end to end, from a tournament generation engine to the API to the UI, with everything running in containers.

# 

# \## What it does

# 

# The app is organized in tabs:

# 

# \- \*\*Generate season\*\* – draws a full new season. Teams are seeded into 4 pots of 9 based on their ranking, the league calendar is built from precalculated templates that avoid repeating a schedule used in the last 5 seasons, and knockout brackets are generated and filled round by round.

# \- \*\*Import season\*\* – reads a season from an Excel workbook, extracts every match with a custom parser and stores it in the database.

# \- \*\*Seasonal stats\*\* – standings and statistics for a single season, per competition.

# \- \*\*Cumulative stats\*\* – aggregated statistics across all seasons.

# \- \*\*Competitions\*\* – history and results browser across competitions.

# \- \*\*Hall of champions\*\* – the roll of winners season by season.

# 

# When a result is edited, the knockout brackets that depend on it are propagated automatically. The whole archive can be exported and re-imported as JSON. It currently holds 12 seasons and more than 7,000 matches.

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

# git clone https://github.com/SquaSimone/galactic-tournaments.git

# cd galactic-tournaments

# 

# \# the database volume is declared as external, so create it once

# docker volume create prova1\_pgdata

# 

# \# create your local environment file from the template

# \# PowerShell:

# Copy-Item .env.example .env

# \# bash:

# \# cp .env.example .env

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

# The folder `sample-data/` contains a JSON file with one full season (`sample-season-1.json`).

# Load it from the import function of the app to see the interface populated with real content, without needing the original Excel files.

# 

# \## Project structure

# 

# ```

# backend/        FastAPI app

# &#x20; src/main.py        API endpoints, standings and bracket propagation

# &#x20; src/estrattore.py  Excel parser and extraction logic

# &#x20; src/sorteggio.py   season draw: pots, templates, league phase

# db/             Database init script and migrations

# src/            React frontend (one file per tab under src/pages/)

# public/         Static assets

# sample-data/    Example season in JSON format

# ```

# 

# \## Notes

# 

# This started as a hobby project to manage a tournament I follow, and it grew into a way to practice building a real system: a non-trivial domain engine, a REST API, a relational schema with migrations, and a containerized setup that runs with a single command.

