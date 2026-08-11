# Day 023 Docker Practice & Notes

## Exercise 1: Install Docker Desktop

- Install Docker Desktop on your machine.
- Verify installation by running:

```bash
docker --version
```

## Exercise 2: Run Hello World

Run the Docker hello-world container:

```bash
docker run hello-world
```

- Understand every line of the output.

## Exercise 3: List Images

List local Docker images:

```bash
docker images
```

## Exercise 4: List Containers

List all containers, including stopped ones:

```bash
docker ps -a
```

## Exercise 5: Docker Architecture

Draw this architecture yourself:

```text
Developer
↓
Docker CLI
↓
Docker Engine
↓
Image
↓
Container
```

---

## Common Docker Commands

```bash
docker --version
docker images
docker ps
docker ps -a
docker pull hello-world
docker run hello-world
```

## Docker Command Breakdown

### 1. System Verification

```bash
docker --version
```

- What it does: Displays the currently installed version of Docker on your system.
- Why use it: Quick way to check if Docker is properly installed and accessible from your command line interface (CLI).

### 2. Image Management

```bash
docker images
```

- What it does: Lists all Docker images stored locally on your machine, along with details like repository name, tag, image ID, creation date, and size.
- Why use it: To see what blueprints/templates you have locally available to spin up containers.

```bash
docker pull hello-world
```

- What it does: Downloads the hello-world image from Docker Hub (the public registry) to your local machine without running it immediately.
- Why use it: Pre-downloading images speeds up container deployment when you're ready to run them.

### 3. Running Containers

```bash
docker run hello-world
```

- What it does: Creates and starts a new container based on the hello-world image.
- Note: If the image isn't available locally, Docker will automatically run `docker pull hello-world` first, then start the container.
- The hello-world container prints a greeting message explaining how Docker works, then immediately stops.

### 4. Container Inspection

```bash
docker ps
```

- What it does: Lists only currently active/running containers.
- Why use it: To check status, assigned ports, container IDs, and names of actively running services.

```bash
docker ps -a
```

- What it does: Lists all containers on your system—both currently running and stopped/exited containers.
- Why use it: Since many containers (like hello-world) complete their task and exit immediately, `docker ps` won't show them. `docker ps -a` lets you see past runs and exited containers.
