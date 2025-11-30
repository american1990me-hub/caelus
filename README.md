# Caelus

This is the Caelus v1 core.

## Getting Started

This project is configured within a Firebase Studio environment, utilizing a `.idx/dev.nix` file for a reproducible and consistent development experience.

**What is `dev.nix`?**
The `.idx/dev.nix` file declaratively defines all the dependencies, tools, and services needed for this project. This ensures that everyone working on "Caelus" has the exact same development environment, preventing "it works on my machine" issues and simplifying onboarding.

### Customizing Your Environment

You can customize your development environment by modifying the `.idx/dev.nix` file. This file allows you to:

*   **Install packages:** Add necessary tools and libraries (e.g., `nodejs`, `python`, `go`).
*   **Set environment variables:** Configure project-specific environment variables.
*   **Install VS Code extensions:** Ensure everyone uses the same recommended IDE extensions.
*   **Define workspace lifecycle hooks:** Run commands `onCreate` (when the workspace is first created) or `onStart` (every time the workspace is restarted).
*   **Configure web previews:** Set up local development servers that are accessible via the Firebase Studio web preview.

**Important:** After making changes to `.idx/dev.nix`, you will need to reload your environment for the changes to take effect.

Learn more about customizing your Firebase Studio environment at [https://developers.google.com/](https://developers.google.com/).