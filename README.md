# RaccoonCatcher

A Pygame game where you monitor security cameras to find raccoons in your yard, then sneak up and photograph them before they bolt.

## Prerequisites

- Python 3.11
- pip

## Setup

1. Clone the repository and enter the project directory.

2. Install the dependency:

```bash
python3.11 -m pip install pygame==2.5.2
```

Or use the requirements file:

```bash
python3.11 -m pip install -r requirements.txt
```

## Running the game

```bash
python3.11 main.py
```

The game opens a 1280×720 window at 60 FPS.

## How to play

**Camera view** — You start at a bank of four CCTV feeds showing your yard zones (Front Yard, Back Yard, Side Gate, Garden Shed). Raccoons wander between zones in real time.

- Click the **GO** button on a camera feed to head to that zone. You can only go to a zone that currently has a raccoon.
- The longer you linger at the cameras, the more likely the raccoon will flee before you arrive.

**Yard view** — You arrive in the zone with your camera. A crosshair follows your mouse.

- **Left-click** to take a photo.
- Center the inner reticle over the raccoon to score points. Missing scores nothing.
- You have 6 seconds before the raccoon escapes on its own.

**Scoring** — Each raccoon size is worth a different number of points:

| Size   | Points |
|--------|--------|
| Small  | 10     |
| Medium | 25     |
| Large  | 50     |
| XL     | 100    |

**Levels** — There are three levels, each with a higher score target and more raccoons that are faster and warier. Hit the score target before the 3-minute timer runs out to advance. Fail and it's game over.

| Level | Score target | Raccoons |
|-------|-------------|----------|
| 1     | 100         | 3        |
| 2     | 250         | 4        |
| 3     | 500         | 5        |
